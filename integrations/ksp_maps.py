"""Portable, bounded KSP height maps and SCANsat CSV conversion (no dependencies)."""
import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from integrations.ksp_navigation import coordinate, finite, to_local, plan_ksp_mission

SCHEMA = 'ksp-terrain-v1'
SOURCES = ('KSP1-kRPC-bedrock', 'SCANsat-CSV', 'synthetic-ksp-demo')


def validate_terrain(value):
    if not isinstance(value, dict):
        raise ValueError('Mapa KSP no válido.')
    w, h = value.get('width'), value.get('height')
    if any(isinstance(n, bool) or not isinstance(n, int) or not 3 <= n <= 41 for n in (w, h)):
        raise ValueError('La malla debe tener entre 3 y 41 muestras por lado.')
    cell = finite(value.get('cellMeters'), 'Celda')
    radius = finite(value.get('bodyRadius'), 'Radio')
    if not 5 <= cell <= 10000 or not 100 <= radius <= 1e9 or math.hypot(w-1,h-1)*cell/(2*radius) > .08:
        raise ValueError('Resolución, radio o extensión local no válidos.')
    lat, lon = coordinate(value.get('center'))
    body, source = value.get('body'), value.get('sourceType')
    if not isinstance(body,str) or not body.strip() or len(body)>80 or source not in SOURCES:
        raise ValueError('Cuerpo o procedencia KSP no válidos.')
    if value.get('projection') != 'local-azimuthal-equidistant':
        raise ValueError('La proyección del mapa no es compatible.')
    elevations, water = value.get('elevations'), value.get('water')
    if not isinstance(elevations,list) or not isinstance(water,list) or len(elevations)!=w*h or len(water)!=w*h:
        raise ValueError('Las alturas y la máscara de agua no coinciden con la malla.')
    for v in elevations:
        if v is not None and abs(finite(v,'Altura'))>1e8:
            raise ValueError('Altura fuera de rango.')
    if not any(v is not None for v in elevations) or any(not isinstance(v,bool) for v in water):
        raise ValueError('Mapa sin alturas o con máscara de agua no válida.')
    terrain=dict(width=w,height=h,cellMeters=float(cell),bodyRadius=float(radius),body=body,
                 center=dict(lat=float(lat),lon=float(lon)),elevations=[None if v is None else float(v) for v in elevations],water=water,
                 projection='local-azimuthal-equidistant',sourceType=source)
    # Content identity is recomputed; an imported ID or a vehicle/session is never trusted.
    digest=hashlib.sha256(json.dumps(terrain,sort_keys=True,allow_nan=False).encode()).hexdigest()
    terrain.update(id='archive-'+digest[:24],vesselId='archive',sampledAt=None)
    return terrain


def archive(value):
    return dict(schema=SCHEMA,exportedAt=datetime.now(timezone.utc).isoformat(),terrain=validate_terrain(value))


def read_archive(value):
    if not isinstance(value,dict) or value.get('schema')!=SCHEMA:
        raise ValueError('Selecciona un mapa ksp-terrain-v1; una imagen PNG no contiene alturas.')
    return validate_terrain(value.get('terrain'))


def plan_archive(payload):
    if not isinstance(payload,dict):
        raise ValueError('Solicitud no válida.')
    terrain=read_archive(payload.get('map'))
    mission=plan_ksp_mission(terrain,payload.get('mission'))
    mission['planningContext']['mapMode']='imported-height-map'
    mission['notice']='Ruta sobre un mapa importado; su procedencia es declarada, no certificada. No detecta obstáculos pequeños ni controla KSP.'
    return mission


def scansat_region(stream, *, body, radius, latitude, longitude, size=33, cell=250, ocean=False):
    """Stream SCANsat Row,Column,Lat,Long,Height; retain nearest sample per local cell.

    Missing/scanned-out cells remain null. No height interpolation or invented detail.
    """
    if isinstance(size,bool) or not isinstance(size,int) or not 3<=size<=41:
        raise ValueError("Tamaño de malla no válido.")
    template=dict(width=size,height=size,cellMeters=cell,bodyRadius=radius,body=body,
                  center=dict(lat=latitude,lon=longitude),projection='local-azimuthal-equidistant',
                  sourceType='SCANsat-CSV',elevations=[0.]*(size*size),water=[False]*(size*size))
    terrain=validate_terrain(template)
    terrain['elevations']=[None]*(size*size)
    distances=[math.inf]*(size*size)
    reader=csv.DictReader(stream)
    if reader.fieldnames!=['Row','Column','Lat','Long','Height']:
        raise ValueError('Se requiere el CSV SCANsat: Row,Column,Lat,Long,Height (decimales con punto).')
    count=invalid=0
    for row in reader:
        count+=1
        try:
            if None in row:raise ValueError('Columns')
            lat,lon,z=(float(row[k]) for k in ('Lat','Long','Height'))
            coordinate(dict(lat=lat,lon=lon));finite(z,'Altura')
            if abs(z)>1e8:raise ValueError('Altura')
            try:x,y=to_local(terrain['center'],lat,lon,radius)
            except ValueError:continue
            gx=x/cell+(size-1)/2;gy=y/cell+(size-1)/2
            ix,iy=math.floor(gx+.5),math.floor(gy+.5)
            if not 0<=ix<size or not 0<=iy<size:continue
            d=math.hypot(gx-ix,gy-iy)
            i=iy*size+ix
            if d<distances[i]:
                distances[i]=d;terrain['elevations'][i]=z;terrain['water'][i]=bool(ocean and z<0)
        except (ValueError,TypeError,KeyError):invalid+=1
    if invalid:
        raise ValueError(f'CSV con {invalid} filas no válidas. Revisa separador, decimales y alturas; no se importó.')
    result=archive(terrain)
    result['conversion']=dict(rowsRead=count,cellsWithData=sum(v is not None for v in terrain['elevations']),
                              totalCells=size*size,method='nearest-sample-per-cell-no-interpolation',
                              oceanDeclared=bool(ocean),notice='La resolución del CSV limita el detalle. Las celdas sin muestras quedan bloqueadas.')
    return result
