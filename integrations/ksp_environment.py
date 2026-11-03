"""Explicit training weather; never inferred from KSP telemetry."""
import math

def training_environment(terrain, scenario='clear', wind_direction=90):
    if isinstance(wind_direction,bool) or not isinstance(wind_direction,(int,float)) or not math.isfinite(wind_direction) or not 0<=wind_direction<360:
        raise ValueError('La dirección del viento debe estar entre 0 y menos de 360 grados.')
    if not isinstance(scenario,str) or scenario not in ('clear','wind','dust','storm'):
        raise ValueError('Escenario de entrenamiento KSP no válido.')
    zones=[]
    if scenario=='storm':
        zones=[dict(x=(terrain['width']-1)*.65,y=(terrain['height']-1)*.48,
                    radiusCells=max(1,(min(terrain['width'],terrain['height'])-1)*.1))]
    blocked={(x,y) for y in range(terrain['height']) for x in range(terrain['width'])
             if any(math.hypot(x-z['x'],y-z['y'])<=z['radiusCells'] for z in zones)}
    speed,gust,visibility={'clear':(0,0,20000),'wind':(12,20,5000),'dust':(8,14,1500),'storm':(25,40,200)}[scenario]
    return dict(wind=dict(speedMS=speed,gustMS=gust,fromDegrees=wind_direction),visibilityMeters=visibility,scenario=scenario,sourceType='synthetic-training',zones=zones,
                speedFactor={'clear':1,'wind':.85,'dust':.75,'storm':.5}[scenario],
                notice='Escenario hipotético de entrenamiento; no es clima observado ni modifica KSP.'),blocked
