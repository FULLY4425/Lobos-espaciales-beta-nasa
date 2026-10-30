"""Terrain navigation and educational mission estimates (standard library only)."""
import math
import heapq
from datetime import datetime, timezone


def slope_at(t, x, y):
    w, h, m = t['width'], t['height'], t['cellMeters']
    def at(a, b):
        return t['elevations'][max(0, min(h-1, b))*w+max(0, min(w-1, a))]
    v = [at(x, y), at(x-1, y), at(x+1, y), at(x, y-1), at(x, y+1)]
    if None in v:
        return math.inf
    return math.degrees(math.atan(math.hypot((v[2]-v[1])/(2*m if 0<x<w-1 else m), (v[4]-v[3])/(2*m if 0<y<h-1 else m))))


def grid_point(t, p):
    return (math.floor((p['lon']-t['west'])/t['degreeStep']+.5), math.floor((t['north']-p['lat'])/t['degreeStep']+.5))


def find_path(t, start, end, max_slope=20):
    w, h, m = t['width'], t['height'], t['cellMeters']
    start, end = tuple(start), tuple(end)
    def inside(p):
        return 0<=p[0]<w and 0<=p[1]<h
    def elevation(p):
        return t['elevations'][p[1]*w+p[0]]
    def passes(p):
        return inside(p) and elevation(p) is not None and slope_at(t, *p)<=max_slope
    if not passes(start) or not passes(end):
        return None
    scores, parents, closed = {start: 0}, {}, set()
    queue = [(0, start)]
    while queue:
        _, current = heapq.heappop(queue)
        if current in closed:
            continue
        if current == end:
            path = [current]
            while current in parents:
                current = parents[current]
                path.append(current)
            return path[::-1]
        closed.add(current)
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            nxt = current[0]+dx, current[1]+dy
            if nxt in closed or not passes(nxt):
                continue
            if dx and dy and (not passes((nxt[0], current[1])) or not passes((current[0], nxt[1]))):
                continue
            distance = math.hypot(dx, dy)*m
            grade = abs(elevation(nxt)-elevation(current))/distance
            if math.degrees(math.atan(grade))>max_slope:
                continue
            cost = scores[current]+distance*(1+3*grade)
            if cost < scores.get(nxt, math.inf):
                scores[nxt], parents[nxt] = cost, current
                heuristic = math.hypot(nxt[0]-end[0], nxt[1]-end[1])*m
                heapq.heappush(queue, (cost+heuristic, nxt))
    return None


def route_metrics(t, path):
    distance = ascent = 0
    for (x,y),(a,b) in zip(path[1:],path):
        distance += math.hypot(x-a,y-b)*t['cellMeters']
        ascent += max(0,t['elevations'][y*t['width']+x]-t['elevations'][b*t['width']+a])
    return dict(distance=distance, ascent=ascent)


def plan_mission(t, targets, payload):
    names, limit = payload.get('stops'), payload.get('maxSlopeDegrees',20)
    if not isinstance(names,list) or not 2<=len(names)<=20 or any(not isinstance(n,str) for n in names):
        raise ValueError('Selecciona entre 2 y 20 objetivos.')
    if isinstance(limit,bool) or not isinstance(limit,(int,float)) or not math.isfinite(limit) or not 5<=limit<=40:
        raise ValueError('La pendiente debe estar entre 5 y 40 grados.')
    lookup = {p['name']:p for p in targets}
    if any(n not in lookup for n in names) or len(set(names))!=len(names):
        raise ValueError('Objetivos desconocidos o repetidos.')
    stops, path = [lookup[n] for n in names], []
    for a,b in zip(stops,stops[1:]):
        segment = find_path(t,grid_point(t,a),grid_point(t,b),limit)
        if segment is None:
            raise ValueError(f"No se encontró un paso entre {a['name']} y {b['name']} con este límite y resolución.")
        path.extend(segment if not path else segment[1:])
    metrics = route_metrics(t,path)
    metrics['durationMinutes'] = math.ceil(metrics['distance']/2000*60+(len(stops)-1)*10)
    return dict(name='Glen Torridon — Lobos Espaciales', educationalSimulation=True,
                createdAt=datetime.now(timezone.utc).isoformat(), maxSlopeDegrees=limit,
                stops=stops, metrics=metrics, gridPath=path, returnIncluded=False,
                assumptions=dict(speedKmH=2,stopMinutes=10,terrainCellMeters=t['cellMeters']),
                route=[dict(lon=t['west']+x*t['degreeStep'],lat=t['north']-y*t['degreeStep']) for x,y in path],
                sources=['https://doi.org/10.17189/dw9v-xe39',t['source']])
