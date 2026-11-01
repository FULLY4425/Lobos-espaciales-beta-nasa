"""Monitor de solo lectura que termina cuando hace falta actuar.

Ejemplos (desde la raíz del repositorio):
  .venv\\Scripts\\python.exe tools/ksp/monitor.py --hasta-ap 80000
  .venv\\Scripts\\python.exe tools/ksp/monitor.py --hasta-pe 70000 --intervalo 0.5
  .venv\\Scripts\\python.exe tools/ksp/monitor.py --min-alt 30000 --max-calor 0.8

Sale con código 0 si se cumple una condición y 2 si se agota --segundos.
Solo lee propiedades: no cambia mandos, SAS, etapas ni tiempo.
"""
import argparse
import sys
import time

from _conexion import conectar

p = argparse.ArgumentParser()
p.add_argument('--segundos', type=float, default=120)
p.add_argument('--intervalo', type=float, default=1)
p.add_argument('--hasta-ap', type=float, help='apoapsis objetivo en metros')
p.add_argument('--hasta-pe', type=float, help='periapsis objetivo en metros')
p.add_argument('--min-alt', type=float, help='avisa al bajar de esta altitud (m)')
p.add_argument('--max-calor', type=float, help='fracción de temperatura máxima de cualquier pieza')
p.add_argument('--antes-ap', type=float, help='avisa cuando falten estos segundos a la apoapsis')
a = p.parse_args()

conn = conectar('Agente · monitor (solo lectura)')
v = conn.space_center.active_vessel
surface, local = v.flight(v.surface_reference_frame), v.flight(v.orbit.body.reference_frame)


def heat():
    return max(max(p.temperature / p.max_temperature, p.skin_temperature / p.max_skin_temperature)
               for p in v.parts.all)


t0 = time.time()
while time.time() - t0 < a.segundos:
    o, alt = v.orbit, local.mean_altitude
    h = heat() if a.max_calor else 0
    print(f'{time.time()-t0:5.0f}s alt {alt/1000:6.1f} km  vs {local.vertical_speed:6.0f}  '
          f'vorb {o.speed:5.0f}  Ap {o.apoapsis_altitude/1000:7.1f}  Pe {o.periapsis_altitude/1000:7.1f}  '
          f't_Ap {o.time_to_apoapsis:6.0f}s  cabeceo {surface.pitch:5.1f}  empuje {v.thrust/1000:4.0f} kN'
          + (f'  calor {h:.2f}' if a.max_calor else ''), flush=True)
    reasons = [r for r, hit in (
        ('apoapsis', a.hasta_ap is not None and o.apoapsis_altitude >= a.hasta_ap),
        ('periapsis', a.hasta_pe is not None and o.periapsis_altitude >= a.hasta_pe),
        ('altitud', a.min_alt is not None and alt < a.min_alt),
        ('calor', a.max_calor is not None and h > a.max_calor),
        ('cerca de apoapsis', a.antes_ap is not None and o.time_to_apoapsis <= a.antes_ap),
    ) if hit]
    if reasons:
        print('ACTUAR: ' + ', '.join(reasons))
        conn.close()
        sys.exit(0)
    time.sleep(a.intervalo)
print('Tiempo agotado sin cumplir condiciones.')
conn.close()
sys.exit(2)
