"""Surface navigation in the active KSP body's own coordinates, read-only."""
import math
from datetime import datetime, timezone
from mars.planner import find_path, route_metrics
from integrations.ksp_environment import training_environment


def finite(value, name):
    try:
        valid = not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)
    except OverflowError:
        valid = False
    if not valid:
        raise ValueError(f'{name}: se requiere un número finito.')
    return value


def coordinate(point):
    if not isinstance(point, dict):
        raise ValueError('Coordenada no válida.')
    lat, lon = finite(point.get('lat'), 'Latitud'), finite(point.get('lon'), 'Longitud')
    if not -90 <= lat <= 90 or not -180 <= lon <= 180:
        raise ValueError('Coordenada fuera de rango.')
    return lat, lon


def to_local(center, lat, lon, radius):
    """Azimuthal equidistant projection; X east, Y south, in meters."""
    lat0, lon0, lat, lon = map(math.radians, [center['lat'], center['lon'], lat, lon])
    dl = (lon-lon0+math.pi) % (2*math.pi)-math.pi
    cosc = max(-1., min(1., math.sin(lat0)*math.sin(lat)+math.cos(lat0)*math.cos(lat)*math.cos(dl)))
    c = math.acos(cosc)
    if c < 1e-10:
        return 0., 0.
    if c > math.pi/2:
        raise ValueError('La posición queda fuera de la proyección local.')
    scale = radius*c/math.sin(c)
    return (scale*math.cos(lat)*math.sin(dl),
            -scale*(math.cos(lat0)*math.sin(lat)-math.sin(lat0)*math.cos(lat)*math.cos(dl)))


def to_geo(center, x, y, radius):
    lat0, lon0 = math.radians(center['lat']), math.radians(center['lon'])
    rho = math.hypot(x, y)
    if rho < 1e-10:
        return dict(lat=center['lat'], lon=center['lon'])
    c, north = rho/radius, -y
    lat = math.asin(max(-1., min(1., math.cos(c)*math.sin(lat0)+north*math.sin(c)*math.cos(lat0)/rho)))
    lon = lon0+math.atan2(x*math.sin(c), rho*math.cos(lat0)*math.cos(c)-north*math.sin(lat0)*math.sin(c))
    return dict(lat=math.degrees(lat), lon=(math.degrees(lon)+180) % 360-180)


def grid_coordinate(terrain, point):
    lat, lon = coordinate(point)
    x, y = to_local(terrain['center'], lat, lon, terrain['bodyRadius'])
    gx, gy = x/terrain['cellMeters']+(terrain['width']-1)/2, y/terrain['cellMeters']+(terrain['height']-1)/2
    if not -1e-6 <= gx <= terrain['width']-1+1e-6 or not -1e-6 <= gy <= terrain['height']-1+1e-6:
        raise ValueError('El punto está fuera del terreno KSP muestreado. Carga una región que lo incluya.')
    return math.floor(gx+.5), math.floor(gy+.5)


def grid_to_geo(terrain, x, y):
    return to_geo(terrain['center'], (x-(terrain['width']-1)/2)*terrain['cellMeters'],
                  (y-(terrain['height']-1)/2)*terrain['cellMeters'], terrain['bodyRadius'])


def terrain_request(sample, payload, terrain_id):
    if not isinstance(payload, dict):
        raise ValueError('Solicitud no válida.')
    size = payload.get('size', 33)
    spacing = finite(payload.get('cellMeters', 25), 'Tamaño de celda')
    if isinstance(size, bool) or not isinstance(size,int) or size not in (17, 33, 41) or not 5 <= spacing <= 250:
        raise ValueError('Usa 17, 33 o 41 celdas por lado y un tamaño de celda de 5–250 m.')
    if math.hypot((size-1)*spacing/2, (size-1)*spacing/2)/sample['bodyRadius'] > .08:
        raise ValueError('La región es demasiado grande para el radio de este cuerpo.')
    return dict(id=terrain_id, width=size, height=size, cellMeters=spacing,
                center=dict(lat=sample['latitude'], lon=(sample['longitude']+180) % 360-180),
                body=sample['body'], bodyRadius=sample['bodyRadius'], vesselId=sample['vesselId'],
                projection='local-azimuthal-equidistant', sourceType='KSP1-kRPC-bedrock',
                elevations=[None]*(size*size), water=[False]*(size*size), sampledAt=None)


def plan_ksp_mission(terrain, payload):
    if not isinstance(payload, dict) or payload.get('terrainId') != terrain['id'] or payload.get('body') != terrain['body']:
        raise ValueError('La región o el cuerpo no coincide. Vuelve a cargar el mapa KSP.')
    reason=payload.get('replanReason','initial')
    if reason not in ('initial','deviation','manual','weather'):
        raise ValueError('Motivo de planificación KSP no válido.')
    entries = payload.get('stops')
    if not isinstance(entries, list) or not 2 <= len(entries) <= 20:
        raise ValueError('Selecciona entre 2 y 20 paradas KSP.')
    limit, speed = finite(payload.get('maxSlopeDegrees', 15), 'Pendiente'), finite(payload.get('speedMS', 2), 'Velocidad')
    if not 1 <= limit <= 40 or not .1 <= speed <= 50:
        raise ValueError('La pendiente debe ser 1–40° y la velocidad estimada 0.1–50 m/s.')
    avoid_water = payload.get('avoidWater', True)
    if not isinstance(avoid_water, bool):
        raise ValueError('La opción de agua debe ser booleana.')
    blocked = {(i % terrain['width'], i // terrain['width']) for i, water in enumerate(terrain['water']) if water and avoid_water}
    environment, weather_blocks = training_environment(terrain, payload.get('weather','clear'))
    blocked.update(weather_blocks)
    stops, names = [], set()
    for entry in entries:
        lat, lon = coordinate(entry)
        name = entry.get('name')
        if not isinstance(name, str) or not name.strip() or len(name) > 60 or name.strip() in names:
            raise ValueError('Las paradas necesitan nombres únicos de 1–60 caracteres.')
        name = name.strip(); names.add(name)
        x, y = grid_coordinate(terrain, entry)
        stops.append(dict(name=name, lat=lat, lon=lon, grid=[x, y], type='ksp-waypoint'))
    path, indices = [], [0]
    for a, b in zip(stops, stops[1:]):
        segment = find_path(terrain, a['grid'], b['grid'], limit, blocked)
        if segment is None:
            raise ValueError(f"Sin paso entre {a['name']} y {b['name']}: revisa pendiente, agua, cobertura y restricciones simuladas.")
        # Preserve physical endpoints inside coarse cells; A* still validates cells.
        def exact(stop):
            east,south=to_local(terrain['center'],stop['lat'],stop['lon'],terrain['bodyRadius'])
            return (east/terrain['cellMeters']+(terrain['width']-1)/2,
                    south/terrain['cellMeters']+(terrain['height']-1)/2)
        first,last=exact(a),exact(b)
        if len(segment)==1:
            segment=[first,last] if math.dist(first,last)>1e-8 else [first]
        else:
            if math.dist(first,segment[0])>1e-8:segment.insert(0,first)
            if math.dist(last,segment[-1])>1e-8:segment.append(last)
        path.extend(segment if not path else segment[1:]); indices.append(len(path)-1)
    for stop,index in zip(stops,indices):stop['pathIndex']=index
    metrics = route_metrics(terrain, [(math.floor(x+.5),math.floor(y+.5)) for x,y in path])
    metrics['distance']=sum(math.dist(a,b)*terrain['cellMeters'] for a,b in zip(path,path[1:]))
    metrics['durationMinutes'] = math.ceil(metrics['distance']/(speed*environment['speedFactor'])/60)
    return dict(name=f"Ruta de superficie · {terrain['body']}", schema='ksp-surface-mission-v1',
                context=dict(kind='ksp-surface', body=terrain['body'], bodyRadius=terrain['bodyRadius'], terrainId=terrain['id']),
                sourceType=terrain['sourceType'], planningContext=dict(reason=reason,weather=environment['scenario']), environment=environment, createdAt=datetime.now(timezone.utc).isoformat(),
                stops=stops, stopPathIndices=indices, gridPath=path,
                route=[grid_to_geo(terrain, x, y) for x, y in path], metrics=metrics,
                maxSlopeDegrees=limit, speedMS=speed, avoidWater=avoid_water,
                assumptions=dict(speedMS=speed,effectiveSpeedMS=speed*environment['speedFactor'],terrainCellMeters=terrain['cellMeters'],obstaclesBelowResolution=False,endpointDetail='Coordenadas exactas; relieve dentro de cada celda no resuelto.'),
                readOnly=True, notice='Guía sobre alturas muestreadas. No detecta rocas pequeñas ni controla el vehículo.')


def demo_terrain():
    terrain = terrain_request(dict(latitude=0.,longitude=0.,bodyRadius=320000.,body='Escenario KSP · DEMO',vesselId='demo'), {}, 'synthetic-demo-v1')
    terrain['sourceType'] = 'synthetic-ksp-demo'
    terrain['elevations'] = [35+10*math.sin(x/8)*math.cos(y/9) for y in range(33) for x in range(33)]
    terrain['sampledAt'] = datetime.now(timezone.utc).isoformat()
    return terrain
