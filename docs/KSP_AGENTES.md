# Guía para agentes: conectar y manejar KSP 1

Notas prácticas para un agente de IA (Codex, Claude u otro) que tenga que probar este
proyecto con una partida real de **KSP 1.12.5 + kRPC 0.7.0** en Windows. Todo
lo que aparece aquí se comprobó el 1 de noviembre de 2026 en el PC del
proyecto, incluidos los errores. Los resultados de la prueba del HUD están en
[VALIDACION.md](VALIDACION.md).

## 1. Reglas antes de tocar nada

- **La aplicación es de solo lectura.** `integrations/ksp_server.py` y las
  páginas web nunca envían mandos al juego. No añadas control de vehículo a la
  aplicación.
- **Por defecto, el vehículo se conduce con teclado y ratón** (computer use),
  como haría una persona. kRPC solo se usa para *leer* (telemetría, órbita,
  motores, temperaturas) con `tools/ksp/`.
- Controlar el vehículo **por kRPC** (sección 7) solo está permitido si el
  usuario lo pide expresamente para esa prueba, en un script aparte que no forme
  parte de la aplicación.
- Nunca presentes telemetría simulada (demo, `synthetic-ksp-demo`) como real.
- Duna/Kerbin y Marte no comparten coordenadas: el HUD de `ksp.html` usa una
  correspondencia local calibrada. El mapa nativo `ksp-map.html` usa el cuerpo real.

## 2. Preparar el entorno

1. KSP 1 (Steam) con el mod kRPC 0.7.0 en `GameData`. Entra en una partida en
   vuelo; en la ventana **kRPC** pulsa **Start server** (RPC `127.0.0.1:50000`,
   stream `50001`).
2. La primera vez que un cliente se conecta, el juego muestra un aviso para
   aceptarlo. Después aparece en la lista de clientes de la ventana kRPC.
3. Entorno Python del repositorio (`krpc==0.7.0` en `integrations/requirements-ksp.txt`):

   ```powershell
   py -3 -m venv .venv
   .venv\Scripts\python.exe -m pip install -r integrations/requirements-ksp.txt
   ```

4. Conector HTTP (déjalo en segundo plano):

   ```powershell
   .venv\Scripts\python.exe integrations/ksp_server.py
   ```

   Comprueba `GET http://127.0.0.1:7173/api/ksp`: debe dar `status: connected`,
   `source: KSP1-kRPC` y `readOnly: true`. Devuelve `503` si no hay juego o los
   datos tienen más de 4 s.
5. Herramientas de lectura del agente (sin `-I`, porque importan `_conexion.py`):

   ```powershell
   .venv\Scripts\python.exe tools/ksp/estado.py
   .venv\Scripts\python.exe tools/ksp/monitor.py --hasta-ap 80000 --intervalo 0.5
   ```

   `estado.py` muestra vehículo, situación, rumbo/cabeceo/alabeo, Ap/Pe, masa,
   empuje real frente a disponible, acelerador, SAS, frenos, recursos, motores y
   las piezas más calientes. `monitor.py` repite la lectura y termina (código 0)
   cuando se cumple una condición: `--hasta-ap`, `--hasta-pe`, `--min-alt`,
   `--max-calor`, `--antes-ap`.

## 3. Computer use con KSP en Windows

- Pide acceso a **"Kerbal Space Program"** y también a **`ksp_x64.exe`**: la
  ventana pertenece a ese proceso y sin él la captura sale enmascarada.
- `open_application("Kerbal Space Program")` falla (es un enlace `steam://`);
  usa `open_application("Ksp_x64")` para traer la ventana al frente.
- Antes de enviar teclas, **haz clic en una zona vacía del cielo** para dar el
  foco al juego. No hagas clic sobre el vehículo: abre menús de piezas.
- Las teclas mantenidas (`hold_key`) llegan bien a KSP. Comprueba siempre el
  efecto con `tools/ksp/estado.py` o `/api/ksp`, no solo con capturas.
- **Teclado en español:** la tecla `/` (detener aceleración de tiempo) no llega
  como `/`. Para bajar la aceleración usa `,` varias veces, o lee
  `space_center.warp_rate` para confirmar que es `1`.
- La interfaz está en español: el grupo de frenos se llama "Conmutar Grupo de
  Acción de Frenos" y SAS aparece como "SAE".

### Iconos útiles (ventana de ~980×800 px en la esquina superior izquierda)

Las posiciones cambian con el tamaño de la ventana; localízalas con una captura
y pasando el ratón por encima (aparece el nombre).

- Arriba, a la derecha del altímetro: luces, tren y **frenos** (de arriba a
  abajo). Hacer clic en el icono de frenos los deja **activados de forma fija**;
  es la forma fiable de detener un rover.
- A la izquierda de la navball: modos SAS. Fila superior: estabilidad y nodo;
  segunda fila: **prógrado** y **retrógrado**; luego normal/antinormal y
  radial. Los clics aquí **no siempre se registran** (a veces hace falta pasar
  el ratón antes). Confirma el modo con `estado.py`.

## 4. Mandos de teclado comprobados

| Acción | Tecla | Notas de la prueba |
| --- | --- | --- |
| SAS on/off | `T` | Al apagarlo y encenderlo vuelve a **estabilidad**, útil cuando los iconos fallan. |
| Acelerador máx./cero | `Z` / `X` | **Verifica** el resultado: en el ascenso el Dart estaba al 21 % (38 de 180 kN) hasta pulsar `Z` otra vez. |
| Etapa siguiente | `Espacio` | |
| Cabeceo | `W` baja el morro, `S` lo sube | Con SAS en estabilidad, el avión vuelve a su actitud al soltar. |
| Alabeo | `Q` / `E` | ~100°/s en el Aeris 4A a gran velocidad: pulsos de 0,3 s. |
| Rover: avanzar/girar | `W`/`S`, `A`/`D` | Crater Crawler: `W` 8 s → 19 m/s; pulsos de 1,5–2,5 s → 4–6 m/s. |
| Frenos | `B` (mantener) | Mantener `B` **no siempre frenó**. Usa el icono de frenos. |
| Tren | `G` | |
| Vista de mapa | `M` | El mapa tenía muchas líneas superpuestas; mejor leer la órbita con `estado.py`. |
| Aceleración de tiempo | `.` sube, `,` baja | Se detiene sola al entrar en la atmósfera (70 km en Kerbin). |
| Grupo de acción 1 | `1` | En el Aeris 4A no hizo nada (no lleva RAPIER). |

## 5. Trampas de kRPC (lectura)

- **Rumbo y cabeceo:** `vessel.flight(body.reference_frame).heading` (lo que usa
  `integrations/ksp_server.py` hoy) **no coincide con la navball**: 171,8°
  frente a 151°, y 196° frente a 227°. Usa
  `vessel.flight(vessel.surface_reference_frame)` para rumbo, cabeceo y alabeo.
  La latitud y la longitud sí son correctas, y la trayectoria calculada con ellas
  coincidía con la navball.
- `flight(body.reference_frame).speed` es velocidad de superficie;
  `vessel.orbit.speed` es la orbital (la que muestra la navball en modo "Órbita").
- Ap y Pe están en `vessel.orbit.apoapsis_altitude` y `periapsis_altitude`.
  `time_to_apoapsis` es grande (~1300 s) si ya has pasado la apoapsis: señal
  de que vas bajando.
- Calor: `part.temperature / part.max_temperature` y la versión `skin_*`. Al
  destruirse el vehículo, `vessel.parts.all` queda vacío y aparecen
  `Escombros de …` en `space_center.vessels`.

## 6. Probar el HUD (`ksp.html`) con el rover

1. En `/` calcula Stornoway → Whaligoe (`targetSelect` 0 y 717, `addStop`,
   `plan`) y pulsa **Prueba KSP**. La misión queda en
   `sessionStorage['mars-ar-mission']`.
2. `connectKsp` → `calibrateKsp` con el rover **parado**.
3. **Rotación del escenario** (`kspHeadingOffset`): rotación = rumbo real de
   desplazamiento en KSP − rumbo inicial de la ruta en el mapa. El rumbo inicial
   sale de `gridPath` (la *y* crece hacia el sur): Stornoway → Whaligoe sale a
   ≈135° y gira a ≈100°. Los "20°" de la misión son la **pendiente máxima**, no
   el rumbo. Con el rover avanzando a 151°, la rotación correcta fue 16°.
   Cambiar la rotación anula la calibración: vuelve a calibrar.
4. Para seguir la prueba, registra cada 0,5 s `kspStatus`, `navigationBanner`,
   `hudReplanStatus` y `arStatus`, y envuelve `speechSynthesis.speak/cancel`
   para registrar lo que dice la voz.
5. Comportamiento observado: el desvío sube de forma lineal si la rotación es
   incorrecta. A unos 30 m dice "Recalculando ruta.", luego "Ruta recalculada.",
   el desvío vuelve a unos 4 m y la misión pasa a "Posición actual" → destino.

## 7. Control por kRPC (solo si el usuario lo pide)

Habría evitado los fallos de la sección 8, pero **cambia el juego**. Úsalo solo
en un script aparte y con permiso expreso. API de kRPC 0.7.0:

```python
sc = conn.space_center; v = sc.active_vessel; c = v.control
c.throttle = 1.0                      # 0..1, y comprueba v.thrust/v.available_thrust
c.activate_next_stage()
c.sas = True; c.sas_mode = sc.SASMode.prograde
c.brakes = True; c.wheel_throttle = 0.3; c.wheel_steering = -0.2   # rover
c.toggle_action_group(1)
ap = v.auto_pilot; ap.engage(); ap.target_pitch_and_heading(15, 90)   # grados
sc.warp_to(sc.ut + v.orbit.time_to_apoapsis - 30)                     # para 30 s antes
```

## 8. Vuelo del Aeris 4A: qué pasó y cómo hacerlo mejor

Vehículo: 2 × Whiplash (etapa 1) + aerospike T-1 "Dart" (etapa 0, 180 kN,
Isp 340 s en vacío). La masa era de 17,1 t al encender el Dart. Cabina Mk1.

**Ascenso con motores de aire (bien):** SAS, `Z`, `Espacio`. A 100–110 m/s,
`S` 1,5 s para despegar y `G`. El SAS mantuvo ~15° de subida:
5 km → 725 m/s, 10 km → 1065 m/s, 15,8 km → 1289 m/s, 20–22 km → ~1310 m/s
(meseta). Por encima de ~25 km los Whiplash se apagaron por falta de aire.

**Fase cohete (con errores):**

1. Se encendió el Dart con `Espacio`, pero con el acelerador al 21 %. Durante
   ~1 min apenas aceleró (1,5 m/s²) y la apoapsis se quedó en 52 km. Con `Z`
   pasó a 180 kN (~10,6 m/s²).
2. Con el empuje completo, la apoapsis subió de ~50 a 91 km en ~60 s
   (velocidad orbital 2180 m/s). El corte llegó tarde por la latencia de lectura
   más tecla: la apoapsis quedó en 113 km en vez de 85. **Corta a ~75 km de
   apoapsis** o vigila con `monitor.py --hasta-ap` y un margen.
3. Se usó aceleración de tiempo 10× para esperar la apoapsis. `/` no la detuvo
   (teclado español): el avión pasó la apoapsis y empezó a quemar **bajando a
   68 km**. La apoapsis subió a 1067 km, se agotó el oxidante y el periapsis
   quedó en 43 km.
4. **Reentrada:** la primera pasada a 43 km y ~2800 m/s se superó con el morro en
   prógrado. En la segunda se invirtió el avión (sustentación hacia abajo, ~20°
   de ataque) para frenar más. La cabina Mk1 pasó del 60 % al 93 % de su
   temperatura máxima. Después, cambios bruscos de alabeo y cabeceo a ~2560 m/s
   y ~45 km **destruyeron el avión** (solo quedaron escombros).

**Lecciones:**

- Comprueba `empuje == empuje disponible` justo después de encender cada motor.
- Para esperar a la apoapsis usa `,` (no `/`) y confirma `warp_rate == 1` y
  `time_to_apoapsis` pequeño **antes** de acelerar.
- Planifica el combustible: circularizar a 85 km desde una apoapsis de 85 km con
  el periapsis bajo cuesta unos 200–700 m/s según la velocidad que lleves.
- En reentrada, la pieza limitante es la **cabina Mk1**. Vigila con
  `monitor.py --max-calor 0.8`. Usa poco ángulo de ataque y ninguna maniobra
  brusca por encima de ~1500 m/s. Si la apoapsis es alta, es más seguro
  aerofrenar en varias pasadas con aceleración de tiempo, sin invertir el avión.
- El rover también puede seguir rodando tras soltar `W`: deja los frenos fijos
  con el icono y confirma `velocidad ≈ 0`.
