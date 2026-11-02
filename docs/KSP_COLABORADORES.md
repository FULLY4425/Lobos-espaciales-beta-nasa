# Bitácora y validaciones · Pruebas de integración KSP

Este documento reúne las experiencias de quienes prueban la integración con una partida real de **Kerbal Space Program 1**: mapa nativo, conector kRPC, HUD conectado al juego y mapas importados utilizados junto a KSP.

**Este es el documento único para reunir las pruebas del equipo.** Integra también todo el contenido del antiguo `VALIDACION.md`, además de la sesión real que ya se había trasladado.

[Registro de sesiones KSP](#registro-de-sesiones) · [Plantilla para nuevas pruebas](#plantilla-para-copiar) · [Validaciones previas y pendientes](#validaciones-registradas-y-pruebas-pendientes)

Cada colaborador añade aquí sus resultados, logs, errores, mejoras y sugerencias. También se pueden documentar intentos reales bloqueados por problemas de conexión, indicando qué se intentó. Las pruebas exclusivas de la demo, del explorador de Marte o de AR sin KSP quedan fuera del alcance de esta bitácora.

[Configuración del conector](AR_KSP.md) · [Mapa nativo KSP](KSP_MAPA.md) · [Mapas SCANsat](KSP_MAPAS_DATOS.md) · [Validaciones registradas](#validaciones-registradas-y-pruebas-pendientes)

## Cómo añadir tu experiencia

1. Copia la plantilla de este documento y añádela al final, después del registro de sesiones.
2. Identifica la versión o commit realmente probado, aunque sea anterior al actual.
3. Completa los datos del entorno, pasos, resultados y sugerencias. Marca como **No probado** lo que no hayas comprobado.
4. Añade los logs y evidencias con nombres que permitan relacionarlos con la sesión. Puedes usar `docs/ksp-logs/AAAA-MM-DD-usuario/` para archivos de texto revisados, misiones JSON y capturas. Crea la carpeta cuando tengas archivos que aportar.
5. Enlaza los archivos desde tu entrada y relaciona los errores con la hora o línea del log. Si falta algún log, explica por qué y qué evidencia sí obtuviste.
6. Guarda los cambios con un commit o abre un pull request para que el equipo revise e incorpore la experiencia.

Desde GitHub puedes editar este documento con el botón del lápiz y subir los archivos con **Add file → Upload files** en la carpeta correspondiente. Para un cambio que incluya varios archivos, conviene trabajar en una rama y agruparlo en un pull request. Si no tienes permiso de escritura, utiliza un fork y propone el pull request.

Este repositorio es público: revisa los logs antes de añadirlos, especialmente claves, correos, nombres de usuario y rutas personales. Usa archivos de texto o ZIP revisados para logs extensos y respeta los límites de archivos de GitHub. No añadas el juego, ejecutables, credenciales ni tu instalación completa de KSP.

## Qué evidencias recopilar

- **`KSP.log`** de la carpeta de instalación, correspondiente a la sesión del problema. Si aportas `Player.log`, identifica instalación y sesión.
- **Salida del conector Python**, con mensajes de inicio, conexión y errores. Por ejemplo:

  ```bash
  # macOS/Linux, desde la raíz del repositorio:
  .venv/bin/python -u integrations/ksp_server.py > ksp-connector.log 2>&1
  ```

  ```powershell
  # Windows, desde la raíz del repositorio:
  .venv\Scripts\python.exe -u integrations/ksp_server.py *> ksp-connector.log
  ```

  Mantén el proceso abierto durante la prueba y detén con Ctrl+C al terminar. La salida se escribe en el archivo en estos ejemplos.
- **Errores de la consola del navegador**, con mensaje completo y hora.
- **Misión y mapa exportados**, cuando el fallo dependa de destinos, alturas, pendiente o cobertura.
- **Capturas o video** del juego y la guía; para errores de rumbo, compara con la navball.
- **Estado del conector**, si es relevante: guarda la respuesta de `http://localhost:7173/api/ksp` y de `http://localhost:7173/api/ksp/terrain`. Son instantáneas, no logs de toda la sesión.

## Plantilla para copiar

Copia el bloque siguiente, rellénalo y añade la sesión al registro. No marques la plantilla vacía como una prueba realizada.

**Si una IA prepara el registro:** debe editar `docs/KSP_COLABORADORES.md`, ruta relativa a la raíz del repositorio. Añadirá la sesión en **Registro de sesiones**, antes de **Validaciones registradas y pruebas pendientes**, y su enlace en la tabla. Los logs y adjuntos van en `docs/ksp-logs/AAAA-MM-DD-usuario/`. Debe conservar los registros existentes e indicar qué no se probó, sin inventar resultados.

```markdown
<!-- Instrucción para IA: añade esta sesión en docs/KSP_COLABORADORES.md,
     dentro de Registro de sesiones y antes de Validaciones registradas y pruebas pendientes.
     Añade su enlace a la tabla. Guarda evidencias en docs/ksp-logs/AAAA-MM-DD-usuario/
     y enlázalas desde aquí. No crees otra bitácora ni sobrescribas sesiones anteriores. -->
## AAAA-MM-DD · Usuario · Título de la prueba

### Sesión y entorno

- Colaborador / usuario de GitHub:
- Fecha, hora y zona horaria:
- Aplicación: versión y commit probado:
- KSP: versión y distribución:
- kRPC: versión del mod y del cliente Python:
- Python / sistema operativo / navegador:
- Equipo: CPU, RAM y GPU:
- Mods relevantes y versiones (o stock):
- Área probada: mapa nativo / HUD con KSP / mapas importados / conector:
- Cuerpo, ubicación y vehículo o astronauta:
- Duración aproximada de la sesión:
- Resultado general: funcionó / parcial / bloqueado:
- Confirmación: esta experiencia corresponde a una prueba con KSP real:

### Configuración y preparación

Indica cómo ejecutaste el conector, puertos, mapa/misión utilizada,
resolución, pendiente, destinos y cualquier ajuste necesario para repetirla.

### Pasos de la prueba

1.
2.
3.

### Resultado esperado

### Resultado observado y experiencia de uso

Incluye respuesta de la guía, fluidez, indicaciones y diferencias con el juego.

### Comprobaciones

Usa Correcto / Falló / No probado / No aplica, con observaciones.

| Comprobación | Resultado | Observaciones / evidencia |
| --- | --- | --- |
| Conexión y reconexión kRPC | No probado | |
| Posición y cuerpo correctos | No probado | |
| Rumbo frente a la navball | No probado | |
| Muestreo de alturas | No probado | |
| Destinos y cálculo de ruta | No probado | |
| Recálculo al desviarse | No probado | |
| Pausa por desconexión / salida de región | No probado | |
| Indicaciones y voz | No probado | |
| Importación / exportación de mapas | No probado | |
| Fluidez y consumo de recursos | No probado | |

### Logs y evidencias

Enlaza cada archivo y explica qué demuestra. Indica sesión, hora o líneas
relevantes. Añade extractos si ayudan, conservando también los logs completos.

- Log KSP:
- Log del conector:
- Errores de navegador:
- Misión / mapa:
- Capturas / video:
- Evidencias que faltan y motivo:

### Errores encontrados

Para cada error: pasos, hora, mensaje exacto, frecuencia e impacto.

### Mejoras y sugerencias

Para cada propuesta: problema, cambio sugerido, utilidad y prioridad.
Si no tienes propuestas, indícalo.

### Seguimiento

- Pendientes:
- Respuesta o revisión de otro colaborador:
- Nueva versión probada y resultado:
- Estado: pendiente / en revisión / resuelto:
```

## Registro de sesiones

Añade las experiencias debajo de esta tabla y enlaza aquí su encabezado. Conserva las observaciones originales cuando añadas una repetición o corrección.

| Fecha | Colaborador | Versión / commit | Prueba | Resultado | Enlace a la sesión |
| --- | --- | --- | --- | --- | --- |
| 2026-11-01 | No identificado en el registro original | Copia anterior a `92c7046` | HUD con KSP 1.12.5 · Crater Crawler en Kerbin | Parcial; incidencias y pendientes documentados | [Leer sesión](#2026-11-01--prueba-real-del-hud-ksp-1125) |

## 2026-11-01 · Prueba real del HUD KSP 1.12.5

> Procedencia: registro trasladado desde `docs/VALIDACION.md` el 2 de noviembre de 2026, conservando las observaciones originales. Colaborador no identificado en el registro de origen.
>
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


## Validaciones registradas y pruebas pendientes

Contenido completo incorporado desde el antiguo `docs/VALIDACION.md` el 2 de noviembre de 2026. Se conserva como antecedente de las comprobaciones del proyecto; las experiencias nuevas de KSP se añaden al registro de sesiones de este mismo documento. Las comprobaciones simuladas y de otros modos siguen identificadas como tales.

Estado documental: **2 de noviembre de 2026**. Este documento recoge comprobaciones realizadas durante el desarrollo; no es una certificación científica, de seguridad, de rendimiento AR ni de compatibilidad de hardware.

### Pruebas automatizadas incluidas

| Suite | Último resultado registrado | Cobertura |
| --- | --- | --- |
| `python3 -m unittest discover -s test -v` | 31 pruebas aprobadas. | Planificación, obstáculos, esquinas, pendientes, datos reales, entradas y objetivos propios; contrato/frescura de telemetría y lecturas con cliente kRPC simulado; archivos de mapa, conversión SCANsat, huecos, procedencia y marco de rumbo. |
| `node test/directions.test.js` | 6 pruebas aprobadas. | Derecha/izquierda, ruta recta, agrupación de zigzags, objetivos intermedios, distancia 3D, rutas vacías y media vuelta. |
| `node test/ar-tracking.test.js` | 5 pruebas aprobadas. | Proyección relativa, radio del cuerpo, cruce de longitud, cambio de vehículo/cuerpo, rotación de calibración y distancia a la ruta. |
| `node test/replanning.test.js` | 4 pruebas aprobadas. | Paradas pendientes, nueva salida, rechazo fuera del mapa, progreso físico y origen KSP conservado. |
| `node test/ksp-geo.test.js` | 3 pruebas aprobadas. | Proyección nativa, altas latitudes, cruce de longitud y destinos con coordenadas de malla. |


Total registrado: **49 pruebas**. No se necesita Node.js para ejecutar el servidor; es una herramienta opcional de desarrollo. Los comandos y la arquitectura están en [DESARROLLO.md](DESARROLLO.md).

### Comprobaciones de navegador realizadas

Se utilizó Chromium con Playwright como herramienta temporal. Estos scripts de navegador no forman parte de una suite versionada del repositorio.

- Carga de los 718 objetivos y de la ortofoto HiRISE; mapa 2D, terreno 3D, globo y cámaras.
- Recorrido Stornoway → Whaligoe a 20°: unos 1310 m, +59.6 m de ascenso y 50 minutos educativos. La distancia de la animación puede ser ligeramente mayor al considerar desplazamiento 3D; las métricas de misión usan distancia horizontal.
- Astronautas: reproducción, pausa, avance, llegada y limpieza de la ruta.
- Creación de objetivos propios en 2D/3D y por coordenadas, rechazo fuera de cobertura, persistencia al recargar, eliminación y ruta combinada con un objetivo científico.
- Indicaciones: selección de voz, inicio/pausa, llegada, recálculo y cancelación con motor de voz simulado. Alternativa de texto cuando no existe síntesis. No se afirma haber escuchado todas las voces de dispositivos reales.
- Menú KSP separado: transferencia de misión, estado sin conector y demostración del HUD. Se comprobaron cero solicitudes a cámara o consulta WebXR en esa página.
- HUD AR: misión cargada, interfaz compacta sin desbordamiento, simulación, inicio/cierre con cámara de prueba de Chromium y alternativa ante rechazo de sesión WebXR.
- KSP: calibración, recálculo por desvío y pausa fuera de cobertura con telemetría simulada, y respuesta `503` del conector cuando no hay juego/dependencia disponible.

### Bitácora KSP: documento (v1.3.1)

La bitácora se conserva únicamente como documento Markdown con plantilla, registro de sesiones e instrucciones para logs. Se retiraron la página, sus scripts/estilos, el formulario de issues y sus ocho pruebas específicas. Las comprobaciones históricas de esa página corresponden a v1.3.0 y no describen una función disponible en la versión actual. Se verificaron enlaces y empaquetado del documento.

### Mapas descargables (v1.2.0)

CSV de prueba con el formato del exportador SCANsat 21.1: importación, huecos bloqueados, rechazo de columnas ambiguas y números no finitos, y conservación de coordenadas/alturas. En Chromium se comprobaron carga, salida manual, planificación, relieve 3D, descarga/reimportación, pérdida de conector y tamaño compacto sin errores JavaScript. Se repitió el flujo del conector con cuerpo y telemetría simulados. No se ha procesado todavía una exportación de una partida real en esta validación.

### Pruebas reales de KSP registradas en la bitácora

El registro de conexión y conducción del rover Crater Crawler con KSP 1.12.5 se trasladó a la [bitácora de colaboradores](KSP_COLABORADORES.md#2026-11-01--prueba-real-del-hud-ksp-1125). Allí se conservan el entorno, pasos, mediciones, incidencias y pendientes originales. Las nuevas experiencias con el juego se añaden en esa misma bitácora.

### Distribución y servicio público

`python3 scripts/build.py` ha generado correctamente la aplicación ejecutable, incluyendo las pantallas KSP y AR y el conector opcional. La salida es una aplicación Python, no un sitio que pueda planificar rutas con alojamiento exclusivamente estático.

Se verificaron en Render los recursos publicados y respuestas HTTP de salud, planificación y exportación, incluyendo puntos personalizados. La aplicación pública es un prototipo; no sustituye las pruebas físicas que faltan.

Las capturas del README documentan la interfaz web. Una captura o emulación de pantalla no acredita uso en un visor físico.

### Pendiente de validar

| Área | Falta por comprobar |
| --- | --- |
| KSP real | Conexión y conducción breve en Kerbin comprobadas con la versión anterior (véase la bitácora de colaboradores). Falta probar el mapa nativo con el juego, llegar al destino, Duna, la suspensión fuera de cobertura y sesiones largas. La corrección del rumbo del conector implementada en v1.2.0 aún necesita compararse con la navball en el juego real. |
| AR físico | Permisos, detección de superficies, estabilidad de maqueta, visibilidad, entrada y finalización en un visor concreto. |
| Casco de astronauta | Hardware, SDK, sensores, óptica, latencia, interacción, ergonomía y ensayos específicos. No hay un casco integrado. |
| Rendimiento | FPS, consumo, temperatura y autonomía medidos en hardware real. Las optimizaciones actuales son de arquitectura y carga de recursos. |
| Ciencia | Precisión horizontal absoluta, alineación vertical de las alturas científicas, obstáculos pequeños y modelos de movilidad humana. |

La etiqueta PDS y la coincidencia numérica de coordenadas no demuestran por sí solas exactitud absoluta. Las rutas no validan resistencia del suelo, seguridad, comunicaciones, radiación ni autonomía de un traje.

### Recálculo y escenarios ambientales

Se comprobó que A* evita las celdas restringidas de una tormenta sintética,
conserva destino y restricciones de pendiente, y rechaza puntos sin salida.
En navegador se verificaron cambios de escenario, desvío del astronauta,
recálculo KSP con telemetría simulada y bloqueo fuera del terreno. Las condiciones
atmosféricas son supuestos de entrenamiento, no predicciones validadas.

### Distribución web actual

La versión actual se ejecuta en el navegador con el servidor Python y conserva las
funciones de mapa, clima simulado, navegación, KSP y AR. El endpoint `sw.js`
solo permite retirar trabajadores y cachés heredados; no instala una app.

Se verificó en navegador la retirada de cachés heredadas conservando puntos
personalizados, preferencias de voz y cachés ajenas. También se comprobaron
mapa 3D, tormenta simulada, exportación JSON y transferencia al menú KSP.

### Mapa nativo KSP

Se comprobaron proyección geográfica y radio del cuerpo, muestreo por bloques,
cancelación, rechazo de cuerpos gaseosos y conexiones caducadas, agua,
pendientes y separación respecto a coordenadas NASA. En navegador: demo
2D/3D, destinos, exportación, persistencia y recálculo con destinos pendientes.
También se ejercitaron las rutas HTTP reales del conector con un proveedor de
alturas/telemetría simulado: carga de región, ruta en Duna, desvío, cambio de
cuerpo y pérdida de datos. No equivale a una prueba en el juego real.
