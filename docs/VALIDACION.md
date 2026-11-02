# Validación registrada y pruebas pendientes

Estado documental: **1 de noviembre de 2026**. Este documento recoge comprobaciones realizadas durante el desarrollo; no es una certificación científica, de seguridad, de rendimiento AR ni de compatibilidad de hardware.

## Pruebas automatizadas incluidas

| Suite | Último resultado registrado | Cobertura |
| --- | --- | --- |
| `python3 -m unittest discover -s test -v` | 31 pruebas aprobadas. | Planificación, obstáculos, esquinas, pendientes, datos reales, entradas y objetivos propios; contrato/frescura de telemetría y lecturas con cliente kRPC simulado; archivos de mapa, conversión SCANsat, huecos, procedencia y marco de rumbo. |
| `node test/directions.test.js` | 6 pruebas aprobadas. | Derecha/izquierda, ruta recta, agrupación de zigzags, objetivos intermedios, distancia 3D, rutas vacías y media vuelta. |
| `node test/ar-tracking.test.js` | 5 pruebas aprobadas. | Proyección relativa, radio del cuerpo, cruce de longitud, cambio de vehículo/cuerpo, rotación de calibración y distancia a la ruta. |
| `node test/replanning.test.js` | 4 pruebas aprobadas. | Paradas pendientes, nueva salida, rechazo fuera del mapa, progreso físico y origen KSP conservado. |
| `node test/ksp-geo.test.js` | 3 pruebas aprobadas. | Proyección nativa, altas latitudes, cruce de longitud y destinos con coordenadas de malla. |


Total registrado: **49 pruebas**. No se necesita Node.js para ejecutar el servidor; es una herramienta opcional de desarrollo. Los comandos y la arquitectura están en [DESARROLLO.md](DESARROLLO.md).

## Comprobaciones de navegador realizadas

Se utilizó Chromium con Playwright como herramienta temporal. Estos scripts de navegador no forman parte de una suite versionada del repositorio.

- Carga de los 718 objetivos y de la ortofoto HiRISE; mapa 2D, terreno 3D, globo y cámaras.
- Recorrido Stornoway → Whaligoe a 20°: unos 1310 m, +59.6 m de ascenso y 50 minutos educativos. La distancia de la animación puede ser ligeramente mayor al considerar desplazamiento 3D; las métricas de misión usan distancia horizontal.
- Astronautas: reproducción, pausa, avance, llegada y limpieza de la ruta.
- Creación de objetivos propios en 2D/3D y por coordenadas, rechazo fuera de cobertura, persistencia al recargar, eliminación y ruta combinada con un objetivo científico.
- Indicaciones: selección de voz, inicio/pausa, llegada, recálculo y cancelación con motor de voz simulado. Alternativa de texto cuando no existe síntesis. No se afirma haber escuchado todas las voces de dispositivos reales.
- Menú KSP separado: transferencia de misión, estado sin conector y demostración del HUD. Se comprobaron cero solicitudes a cámara o consulta WebXR en esa página.
- HUD AR: misión cargada, interfaz compacta sin desbordamiento, simulación, inicio/cierre con cámara de prueba de Chromium y alternativa ante rechazo de sesión WebXR.
- KSP: calibración, recálculo por desvío y pausa fuera de cobertura con telemetría simulada, y respuesta `503` del conector cuando no hay juego/dependencia disponible.

## Bitácora KSP: documento (v1.3.1)

La bitácora se conserva únicamente como documento Markdown con plantilla, registro de sesiones e instrucciones para logs. Se retiraron la página, sus scripts/estilos, el formulario de issues y sus ocho pruebas específicas. Las comprobaciones históricas de esa página corresponden a v1.3.0 y no describen una función disponible en la versión actual. Se verificaron enlaces y empaquetado del documento.

## Mapas descargables (v1.2.0)

CSV de prueba con el formato del exportador SCANsat 21.1: importación, huecos bloqueados, rechazo de columnas ambiguas y números no finitos, y conservación de coordenadas/alturas. En Chromium se comprobaron carga, salida manual, planificación, relieve 3D, descarga/reimportación, pérdida de conector y tamaño compacto sin errores JavaScript. Se repitió el flujo del conector con cuerpo y telemetría simulados. No se ha procesado todavía una exportación de una partida real en esta validación.

## Conexión con una partida real de KSP 1 (parcial)

> Versión probada: copia local previa al commit `92c7046` (mapa nativo KSP), con
> `ksp.html` y el conector de esa copia. El mapa nativo `ksp-map.html` no se ha
> probado aún con el juego real. El fallo de rumbo descrito abajo se corrigió
> en v1.2.0 usando el marco de superficie; su comparación real con la navball sigue pendiente.

1 de noviembre de 2026, Windows 10, Python 3.13.17, Node.js 26.13.0. KSP 1.12.5
(Steam, build 03190) con el mod kRPC 0.7.0 y cliente Python `krpc==0.7.0`
(protobuf 7.36.2) en `.venv`. Servidor kRPC en 127.0.0.1, RPC 50000, stream 50001.

- Las 31 pruebas automatizadas de esa copia y `scripts/build.py` se ejecutaron sin errores en este equipo.
- Tras aceptar la conexión en el juego, `/api/ksp` devolvió `connected`, origen
  `KSP1-kRPC` y `readOnly: true` con datos del rover activo (Kerbin, cerca del KSC, parado).
- En `ksp.html`: **Conectar KSP local** identificó cuerpo y vehículo; la ruta
  Stornoway → Whaligoe (20°, 1310 m) se calibró con el vehículo y el HUD mostró la
  primera indicación con desvío 0 m.
- Observación: tras conectar, el HUD mantiene el texto “KSP requiere ejecutar
  integrations/ksp_server.py…”, aunque el conector ya esté en marcha.

### Conducción manual del rover (mismo día)

Se condujo el rover “Crater Crawler” con el teclado de KSP (W/A/D y grupo de
acción de frenos) en la pista del KSC, mientras `ksp.html` leía la telemetría por
`/api/ksp`. El conector solo leyó datos; no se enviaron controles por kRPC. Los
valores siguientes son los textos del HUD registrados cada 0,5 s en el navegador.

- **Orientación.** La primera salida de la ruta tiene rumbo de mapa ≈135° (luego
  gira hacia ≈100°); los “20°” de la misión son la pendiente máxima, no el rumbo.
  Con “Rotación del escenario KSP” en 0° y en 132° el desvío crecía casi al mismo
  ritmo que el avance. Con 16° (desplazamiento real del rover ≈151° − 135°) y
  recalibrando parado, la navegación encajó.
- **Avance con calibración correcta.** El aviso bajó de “En 50 metros” a 45, 40,
  35 … 5 m y “Ahora” con desvío entre 1 y 4 m. Tras el giro pasó a “En 870 metros ·
  Gira ligeramente a la derecha” y el total bajó de 1.3 a 1.2 km.
- **Recálculo por desvío.** Con un giro excesivo y, después, un desvío intencionado
  hacia la derecha, el desvío subió hasta 28–30 m; el HUD mostró “Recalculando desde
  la posición…”, y en aproximadamente un segundo pasó a “Ruta recalculada · …
  Se conservan las paradas pendientes”. El desvío volvió a 3–5 m. La misión
  guardada pasó a ser “Posición actual” → Whaligoe (≈1204 m). Con la rotación mal
  ajustada se repitió el recálculo cada ~7 s, y el aviso siempre volvía a
  “En 50 metros”.
- **Voz.** “Activar voz” cambió el botón a “🔊 Voz activada” y
  `speechSynthesis.speaking` pasó a `true` (Microsoft Helena es-ES). “Repetir
  indicación” enunció “En 830 metros, gira ligeramente a la derecha”. En el
  recálculo se registró: cancelar, “Recalculando ruta.”, “Ruta recalculada.”,
  y la nueva indicación al cabo de 1 s. No se escuchó el audio; solo se
  registraron las llamadas a la API de voz.
- **Parada.** El rover quedó detenido con el grupo de frenos activo (0,002 m/s).

Fallos y observaciones:

1. El aviso “KSP requiere ejecutar integrations/ksp_server.py…” sigue visible
   durante toda la conducción.
2. `heading` del conector no coincide con la navball: 171.8° frente a 151°, y 196°
   frente a 227° más tarde. La trayectoria medida por latitud y longitud coincidía
   con la navball. El conector usa `vessel.flight(body.reference_frame)`, y kRPC
   calcula el rumbo en el marco de superficie. La posición no se ve afectada,
   pero ese valor no sirve para orientar la ruta automáticamente.
3. La rotación hay que deducirla a mano (rumbo real − rumbo inicial de la ruta),
   y la interfaz no muestra el rumbo inicial de la ruta.
4. El estado de recálculo muestra “Despejado Â· simulado” (codificación incorrecta).
5. El texto de estado de voz no cambia mientras habla; el aviso “Ruta recalculada.”
   se corta casi enseguida por la siguiente indicación.
6. El total restante se redondea a 0,1 km, así que no cambia en tramos cortos.
7. En una ocasión el recálculo se disparó cuando el HUD mostraba 28 m.

**Aún sin comprobar con el juego:** completar la ruta hasta la llegada, “fuera de
cobertura” con mensaje de suspensión, Duna y sesiones largas.

## Distribución y servicio público

`python3 scripts/build.py` ha generado correctamente la aplicación ejecutable, incluyendo las pantallas KSP y AR y el conector opcional. La salida es una aplicación Python, no un sitio que pueda planificar rutas con alojamiento exclusivamente estático.

Se verificaron en Render los recursos publicados y respuestas HTTP de salud, planificación y exportación, incluyendo puntos personalizados. La aplicación pública es un prototipo; no sustituye las pruebas físicas que faltan.

Las capturas del README documentan la interfaz web. Una captura o emulación de pantalla no acredita uso en un visor físico.

## Pendiente de validar

| Área | Falta por comprobar |
| --- | --- |
| KSP real | Conexión y conducción breve en Kerbin comprobadas con la versión anterior (ver arriba). Falta probar el mapa nativo con el juego, llegar al destino, Duna, la suspensión fuera de cobertura y sesiones largas. También hay que corregir el rumbo del conector. |
| AR físico | Permisos, detección de superficies, estabilidad de maqueta, visibilidad, entrada y finalización en un visor concreto. |
| Casco de astronauta | Hardware, SDK, sensores, óptica, latencia, interacción, ergonomía y ensayos específicos. No hay un casco integrado. |
| Rendimiento | FPS, consumo, temperatura y autonomía medidos en hardware real. Las optimizaciones actuales son de arquitectura y carga de recursos. |
| Ciencia | Precisión horizontal absoluta, alineación vertical de las alturas científicas, obstáculos pequeños y modelos de movilidad humana. |

La etiqueta PDS y la coincidencia numérica de coordenadas no demuestran por sí solas exactitud absoluta. Las rutas no validan resistencia del suelo, seguridad, comunicaciones, radiación ni autonomía de un traje.

## Recálculo y escenarios ambientales

Se comprobó que A* evita las celdas restringidas de una tormenta sintética,
conserva destino y restricciones de pendiente, y rechaza puntos sin salida.
En navegador se verificaron cambios de escenario, desvío del astronauta,
recálculo KSP con telemetría simulada y bloqueo fuera del terreno. Las condiciones
atmosféricas son supuestos de entrenamiento, no predicciones validadas.

## Distribución web actual

La versión actual se ejecuta en el navegador con el servidor Python y conserva las
funciones de mapa, clima simulado, navegación, KSP y AR. El endpoint `sw.js`
solo permite retirar trabajadores y cachés heredados; no instala una app.

Se verificó en navegador la retirada de cachés heredadas conservando puntos
personalizados, preferencias de voz y cachés ajenas. También se comprobaron
mapa 3D, tormenta simulada, exportación JSON y transferencia al menú KSP.

## Mapa nativo KSP

Se comprobaron proyección geográfica y radio del cuerpo, muestreo por bloques,
cancelación, rechazo de cuerpos gaseosos y conexiones caducadas, agua,
pendientes y separación respecto a coordenadas NASA. En navegador: demo
2D/3D, destinos, exportación, persistencia y recálculo con destinos pendientes.
También se ejercitaron las rutas HTTP reales del conector con un proveedor de
alturas/telemetría simulado: carga de región, ruta en Duna, desvío, cambio de
cuerpo y pérdida de datos. No equivale a una prueba en el juego real.
