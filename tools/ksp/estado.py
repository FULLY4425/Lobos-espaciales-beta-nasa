"""Instantánea de solo lectura del vehículo activo de KSP 1 vía kRPC.

Uso: .venv\\Scripts\\python.exe tools/ksp/estado.py
Solo lee propiedades: no cambia mandos, SAS, etapas ni tiempo.
"""
from _conexion import conectar

conn = conectar('Agente · estado (solo lectura)')
sc = conn.space_center
v = sc.active_vessel
body = v.orbit.body
surface = v.flight(v.surface_reference_frame)  # rumbo/cabeceo/alabeo como la navball
local = v.flight(body.reference_frame)         # altitud, velocidad de superficie, vertical
o, c = v.orbit, v.control

print(f'{v.name} · {body.name} · {v.situation.name} · etapa {c.current_stage} · warp {sc.warp_rate:g}x')
print(f'alt {local.mean_altitude:.0f} m (sobre terreno {local.surface_altitude:.0f} m)  '
      f'vel sup {local.speed:.1f} m/s  vertical {local.vertical_speed:.1f} m/s  vel orbital {o.speed:.1f} m/s')
print(f'rumbo {surface.heading:.1f}°  cabeceo {surface.pitch:.1f}°  alabeo {surface.roll:.1f}°  '
      f'ataque {local.angle_of_attack:.1f}°')
print(f'Ap {o.apoapsis_altitude/1000:.1f} km (en {o.time_to_apoapsis:.0f} s)  '
      f'Pe {o.periapsis_altitude/1000:.1f} km (en {o.time_to_periapsis:.0f} s)')
print(f'masa {v.mass:.0f} kg  empuje {v.thrust/1000:.1f}/{v.available_thrust/1000:.1f} kN  '
      f'acelerador {c.throttle:.2f}  SAS {c.sas} ({c.sas_mode.name})  frenos {c.brakes}  tren {c.gear}')
for name in ('LiquidFuel', 'Oxidizer', 'MonoPropellant', 'ElectricCharge'):
    if v.resources.has_resource(name):
        print(f'  {name}: {v.resources.amount(name):.1f}/{v.resources.max(name):.1f}')
for e in v.parts.engines:
    print(f'  motor {e.part.title} · etapa {e.part.stage} · activo {e.active} · '
          f'{e.thrust/1000:.1f}/{e.available_thrust/1000:.1f} kN · combustible {e.has_fuel}')
hot = sorted(((max(p.temperature / p.max_temperature, p.skin_temperature / p.max_skin_temperature), p.title)
              for p in v.parts.all), reverse=True)[:3]
print('  calor máx: ' + ', '.join(f'{t} {r:.0%}' for r, t in hot))
conn.close()
