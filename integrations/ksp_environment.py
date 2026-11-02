"""Explicit training weather; never inferred from KSP telemetry."""
import math

def training_environment(terrain, scenario='clear'):
    if not isinstance(scenario,str) or scenario not in ('clear','dust','storm'):
        raise ValueError('Escenario de entrenamiento KSP no válido.')
    zones=[]
    if scenario=='storm':
        zones=[dict(x=(terrain['width']-1)*.65,y=(terrain['height']-1)*.48,
                    radiusCells=max(1,(min(terrain['width'],terrain['height'])-1)*.1))]
    blocked={(x,y) for y in range(terrain['height']) for x in range(terrain['width'])
             if any(math.hypot(x-z['x'],y-z['y'])<=z['radiusCells'] for z in zones)}
    return dict(scenario=scenario,sourceType='synthetic-training',zones=zones,
                speedFactor={'clear':1,'dust':.75,'storm':.5}[scenario],
                notice='Escenario hipotético de entrenamiento; no es clima observado ni modifica KSP.'),blocked
