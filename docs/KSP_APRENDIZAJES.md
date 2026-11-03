# Aprendizajes de las pruebas KSP reales (v1.1.0 – v1.7.5)

> **Seguimiento v1.7.10:** las bitácoras v1.7.9 y tormenta se cruzaron con Supabase y sus ZIP. Caché integrada desde PR #4; nuevo umbral de desvío, registro de cobertura y clasificación de peticiones. Los resúmenes históricos desfasados están anotados sin reescribir muestras. Consulta [la revisión vigente](KSP_REVISION_V1710.md); el texto siguiente conserva el contexto de las pruebas anteriores.


Resumen de lo que se aprendió en las sesiones del 1 y 2 de noviembre de 2026 (FULLY4425, con ayuda de Claude). Sirve para preparar los próximos experimentos sin repetir los mismos tropiezos. Los detalles y las evidencias de cada sesión están en [la bitácora](KSP_COLABORADORES.md#registro-de-sesiones); aquí solo se resumen. Los valores son medidas de un equipo y una partida concretos, no garantías.

## 1. Puesta en marcha que funciona

| Paso | Detalle aprendido |
| --- | --- |
| kRPC en KSP | Después de cada arranque de KSP hay que pulsar **Start server** en la ventana de kRPC. Mientras tanto el conector muestra `kRPC no disponible: timed out` cada 4 s; es normal. |
| Conector | `.venv\Scripts\python.exe -u integrations/ksp_server.py` desde la carpeta del repositorio. Desde v1.7.2 necesita `psutil` para medir el PC. |
| Navegador | Abrir **`http://localhost:7173/ksp-map.html`**. La versión de Render (`onrender.com`) no puede llegar al conector local. |
| Consentimiento (v1.7.3+) | Al arrancar aparece un aviso de Windows. Con **Permitir esta sesión**, la sesión se sube a Supabase sin cuenta personal. El permiso se vuelve a pedir en cada arranque. Primera subida real confirmada desde el PC de FULLY4425: 2026-11-02 23:43:45 UTC. |
| Mapa SCANsat | Exportar el CSV desde el mapa grande de SCANsat (Altimetry). Convertirlo con `scripts/import-scansat.py` y cargarlo con **Cargar mapa KSP (.json)**. Con valores negativos usa `--lon=-73.82612` (con `=`). |
| Mapa grande de SCANsat | Si `BigMapWidth` supera la pantalla (por ejemplo, 2276 px), la ventana no se puede mover ni exportar. Baja el ancho a 1280 en los ajustes de SCANsat y usa "Reset Window Positions". |
| Al cambiar de vehículo | La guía se pausa ("Cambió el vehículo…"); recalcula desde la nueva posición. Si reinicias el conector, vuelve a importar el JSON del mapa: "Conectar KSP usando este mapa" no basta. |

## 2. Valores de referencia medidos

| Medida | Valor | Sesión |
| --- | --- | --- |
| Lectura kRPC por muestra | media 8,8 ms · p95 37 ms · máx. 117 ms | v1.7.2 |
| KSP (CPU / memoria) | ~255 % de un núcleo (≈21 % de 12 hilos) · 7,4–7,9 GB | v1.4.0 y v1.7.2 |
| Conector (memoria) | 44 MB (v1.4.0) · 75 MB (v1.7.2 con diagnóstico) | |
| Repintado del mapa | 0,74 ms de media (v1.4.0, navegador de la app) · 9,6 ms de media y 173 ms de máximo (v1.7.2, Firefox) | |
| FPS de KSP | No disponibles por kRPC; hace falta una herramienta externa | |
| Tamaño de la carpeta de sesión | ~18 MB en 2 h 40 min (ZIP ~1,9 MB) | v1.7.2 |
| Mapa SCANsat | CSV de 1126 × 563, 83,5 % de cobertura; regiones de 17 × 17 celdas de 2000 m | v1.4.0 |

**Satélites SCANsat en Duna:**
- SAR-X: 70–500 km, ideal por encima de 250 km.
- R-3B: ideal por encima de 70 km.
- Hay dos satélites, los dos llamados "Nave Espacial Sin Nombre":
  - 352 × 235 km, i 72,24°, periodo 5505 s.
  - 328,6 × 269 km, i 88,47° (polar), periodo 5571 s.

  Conviene renombrarlos para distinguirlos en la telemetría.

## 3. Conducción del Crater Crawler en Duna

- **Pendientes:** en pendientes de 13–16°, con los frenos puestos, el rover se desliza a ~0,9 m/s y no puede cumplir la parada de 3 s. Para confirmar la llegada, elige destinos en zonas de unos 4°.
- **Velocidad:** a más de 20 m/s el rover salta (situación `flying`, picos de 4,4 g) y pasa de largo. En v1.7.2 pasó a 152 m del destino a 21,7 m/s y a 12 m de otro a 14,2 m/s; no hubo llegada.
- **Llegada:** solo se confirma a ≤ 8 m y con el rover parado 3 s. Lo práctico es acercarse a menos de 5 m/s y frenar por pulsos (frenos fuera 3–6 s, frenos dentro).
- **Teclado (distribución española):**
  - Para salir de la aceleración temporal se usa `,`; `/` no funciona.
  - `Alt+A` / `Alt+D` dejan un ajuste fijo de dirección; `Alt+X` lo borra.
- **Cargar partida:** si se carga una partida guardada, el rover vuelve a su posición antigua y la telemetría muestra un salto. Anótalo para no confundirlo con un error del mapa.

## 4. Fallos ya encontrados y su estado

| Fallo | Visto en | Estado |
| --- | --- | --- |
| Rumbo leído en un marco incorrecto | v1.1.0 | Corregido en v1.2.0 (comprobado en el juego). |
| Ruta de "0 m" con el destino en la misma celda de 2 km | v1.4.0, v1.7.2 | Corregido en v1.7.5 según [la revisión](KSP_REVISION_V175.md); falta comprobarlo en el juego. |
| Recálculo cada 20 s por clima, con ETA variable | v1.7.2 | Corregido en v1.7.5; falta comprobarlo en el juego. |
| Ráfaga de reconexiones al cambiar de vehículo | v1.7.2 | Corregido en v1.7.5; falta comprobarlo en el juego. |
| Avisos de llegada y velocidad sin registro | v1.7.2 | v1.7.5 añade eventos `browser-arrival-confirmed`, `browser-destination-passed`, `browser-driving-advice` y `browser-region-exit`. |
| Hay que volver a importar el mapa tras reiniciar el conector | v1.4.0 | Abierto. |
| "Repetir" no habla tras la llegada | v1.4.0 | Abierto. |

## 5. Protocolo propuesto para el próximo experimento (v1.7.5 o posterior)

1. Arrancar KSP → **Start server** en kRPC → arrancar el conector → aceptar o rechazar el aviso → abrir localhost en Firefox.
2. Pasar al rover y cargar el JSON SCANsat de la zona (por ejemplo, [duna-rover-scansat-2.json](ksp-logs/2026-11-01-FULLY4425-travesia/duna-rover-scansat-2.json)).
3. **Dejar desactivado el ciclo de clima.**
4. **Misma celda:** dos destinos a unos 600 m dentro de una celda de 2 km. La ruta debe mostrar la distancia real, no "0 m".
5. **Llegada:** conducir a menos de 5 m/s en una zona llana y parar a ≤ 8 m durante 3 s. Buscar `browser-arrival-confirmed` en `events.jsonl`.
6. **Paso de largo y velocidad:** pasar un destino a más de 5 m/s. Buscar `browser-destination-passed` y `browser-driving-advice`.
7. **Salida de región:** salir del área del JSON importado. Buscar `browser-region-exit`.
8. **Cambio de vehículo:** cambiar al satélite y volver. El conector no debe crear varias sesiones kRPC seguidas.
9. **Rendimiento:** comparar el repintado en Firefox con el valor de v1.7.2. Si es posible, medir los FPS con una herramienta externa.
10. Copiar las evidencias a `docs/ksp-logs/AAAA-MM-DD-usuario/`, quitando el nombre de usuario de Windows de las rutas, y añadir la sesión a la bitácora.

## 6. Cómo leer las evidencias de una sesión

Cada arranque del conector crea `ksp-sessions/<fecha>-<id>/`, excluida de Git:

- `telemetry.jsonl` y `flight.jsonl`: una muestra por segundo, con `vessel`, `situation`, latitud y longitud, velocidad y órbita.
- `events.jsonl`: conexiones, rutas (`browser-route-created` con `reason`), estado de la guía y, desde v1.7.5, llegada y avisos.
- `mission-*.json` y `terrain-*.json`: cada ruta calculada y cada región cargada.
- `computer.jsonl`: CPU, RAM, memoria de KSP y del conector cada 5 s. `analysis.json`: picos y recomendaciones automáticas.
- `connector.log`: registro de texto del conector.

**Comprobaciones útiles:**
- Contar los eventos por `type`.
- Calcular la distancia mínima a cada destino a partir de la telemetría del rover (radio de Duna: 320 000 m) y la velocidad en ese momento.
- Agrupar la telemetría por `vessel` y `situation` para detectar cambios de vehículo, saltos y cargas de partida.

Un evento de texto no demuestra que la voz se oyera, y la telemetría no sustituye a ver la pantalla: anota siempre qué observaste en directo y qué se reconstruyó después.
