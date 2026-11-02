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

## Envío privado opcional desde v1.5.0

Las evidencias pueden enviarse a un proyecto Supabase propio con usuarios autorizados y copia local. La activación requiere configurar ese proyecto y comprobar el primer envío real. [Guía de acceso, permisos y reintentos](KSP_NUBE.md). La subida privada no publica ni modifica esta bitácora automáticamente.

## Captura automática desde v1.4.0

El conector guarda sesiones únicas en `ksp-sessions/` y el mapa permite descargar evidencias, recuperar sesiones del navegador y distinguir datos reales/demo/offline. Consulta [KSP_TRAVESIA.md](KSP_TRAVESIA.md) para límites y archivos incluidos. Recoge `KSP.log` y `Player.log` por separado antes de reiniciar: no se copian automáticamente.

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
| 2026-11-01 | FULLY4425 (asistida por IA) | `cbdc7ce` (v1.1.0) y `154cbff` (v1.2.0) | Mapa nativo en Duna · rumbo v1.2.0 · SCANsat 21.1 | Parcial; guía y recálculo correctos, destino no alcanzado | [Leer sesión](#2026-11-01--fully4425--mapa-nativo-en-duna-y-conector-v120) |
| 2026-11-01 | FULLY4425 (asistida por IA) | `8b63480` (v1.3.1) | Satélite SCANsat en Duna · CSV real importado al mapa | Funcionó; importación y ruta sobre alturas SCANsat reales | [Leer sesión](#2026-11-01--fully4425--mapa-scansat-real-de-duna) |
| 2026-11-01 | FULLY4425 (asistida por IA) | `2cb6daa` (v1.4.0) | Travesía: rover sobre mapa SCANsat, llegada, paso de largo, desconexión, voz y rendimiento | Parcial; llegada y paso de largo correctos, recuperación requiere reimportar el mapa, voz audible confirmada por el usuario | [Leer sesión](#2026-11-01--fully4425--travesía-v140-sobre-mapa-scansat) |
| 2026-11-02 | FULLY4425 (conducción del usuario; registro asistido por IA) | `b83dcae` (v1.7.2) | Duna Explorador en Firefox: conector local, mapa SCANsat importado, travesía de ~14 km, diagnóstico del PC | Parcial; conexión, rutas y diagnóstico correctos; sin llegada confirmada (mínimo 152 m del destino a 21,7 m/s) | [Leer sesión](#2026-11-02--fully4425--duna-explorador-v172-en-firefox) |

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

## 2026-11-01 · FULLY4425 · Mapa nativo en Duna y conector v1.2.0

> Registro preparado por una IA (Claude) que manejó el juego con teclado y ratón
> en el equipo de FULLY4425, con su autorización. La aplicación y el conector
> solo leyeron datos; no se enviaron mandos por kRPC. Es la continuación de la
> sesión anterior de esta tabla (HUD en Kerbin), que se deja sin cambios.

### Sesión y entorno

- Colaborador / usuario de GitHub: FULLY4425; pruebas ejecutadas por Claude (IA).
- Fecha, hora y zona horaria: 2026-11-01, 17:05–18:13, hora central de México (UTC−6).
- Aplicación: versión y commit probado: mapa nativo con `cbdc7ce` (v1.1.0 «Horizonte KSP»); comprobación de rumbo con `154cbff` (v1.2.0 «Atlas KSP»).
- KSP: versión y distribución: KSP 1.12.5, Steam.
- kRPC: versión del mod y del cliente Python: mod kRPC 0.7.0; cliente `krpc==0.7.0`.
- Python / sistema operativo / navegador: Python 3.13.17 / Windows 10 Pro 19045 / navegador integrado de la app de escritorio de Claude.
- Equipo: CPU, RAM y GPU: Intel Core i5-11400H, 23,7 GB de RAM, NVIDIA GeForce RTX 3050 Laptop GPU (más Intel UHD).
- Mods relevantes y versiones (o stock): kRPC 0.7.0; SCANsat 21.1 (instalado en esta sesión); ModuleManager 4.2.3; además BDArmory, DarkMultiPlayer, EnvironmentalVisualEnhancements, Scatterer, Near Future (Electrical/Propulsion), TweakScale, SystemHeat, CryoTanks, B9PartSwitch, KSP-Recall y otros.
- Área probada: mapa nativo / HUD con KSP / mapas importados / conector: mapa nativo y conector.
- Cuerpo, ubicación y vehículo o astronauta: Duna, rover Crater Crawler (lat −0,049°, lon −74,725°, 5345 m).
- Duración aproximada de la sesión: unos 70 min de pruebas con el mapa y el conector.
- Resultado general: funcionó / parcial / bloqueado: parcial.
- Confirmación: esta experiencia corresponde a una prueba con KSP real: sí.

### Configuración y preparación

- Conector: `.venv\Scripts\python.exe -u integrations/ksp_server.py` en el clon del
  repositorio, en `127.0.0.1:7173`. kRPC en 127.0.0.1, RPC 50000, stream 50001.
  Primero hubo que detener un conector antiguo de otra carpeta que ocupaba el
  puerto 7173 y no tenía las rutas del mapa nativo.
- Mapa: `http://localhost:7173/ksp-map.html` → **Conectar KSP local** → muestreo
  33 × 33 a 25 m (800 m de ancho).
- Destinos: "Base Duna Este" (−0,0489°, −74,6714°) con pendiente 15°, y después
  "Llanura Sureste" (−0,07576°, −74,6893°) con pendiente 20°. La velocidad de
  estimación era de 2 m/s y "Evitar agua" estaba activado.
- Voz activada (Microsoft Helena, es-ES).
- Conducción con el teclado de KSP: `W`/`S`, `A`/`D`, trim `Alt+A`/`Alt+D` y el
  icono del grupo de frenos.

### Pasos de la prueba

1. Conectar el mapa nativo con el rover en Duna y muestrear la región.
2. Calcular una ruta con pendiente máxima de 15° y, después, con 20°.
3. Conducir hacia el destino observando el aviso, la distancia y la voz.
4. Desviarse y salir de la región muestreada.
5. Actualizar a v1.2.0, reiniciar el conector y comparar el rumbo con la navball.
6. Instalar SCANsat 21.1, reiniciar KSP y comprobar en `KSP.log` que carga.

### Resultado esperado

Ruta sobre las alturas reales de Duna, distancia decreciente al conducir,
recálculo al desviarse conservando el destino, aviso al salir de la región, y
rumbo del conector igual al de la navball en v1.2.0.

### Resultado observado y experiencia de uso

- **Muestreo:** 1089 alturas reales (5216–5486 m) en unos 12 s.
- **Planificación:**
  - Con 15° el mapa respondió "Sin paso entre Vehículo actual y Base Duna Este…",
    lo que es coherente porque todo el entorno tenía 15–20° de pendiente.
  - Con 20° calculó 262 m, +2,7 m de subida y ~3 min a 2 m/s.
- **Guía:** la distancia bajó de 265 a 45 m durante la conducción, y la voz
  anunció la indicación.
- **Destino no alcanzado (fallo de conducción, no del mapa):** el rover aceleró
  cuesta abajo hasta ~15 m/s y pasó de largo. El mapa mostró "Desvío
  detectado. Recalculando en el terreno KSP…" y "Ruta KSP recalculada desde el
  vehículo; destinos pendientes conservados", y la voz dijo "Recalculando ruta
  KSP." / "Ruta KSP calculada.". Al soltar `W` en pendiente, el rover rodaba
  hacia atrás.
- **Salida de la región:** a ~740 m del destino, el mapa mostró "Vehículo fuera de
  la región muestreada. Carga una región que incluya el vehículo y sus destinos.".
- **Panel del navegador oculto:** con el panel oculto, la página mostró durante un
  momento "Telemetría perdida. Guía en pausa…" y se recuperó sola al volver a
  consultarla.
- **Rumbo con v1.1.0:** el campo de rumbo no coincidía con la navball (p. ej., 130°
  mostrados frente a ~105° de trayectoria real).
- **Rumbo con v1.2.0:** el conector dio 284,3° y la navball 284°. El método anterior
  (`body.reference_frame`) habría dado 301°.
- **SCANsat 21.1:** cargó sin excepciones propias y con 20 piezas. Con él se
  construyó y guardó en el VAB un satélite de altimetría para Duna, sin lanzarlo
  aún.

### Comprobaciones

| Comprobación | Resultado | Observaciones / evidencia |
| --- | --- | --- |
| Conexión y reconexión kRPC | Correcto | Conexión con v1.1.0 y de nuevo tras reiniciar el conector con v1.2.0 ([api-ksp-v1.2.0.json](ksp-logs/2026-11-01-FULLY4425/api-ksp-v1.2.0.json)). |
| Posición y cuerpo correctos | Correcto | Duna, Crater Crawler; las coordenadas cambiaban de forma coherente con la conducción. |
| Rumbo frente a la navball | Correcto (v1.2.0) | 284,3° frente a 284° ([navball-rumbo-284.jpg](ksp-logs/2026-11-01-FULLY4425/navball-rumbo-284.jpg)). Con v1.1.0 falló, como ya se sabía. |
| Muestreo de alturas | Correcto | 33 × 33 a 25 m, 1089 alturas en ~12 s. |
| Destinos y cálculo de ruta | Correcto | "Sin paso" con 15°; ruta de 262 m con 20°. |
| Recálculo al desviarse | Correcto | Varios recálculos desde el vehículo conservando el destino ([registro](ksp-logs/2026-11-01-FULLY4425/registro-mapa-nativo-duna.txt)). |
| Pausa por desconexión / salida de región | Correcto | "Vehículo fuera de la región muestreada…". No se probó la desconexión del juego con la guía activa. |
| Indicaciones y voz | Correcto | Aviso y distancia coherentes; llamadas de voz registradas. No se escuchó el audio. |
| Importación / exportación de mapas | No probado | SCANsat instalado, pero sin escaneo ni exportación todavía. |
| Fluidez y consumo de recursos | No probado | No se midieron FPS ni consumo. |

### Logs y evidencias

- Log KSP: [ksp-log-scansat-vab.zip](ksp-logs/2026-11-01-FULLY4425/ksp-log-scansat-vab.zip)
  contiene el `KSP.log` de la ejecución que empezó a las 17:32 con SCANsat.
  - Líneas 141–142 `[LOG 17:33:01]`: carga de `SCANsat.dll` V21.1.0.
  - Línea 18910 `[LOG 17:35:10]`: fin de la carga.
  - Línea 20526 `[EXC 18:36:43]`: excepción de DynamicBatteryStorage, ajena al proyecto.
  - Las líneas de DarkMultiPlayer sobre `godarklight.privatedns.org` son de ese mod.
- Log de la ejecución con la conducción: [ksp-player-prev-duna.zip](ksp-logs/2026-11-01-FULLY4425/ksp-player-prev-duna.zip)
  contiene el `Player-prev.log` de Unity (ejecución de 16:59 a 17:32). Es parcial:
  Unity lo dejó relleno de bytes nulos y solo conserva parte del texto.
- Log del conector: el registro original menciona `conector-v1.2.0.log` (17:24–17:30), pero el archivo no se incluyó en los adjuntos del repositorio. **Evidencia pendiente de aportar**; se retira el enlace inexistente sin reconstruir ni inventar ese log.
- Errores de navegador: no se registraron errores de consola.
- Misión / mapa: [registro-mapa-nativo-duna.txt](ksp-logs/2026-11-01-FULLY4425/registro-mapa-nativo-duna.txt)
  recoge los textos del mapa y la voz con hora, coordenadas y destinos. Es una
  transcripción de lo leído en la página, no un log generado por la aplicación.
  No se exportó la misión.
- Capturas / video: [navball-rumbo-284.jpg](ksp-logs/2026-11-01-FULLY4425/navball-rumbo-284.jpg).
- Evidencias que faltan y motivo:
  - El `KSP.log` y el log del conector de la conducción (v1.1.0) se sobrescribieron
    al reiniciar KSP y el conector.
  - No se guardó `/api/ksp/terrain` ni la misión exportada antes de reiniciar.
  - Las capturas completas incluían el escritorio del usuario y no se publican.

### Errores encontrados

1. **Doble punto en el mensaje de "Sin paso".** Dice "…agua y cobertura.. No
   sigas…". Sale siempre que no hay ruta; es solo un detalle de texto.
2. **Rumbo del mapa en v1.1.0.** No coincidía con la navball. Ya está corregido en
   v1.2.0 y verificado en esta sesión.

### Mejoras y sugerencias

- **Elegir destinos según la pendiente** (prioridad media). Hoy hay que adivinar un
  destino accesible. Se podría colorear la pendiente máxima por celda en el mapa
  2D, o indicar qué zonas cumplen el límite elegido.
- **Aviso de velocidad cuesta abajo** (prioridad baja). En Duna el rover se pasa
  del destino con facilidad. Se podría avisar "reduce velocidad" cuando la
  velocidad supere la de estimación cerca del destino.

### Seguimiento

- Pendientes:
  - Llegar y detenerse en el destino.
  - Probar la desconexión del juego con la guía activa.
  - Escanear Duna con SCANsat, exportar el CSV, convertirlo con
    `scripts/import-scansat.py` y planificar sobre él.
  - Medir la fluidez.
- Respuesta o revisión de otro colaborador: pendiente.
- Nueva versión probada y resultado: v1.2.0; rumbo correcto frente a la navball.
- Estado: en revisión.


## 2026-11-01 · FULLY4425 · Mapa SCANsat real de Duna

> Registro preparado por una IA (Claude) en el equipo de FULLY4425. La IA no envió mandos al satélite: solo leyó datos por kRPC y usó las ventanas de SCANsat. La maniobra que subió el periapsis la hizo el usuario.

### Sesión y entorno

- Colaborador / usuario de GitHub: FULLY4425; pruebas ejecutadas por Claude (IA).
- Fecha, hora y zona horaria: 2026-11-01, 18:54–19:10, UTC−6.
- Aplicación: versión y commit probado: `8b63480` (v1.3.1).
- KSP: versión y distribución: KSP 1.12.5, Steam.
- kRPC: versión del mod y del cliente Python: 0.7.0 / `krpc==0.7.0`.
- Python / sistema operativo / navegador: Python 3.13.17 / Windows 10 Pro / navegador integrado de la app de Claude.
- Equipo: CPU, RAM y GPU: i5-11400H, 23,7 GB de RAM, RTX 3050 Laptop.
- Mods relevantes y versiones (o stock): SCANsat 21.1, kRPC 0.7.0 y los mismos mods de la sesión anterior.
- Área probada: mapa nativo / HUD con KSP / mapas importados / conector: mapas importados (SCANsat) y conector.
- Cuerpo, ubicación y vehículo o astronauta: Duna; satélite "Nave Espacial Sin Nombre" (SAR-X + R-3B) en órbita 337 × 31 km, i = 72°.
- Duración aproximada de la sesión: unos 16 min.
- Resultado general: funcionó / parcial / bloqueado: funcionó.
- Confirmación: esta experiencia corresponde a una prueba con KSP real: sí.

### Configuración y preparación

- **SCANsat:** "Export .csv Data File" activado y ancho de 1280 px. Con 4096 px el mapa grande no cabía en la ventana y no se podía exportar.
- **Exportación:** Big Map con el cuerpo Duna y el tipo Altimetry. El archivo salió a 1126 × 563.
- **Conversión:**

  ```bash
  python scripts/import-scansat.py duna.csv --output duna-region.json --body Duna --radius 320000 --lat -13.268 --lon -133.961 --size 17 --cell 2000
  ```

  Se eligió un centro con cobertura completa.

### Pasos de la prueba

1. Comprobar el escáner y la órbita por kRPC. Escanear con aceleración de tiempo de 50× hasta el periapsis.
2. Exportar el CSV de altimetría de Duna.
3. Convertir una región, validarla con `/api/ksp/maps/validate` y cargarla en `ksp-map.html`.
4. Planificar una ruta sobre esas alturas y probar "Conectar KSP usando este mapa".

### Resultado esperado

Importar alturas reales de SCANsat y planificar sobre ellas sin inventar huecos.

### Resultado observado y experiencia de uso

- **Escaneo:** el SAR-X estaba en estado "Ideal" y el R-3B en "Muy Alto". La cobertura pasó del 0,1 % al 3,0 %.
- **Paso por la atmósfera:** el satélite cruzó el periapsis de 31 km con un 46 % de calor como máximo. La apoapsis bajó de 370 a 337 km.
- **CSV exportado:** 32 492 filas con la cabecera esperada (`Row,Column,Lat,Long,Height`) y 31 794 alturas reales (0–8214 m).
- **Conversión:** 280 de 289 celdas con datos (2210–3238 m), fuente `SCANsat-CSV`.
- **Importación en el mapa:** mostró "Instantánea importada: 280/289 alturas…".
- **Ruta:** de 11 314 m, +153 m y ~95 min a 2 m/s.
- **Conexión con el juego:** reconoció Duna y el satélite. El aviso de ruta se ocultó sin ningún mensaje que explicara que el vehículo estaba en órbita y fuera de la región.

### Comprobaciones

| Comprobación | Resultado | Observaciones / evidencia |
| --- | --- | --- |
| Conexión y reconexión kRPC | Correcto | Lecturas del satélite y "Conectar KSP usando este mapa". |
| Posición y cuerpo correctos | Correcto | Duna; 11,43°, −128,58°, 325 km. |
| Rumbo frente a la navball | No probado | |
| Muestreo de alturas | No aplica | Alturas de SCANsat, no de kRPC. |
| Destinos y cálculo de ruta | Correcto | [mision-ruta-scansat.json](ksp-logs/2026-11-01-FULLY4425-scansat/mision-ruta-scansat.json) |
| Recálculo al desviarse | No probado | No había un rover en la región. |
| Pausa por desconexión / salida de región | Parcial | La guía se ocultó, pero sin mensaje explicativo. |
| Indicaciones y voz | No probado | |
| Importación / exportación de mapas | Correcto | CSV real → JSON → mapa ([región](ksp-logs/2026-11-01-FULLY4425-scansat/duna-region-scansat.json)). |
| Fluidez y consumo de recursos | No probado | |

### Logs y evidencias

- **Exportación de SCANsat:** [player-log-exportacion.zip](ksp-logs/2026-11-01-FULLY4425-scansat/player-log-exportacion.zip). Las líneas 373–374 confirman la exportación del CSV.
- **KSP.log:** [ksp-log-satelite.zip](ksp-logs/2026-11-01-FULLY4425-scansat/ksp-log-satelite.zip). KSP solo lo había escrito hasta las 19:05, así que no recoge la exportación.
- **Datos de SCANsat:** [scansat-duna-csv.zip](ksp-logs/2026-11-01-FULLY4425-scansat/scansat-duna-csv.zip) y [scansat-duna-altimetria-1126x563.png](ksp-logs/2026-11-01-FULLY4425-scansat/scansat-duna-altimetria-1126x563.png).
- **Lecturas del satélite, el paso y la conversión:** [satelite-y-escaneo.txt](ksp-logs/2026-11-01-FULLY4425-scansat/satelite-y-escaneo.txt).
- **Errores de navegador:** no se registraron.
- **Capturas:** no se publican porque incluían el escritorio del usuario.

### Errores encontrados

1. **"Map Width" redimensiona el mapa grande.** Con 4096 px el mapa grande de SCANsat se hace más grande que la ventana y no se puede exportar. Ocurre siempre con anchos mayores que la ventana, y obliga a exportar a menor resolución.
2. **Falta un mensaje al conectar un vehículo en órbita.** Al conectar un vehículo en órbita y fuera de la región, la guía se oculta sin explicar por qué. Ocurrió una vez; el impacto es bajo.
3. **Texto de kRPC con un mapa de SCANsat.** Con un mapa SCANsat cargado sigue apareciendo "Relieve leído de kRPC…". Es solo un problema de texto.

### Mejoras y sugerencias

- **Aviso de ancho en la guía** (prioridad media). Indicar en la guía de SCANsat que el ancho de exportación también cambia el tamaño del mapa grande.
- **Mensaje explícito al conectar** (prioridad baja). Mostrar "Vehículo en órbita / fuera de la región" al conectar con un mapa importado.

### Seguimiento

- Pendientes:
  - Exportar a más resolución, con una ventana más grande.
  - Conducir un rover dentro de una región importada de SCANsat.
- Respuesta o revisión de otro colaborador: pendiente.
- Nueva versión probada y resultado: —
- Estado: en revisión.

## 2026-11-01 · FULLY4425 · Travesía v1.4.0 sobre mapa SCANsat

> Registro preparado por una IA (Claude) que condujo el rover con teclado y ratón en el equipo de FULLY4425. kRPC solo se usó para leer datos. Entre 21:16 y 21:33 el usuario también manejó el rover y la página; ese tramo se describe, pero no cuenta como resultado.

### Sesión y entorno

- Colaborador / usuario de GitHub: FULLY4425; pruebas ejecutadas por Claude (IA).
- Fecha, hora y zona horaria: 2026-11-01, 20:59–21:45, UTC−6.
- Aplicación: versión y commit probado: v1.4.0 `2cb6daa`. Durante la prueba se publicó v1.5.0 (`56f3726`), que no se probó.
- KSP: versión y distribución: KSP 1.12.5, Steam.
- kRPC: versión del mod y del cliente Python: 0.7.0 / `krpc==0.7.0`.
- Python / sistema operativo / navegador: 3.13.17 / Windows 10 Pro / navegador integrado de la app de Claude.
- Equipo: CPU, RAM y GPU: i5-11400H (12 hilos), 23,7 GB de RAM, RTX 3050 Laptop.
- Mods relevantes y versiones (o stock): SCANsat 21.1, kRPC 0.7.0 y los de las sesiones anteriores.
- Área probada: mapa nativo / HUD con KSP / mapas importados / conector: mapa nativo con mapa SCANsat importado y conector.
- Cuerpo, ubicación y vehículo o astronauta: Duna; rover Crater Crawler (de −0,16° −74,79° a 2,07° −73,95°). Satélite SCANsat en órbita 352 × 235 km.
- Duración aproximada de la sesión: 45 min.
- Resultado general: funcionó / parcial / bloqueado: parcial.
- Confirmación: esta experiencia corresponde a una prueba con KSP real: sí.

### Configuración y preparación

- **Conector:** `.venv\Scripts\python.exe -u integrations/ksp_server.py` (v1.4.0). Al reiniciar KSP, el usuario tuvo que pulsar **Start server** en kRPC.
- **Mapa SCANsat:** CSV exportado por el usuario a las 19:19, de 1126 × 563 y con el 83,5 % de los píxeles. El mapa grande de SCANsat medía 2276 px y no cabía en pantalla, así que no se pudo exportar de nuevo.
- **Regiones:** `scripts/import-scansat.py` con 17 × 17 celdas de 2000 m, centradas en el rover. Hubo dos regiones de 289/289 celdas.
- **Avisos:** umbral de 5 m/s, anticipación de 6 s, radio de llegada de 8 m. Pendiente máxima de 20°.

### Pasos de la prueba

1. Actualizar a v1.4.0 y ejecutar las pruebas: 35 de Python y 28 de Node aprobadas.
2. Pasar al rover, importar la región SCANsat y "Conectar KSP usando este mapa".
3. Conducir hacia distintos destinos: paso de largo, aviso de velocidad, llegada y parada.
4. Detener el conector 20 s, reiniciarlo y observar la recuperación.
5. Probar la voz y medir el rendimiento.

### Resultado esperado

- **Llegada:** solo con proximidad física (≤ 8 m) y parada continua de 3 s; si se pasa, "Destino sobrepasado".
- **Desconexión:** pausa y recuperación con datos frescos.
- **Voz:** el estado de la voz indica cuándo habla.

### Resultado observado y experiencia de uso

- **Llegada (correcto):**
  - 21:41:00, a 7,9 m y 0,3 m/s: "Dentro del radio: detente para confirmar llegada (3 s)."
  - 21:41:03, a 0,0 m/s: "Destino alcanzado y vehículo detenido.", también por voz.
- **Paso de largo (correcto):**
  - 21:13:14, al pasar a 9 m: "Destino sobrepasado. Reduce velocidad y revisa la nueva ruta.", también por voz.
  - Se repitió en otros pasos.
- **Aviso de velocidad (correcto):**
  - "Reduce velocidad: 8.5 m/s; destino próximo." a unos 20 m del destino.
  - "Reduce velocidad: 5.0 m/s; destino próximo." más tarde.
- **Vista oculta (correcto):** "Vista oculta: guía pausada. Se comprobará la conexión al volver."; la guía continuó al mostrarla de nuevo.
- **Desconexión (parcial):**
  - 21:41:46, al detener el conector: "Sin conexión al juego: Failed to fetch…".
  - Al reiniciarlo: "KSP 1 conectado…" y "La conexión kRPC cambió. Vuelve a muestrear la región."
  - Con el mapa SCANsat importado, "Conectar KSP usando este mapa" no reactivó la guía. Hubo que volver a importar el JSON; después volvió a confirmar la llegada a las 21:43:02.
- **Destino en la misma celda de 2 km:** la ruta sale "0 m" y el banner de ruta queda oculto; sí se actualizan la distancia física y la llegada.
- **Conducción en pendientes de Duna:** con los frenos activados el rover se desliza a unos 0,9 m/s en pendientes de 13–16°. En esas zonas no puede cumplir la parada de 3 s; hizo falta ir a una zona de unos 4°.

### Comprobaciones

| Comprobación | Resultado | Observaciones / evidencia |
| --- | --- | --- |
| Conexión y reconexión kRPC | Correcto | El usuario inició kRPC; el conector se reconectó tras los cambios de escena ([rendimiento](ksp-logs/2026-11-01-FULLY4425-travesia/rendimiento.txt)). |
| Posición y cuerpo correctos | Correcto | Duna, Crater Crawler; distancias coherentes con kRPC. |
| Rumbo frente a la navball | No probado | |
| Muestreo de alturas | No aplica | Se usaron alturas de SCANsat. |
| Destinos y cálculo de ruta | Correcto | 10 misiones en el ZIP del conector. Con destinos en la misma celda la ruta sale "0 m". |
| Recálculo al desviarse | No probado | No hubo desvío real de una ruta con varias celdas. |
| Pausa por desconexión / salida de región | Parcial | Pausa correcta; la recuperación sobre un mapa importado exige reimportarlo. La salida de la región ocurrió en el tramo del usuario y no quedó registrada. |
| Indicaciones y voz | Correcto | El estado mostró "Hablando: …". La IA no puede oír, pero FULLY4425 confirmó después haber oído "Destino alcanzado y vehículo detenido" (Microsoft Helena, es-ES). |
| Importación / exportación de mapas | Correcto | CSV real → JSON → mapa ([región](ksp-logs/2026-11-01-FULLY4425-travesia/duna-rover-scansat-2.json)). Exportar desde SCANsat falló por el tamaño del mapa grande. |
| Fluidez y consumo de recursos | Medido parcialmente | Repintado de 0,74 ms de media; KSP al ~21 % de la CPU y 7,4 GB de RAM; FPS no medidos ([rendimiento](ksp-logs/2026-11-01-FULLY4425-travesia/rendimiento.txt)). |

### Logs y evidencias

- **Cronología con mensajes, voz y distancias:** [registro-travesia.txt](ksp-logs/2026-11-01-FULLY4425-travesia/registro-travesia.txt).
- **ZIP del conector, sesiones 1 y 2:** [conector-sesion-1.zip](ksp-logs/2026-11-01-FULLY4425-travesia/conector-sesion-1.zip) y [conector-sesion-2.zip](ksp-logs/2026-11-01-FULLY4425-travesia/conector-sesion-2.zip). Contienen telemetría, eventos (`browser-arrival` 03:41:04Z), misiones, regiones y `connector.log`. Se sustituyó el usuario de Windows en las rutas.
- **Logs de KSP:**
  - [ksp-log-travesia.zip](ksp-logs/2026-11-01-FULLY4425-travesia/ksp-log-travesia.zip): ejecución desde las 20:54.
  - [player-log-travesia.zip](ksp-logs/2026-11-01-FULLY4425-travesia/player-log-travesia.zip): se sustituyó el nombre de Steam.
- **Datos de SCANsat:**
  - CSV: [scansat-duna-1919-csv.zip](ksp-logs/2026-11-01-FULLY4425-travesia/scansat-duna-1919-csv.zip).
  - Imagen: [scansat-duna-1919-altimetria.png](ksp-logs/2026-11-01-FULLY4425-travesia/scansat-duna-1919-altimetria.png).
  - Regiones: [duna-rover-scansat.json](ksp-logs/2026-11-01-FULLY4425-travesia/duna-rover-scansat.json) y [duna-rover-scansat-2.json](ksp-logs/2026-11-01-FULLY4425-travesia/duna-rover-scansat-2.json).
- **Rendimiento:** [rendimiento.txt](ksp-logs/2026-11-01-FULLY4425-travesia/rendimiento.txt).
- **Errores de navegador:** no se registraron.
- **Evidencias que faltan:**
  - La sesión del navegador de 21:05 se descartó por el límite de 6 sesiones.
  - No se descargó el paquete `ksp-test-session-v1`; las métricas se leyeron directamente de IndexedDB.
  - No se publican capturas porque mostraban el escritorio del usuario.

### Errores encontrados

1. **No se recupera el mapa importado tras reiniciar el conector.** Pasos: mapa SCANsat conectado → conector reiniciado a las 21:42:03. Mensaje: "La conexión kRPC cambió. Vuelve a muestrear la región." Ni "Conectar KSP usando este mapa" ni "Calcular ruta" reactivan la guía; con un mapa importado no hay región kRPC que muestrear. Hubo que volver a importar el JSON. Ocurrió una vez; impacto medio.
2. **Ruta de "0 m" con el destino en la misma celda.** Con celdas de 2000 m, un destino a 1200 m da la métrica "0 m · ~0 min" y oculta el banner de ruta. Ocurre siempre que el destino cae en la celda del vehículo; impacto bajo, porque la distancia física y la llegada siguen funcionando.
3. **"Repetir" no dice nada tras la llegada.** Ocurrió una vez; impacto bajo.
4. **Mapa grande de SCANsat más grande que la ventana (mod SCANsat, no de la aplicación).** Con `BigMapWidth` 2276 y posición −832,69 no se puede mover ni exportar. Volvió a ocurrir.

### Mejoras y sugerencias

- **Botón para reconectar un mapa importado** (prioridad media). Tras un reinicio del conector, ofrecer "Volver a conectar este mapa" en lugar de pedir un nuevo muestreo cuando la fuente es SCANsat.
- **Destino en la celda del vehículo** (prioridad baja). Indicar "destino en la celda actual" en lugar de "0 m".
- **Rover que se desliza** (prioridad baja). Avisar cuando un vehículo con frenos sigue moviéndose y no puede confirmar la llegada.

### Seguimiento

- Pendientes:
  - Medir los FPS de KSP.
  - Probar el recálculo al desviarse de una ruta de varias celdas.
  - Comprobar la salida de la región con registro.
  - Comprobar el rumbo frente a la navball en v1.4.0.
  - Probar v1.5.0.
- Respuesta o revisión de otro colaborador: pendiente.
- Nueva versión probada y resultado: v1.4.0 (este registro).
- Estado: en revisión.

## 2026-11-02 · FULLY4425 · Duna Explorador v1.7.2 en Firefox

> El usuario condujo el rover. Claude (IA) ayudó a instalar v1.7.2, arrancar el conector y abrir el mapa en Firefox, y después reconstruyó este registro desde la carpeta de evidencias del conector. La IA no vio la pantalla mientras se conducía, así que no hay lecturas de textos en pantalla ni de la voz. kRPC solo se usó para leer datos.

### Sesión y entorno

- Colaborador / usuario de GitHub: FULLY4425.
- Fecha, hora y zona horaria: 2026-11-02, 14:09–16:50, UTC−6. Conducción entre 14:53 y 15:47.
- Aplicación: versión y commit probado: v1.7.2 `b83dcae`.
- KSP: versión y distribución: KSP 1.12.5, Steam.
- kRPC: versión del mod y del cliente Python: 0.7.0 / `krpc==0.7.0`; `psutil` 7.0.0.
- Python / sistema operativo / navegador: 3.13 / Windows 10 Pro / Firefox.
- Equipo: CPU, RAM y GPU: i5-11400H (12 hilos), 23,7 GB de RAM, RTX 3050 Laptop.
- Mods relevantes y versiones (o stock): SCANsat 21.1, kRPC 0.7.0.
- Área probada: mapa nativo / HUD con KSP / mapas importados / conector: mapa nativo con mapa SCANsat importado, conector y diagnóstico del PC.
- Cuerpo, ubicación y vehículo o astronauta: Duna; rover Crater Crawler. Dos satélites SCANsat llamados "Nave Espacial Sin Nombre": uno en órbita polar de 328,6 × 269,0 km (i 88,47°) y el anterior, de 352,4 × 235,3 km (i 72,24°).
- Duración aproximada de la sesión: 2 h 40 min (55 min de conducción).
- Resultado general: funcionó / parcial / bloqueado: parcial.
- Confirmación: esta experiencia corresponde a una prueba con KSP real: sí.

### Configuración y preparación

- **Conector:** `.venv\Scripts\python.exe -u integrations/ksp_server.py` desde el clon git (v1.7.2), con `psutil` para el diagnóstico del PC. Hubo que pulsar **Start server** en kRPC.
- **Firefox:** primero se abrió la URL de Render (`lobos-espaciales-python.onrender.com`). Desde ahí no se llega al conector local. Funcionó con `http://localhost:7173/ksp-map.html`.
- **Mapa:** se cargó `duna-rover-scansat-2.json` de la sesión anterior con "Cargar mapa KSP (.json)". Para abrirlo, la IA copió la ruta al portapapeles y el usuario la pegó en el diálogo de Firefox. Después se generó otra región SCANsat centrada en 2,118°, −73,806°.
- **Rutas:** pendiente máxima de 15°, 2 m/s, evitando agua. Clima de entrenamiento "dust".

### Pasos de la prueba

1. Arrancar el conector v1.7.2 y conectar Firefox en localhost.
2. Pasar al rover y cargar el mapa SCANsat.
3. Añadir destinos, calcular rutas y conducir.
4. Revisar las evidencias del conector (telemetría, misiones, diagnóstico del PC).

### Resultado esperado

- Ruta sobre alturas SCANsat y guía hasta el destino.
- Llegada confirmada solo a ≤ 8 m y con el rover parado 3 s.
- Diagnóstico del PC y del vuelo guardado en la carpeta de la sesión.

### Resultado observado y experiencia de uso

- **Conexión (correcto):**
  - Firefox mostró "connected" a las 14:50:24.
  - Al cambiar de vehículo, la guía mostró "Cambió el vehículo. Revisa los destinos y calcula desde su posición."
  - Durante el cambio de escena, el conector se reconectó 5 veces en 15 s; luego se estabilizó.
- **Primer tramo (14:53–15:25):**
  - Rutas de 15,7 km, 16,8 km y 38,1 km, y un muestreo kRPC de 33 × 33 celdas de 25 m.
  - El rover fue a hasta 55,6 m/s, con varios saltos (situación "flying", pico de 4,4 g). Recorrió unos 24 km y salió de la región.
  - A las 15:26 el rover reapareció en −0,162°, −74,791°, la posición del 2026-11-01 a las 21:04. Probablemente se cargó una partida guardada.
- **Segundo tramo (15:28–15:47):**
  - Ruta de Destino 1 (−0,14, −74,78) a Destino 2 (1,9709, −73,8006): 14 485 m, +867 m de ascenso.
  - Unos 14 km recorridos a una media de 15,8 m/s en movimiento.
  - La distancia de la ruta bajó por escalones de 2 km hasta 0 m.
  - Lo más cerca que pasó de Destino 2 fue 152 m, a 21,7 m/s. Lo más cerca de otro destino añadido después, 12 m, a 14,2 m/s.
  - El rover se detuvo a las 15:46:51 en 2,041°, −73,917°, sin ningún destino dentro de 8 m.
  - No hay evento de llegada. Comportamiento correcto según la regla de llegada.
- **Recálculo por clima:**
  - Con el clima "dust", la ruta se recalculó cada 20 s (motivo `weather`): 55 de las 69 misiones de la sesión.
  - La duración estimada saltaba entre 121, 161 y 242 min con la misma distancia.
- **Diagnóstico del PC (correcto):**
  - `computer.jsonl` con 1915 muestras, y `flight.jsonl` y `analysis.json` con picos y recomendaciones.
  - FPS siempre `null`: kRPC no los ofrece.
- **Cierre:** a las 15:47:03 Firefox registró "NetworkError…" y "Cierre de vista". El conector siguió grabando hasta las 16:50.

### Comprobaciones

| Comprobación | Resultado | Observaciones / evidencia |
| --- | --- | --- |
| Conexión y reconexión kRPC | Correcto | 5 reconexiones en 15 s en cada cambio de vehículo, con `'NoneType' object has no attribute 'orbit'`; luego estable ([registro](ksp-logs/2026-11-02-FULLY4425-v172/registro-v172.txt)). |
| Posición y cuerpo correctos | Correcto | Duna; satélites y rover con sus órbitas y coordenadas. |
| Rumbo frente a la navball | No probado | |
| Muestreo de alturas | Correcto | Muestreo kRPC de 33 × 33 celdas de 25 m a las 15:07. |
| Destinos y cálculo de ruta | Correcto | 69 misiones sobre SCANsat-CSV en el ZIP. Destinos en la misma celda: "0 m" (ya conocido). |
| Recálculo al desviarse | No probado aparte | Los recálculos fueron por clima cada 20 s, no por desvío. |
| Pausa por desconexión / salida de región | Parcial | "Telemetría perdida. Guía en pausa…" en los cambios de vehículo. La salida de la región ocurrió en el primer tramo; no se vio su mensaje en pantalla. |
| Llegada y detención | No alcanzada | Mínimo 152 m de Destino 2 y 12 m de otro destino, siempre a más de 14 m/s. |
| Indicaciones y voz | No observado | La IA no vio la pantalla; v1.7.2 no guarda esos textos como eventos. |
| Importación / exportación de mapas | Correcto | JSON SCANsat cargado en Firefox. |
| Fluidez y consumo de recursos | Medido parcialmente | KSP al ~21 % de la CPU y hasta 7,9 GB; conector 75 MB; repintado de 9,6 ms de media y 173 ms de máximo en Firefox. FPS no disponibles ([rendimiento](ksp-logs/2026-11-02-FULLY4425-v172/rendimiento-v172.txt)). |

### Logs y evidencias

- **Cronología:** [registro-v172.txt](ksp-logs/2026-11-02-FULLY4425-v172/registro-v172.txt).
- **Rendimiento:** [rendimiento-v172.txt](ksp-logs/2026-11-02-FULLY4425-v172/rendimiento-v172.txt).
- **ZIP del conector:** [conector-sesion-v172.zip](ksp-logs/2026-11-02-FULLY4425-v172/conector-sesion-v172.zip). Contiene telemetría, `flight.jsonl`, `computer.jsonl`, `analysis.json`, eventos, 69 misiones, 6 terrenos y `connector.log`. Se sustituyó el usuario de Windows en las rutas.
- **Mapa usado:** [duna-rover-scansat-2.json](ksp-logs/2026-11-01-FULLY4425-travesia/duna-rover-scansat-2.json), de la sesión anterior.
- **Evidencias que faltan:**
  - Capturas de pantalla.
  - Textos de la guía y la voz durante la conducción.
  - Logs de KSP.
  - Paquete de sesión del navegador.

### Errores encontrados

1. **Recálculo cada 20 s por el clima, con duración inestable.** Con el clima "dust", la ruta se recalcula cada 20 s aunque no cambie nada; la duración estimada salta entre 121, 161 y 242 min. Se crean decenas de misiones (55 en 19 min). Impacto bajo o medio: llena la carpeta de evidencias y la ETA no es fiable.
2. **Reconexiones en ráfaga al cambiar de vehículo.** `'NoneType' object has no attribute 'orbit'` mientras KSP cambia de escena; 5 sesiones kRPC nuevas en 15 s. Impacto bajo: se recupera solo.
3. **Ruta de "0 m" con el destino a cientos de metros (ya conocido).** Desde las 15:42, con el rover a unos 600 m o más de Destino 2, la ruta ya marcaba 0 m porque ambos estaban en la misma celda de 2 km.
4. **Repintado más lento que en v1.4.0.** 9,6 ms de media y 173 ms de máximo, frente a 0,74 / 2,3 ms. El navegador es distinto (Firefox) y el atlas es más grande; hace falta compararlo en el mismo navegador.

### Mejoras y sugerencias

- **Recalcular por clima solo cuando cambie el clima** (prioridad media). O, al menos, no guardar una misión nueva si la ruta es idéntica.
- **Guardar en `events.jsonl` los textos de llegada, paso de largo y aviso de velocidad** (prioridad media), para poder verificarlos sin capturas.
- **Avisar cuando el vehículo sale de la región importada** (prioridad baja) y registrarlo como evento.
- **Advertir si se abre la versión de Render con KSP** (prioridad baja): "Esta página no puede llegar a tu conector local; abre localhost:7173".

### Seguimiento

- Pendientes:
  - Confirmar la llegada en v1.7.2 acercándose a menos de 5 m/s.
  - Comprobar la voz y los avisos en Firefox.
  - Comparar el repintado de v1.4.0 y v1.7.2 en el mismo navegador.
  - Medir los FPS de KSP con una herramienta externa.
- Respuesta o revisión de otro colaborador: correcciones revisadas en [v1.7.5](KSP_REVISION_V175.md); validación automatizada, pendiente repetir en KSP/Firefox.
- Nueva versión probada y resultado: v1.7.2 (este registro; no se ha probado v1.7.5 en este PC).
- Estado: en revisión.

## Validaciones registradas y pruebas pendientes

Contenido completo incorporado desde el antiguo `docs/VALIDACION.md` el 2 de noviembre de 2026. Se conserva como antecedente de las comprobaciones del proyecto; las experiencias nuevas de KSP se añaden al registro de sesiones de este mismo documento. Las comprobaciones simuladas y de otros modos siguen identificadas como tales.

Estado documental: **2 de noviembre de 2026**. Este documento recoge comprobaciones realizadas durante el desarrollo; no es una certificación científica, de seguridad, de rendimiento AR ni de compatibilidad de hardware.

### Validación de v1.4.0 «Travesía KSP»

Comprobaciones automatizadas y de navegador, no una sesión de juego real: avisos anticipados a 15 m/s, llegada física tras detenerse 3 s, ZIP de evidencias, guardado y recuperación del navegador, pausa al ocultar, desconexión real simulada y recuperación, recarga de región con destino conservado e interfaz compacta. Se probaron límites de disco, errores de almacenamiento y colas de voz con un motor simulado. No se afirma haber escuchado audio ni conducido esta versión dentro de KSP.

Se mantiene pendiente: completar llegada con rover real, desconexión con guía activa, conducción sobre el mapa importado de SCANsat, voz audible y medidas de rendimiento de juego/hardware. La comparación real del rumbo de v1.2.0 y el flujo SCANsat real de v1.3.1 sí quedaron registrados en las sesiones anteriores. El CSV archivado se convierte de nuevo y reproduce sus alturas y ruta en las pruebas automatizadas de v1.4.0.

### Validación de v1.5.0 «Evidencias KSP»

Pruebas con servicio simulado: cola duradera tras reinicio, pérdida de red, fallo del índice, reintentos idempotentes, pausa persistente, aislamiento entre identidades locales, autenticación/renovación, límites de logs y exclusión de archivos privados. En navegador se comprobaron controles y estado sin exponer tokens. El proyecto Supabase real aún no está creado: quedan pendientes la aplicación y verificación de RLS y el primer envío contra esa cuenta.

### Validación de v1.6.0 «Atlas de relieve»

Pruebas automatizadas de capas, proyección equirectangular/local, cruce de longitud, rechazo de otro cuerpo/radio, curvas de los triángulos reales sin rellenar huecos y máscaras de cobertura SCANsat. El catálogo integra las dos regiones y el mapa de 529220 píxeles de la sesión Travesía recién sincronizada, además del mapa anterior.

En Chromium: página principal con capas de Marte, mapa KSP integrado, carga de catálogo/texturas reales archivadas, 2D/3D, escala vertical/malla/norte, pausa al cambiar de espacio y vista de 390 px. Con telemetría simulada se comprueban seguimiento/centrado, invariancia de métricas al cambiar la escala visual, avisos, llegada detenida, evidencias, pérdida/recuperación e importación. Las nuevas comprobaciones de la interfaz no equivalen a conducir v1.6.0 en el juego. Las pruebas reales de v1.4.0 figuran arriba con sus propios resultados y pendientes. [Uso y fuentes](KSP_MAPAS_3D.md).

Estado de Supabase actualizado: el propietario indicó que creó el proyecto. La aplicación/verificación de SQL/RLS y el primer envío real no se han comprobado desde este entorno.

### Validación de v1.7.0 «Duna Explorador»

Comprobaciones de datos: PNG completo idéntico al original por SHA-256, 529220 alturas preservadas y huecos desconocidos, proyección global/local y coordenadas esféricas. Pruebas de restricciones meteorológicas hipotéticas, desvío de rutas y rechazo de destino dentro de la tormenta sin alterar el terreno. Chromium: atlas/globo completos, selección y apertura de región, objetivos documentados, textura/alturas/mezcla, cámaras, ensayo virtual, HUD y alternativa WebXR no disponible. Se mantienen pruebas de conexión, evidencias, pérdida/recuperación y funciones de Marte. No constituye una prueba de esta versión en KSP real ni en un dispositivo AR físico. [Guía](DUNA_EXPLORADOR.md).

### Validación de v1.7.1 «Evidencias de Duna»

Diagnóstico Supabase probado con respuestas simuladas: comprobaciones independientes de autenticación, autorización, esquema y Storage; sin subida ni lectura de cuerpos de evidencias y sin tokens en el informe. Se incorpora el proyecto existente a la guía y se añade SQL de verificación. La estructura remota ya se aplicó y pasó nueve verificaciones. Se comprobó el aislamiento con roles reales en una transacción revertida, sin dejar usuarios ni sesiones de prueba; el propietario autorizó su rol de administrador de evidencias. La API deniega acceso anónimo. `configure-project` configura el PC sin crear tokens ni iniciar sesión automáticamente. Sigue pendiente el primer envío real de un ZIP desde el conector.

### Validación de v1.7.2 «Telemetría de misión»

Pruebas con datos simulados: lecturas de vuelo opcionales/valores ausentes, lista permitida de procesos, primera medición CPU sin inventar cero, ausencia de identificadores/comandos personales, resumen de tendencias y ZIP con archivos de diagnóstico. Cierre real de un hilo de envío con cliente simulado, respeto de pausa y persistencia ante pérdida de red. En Chromium: CPU/RAM, vuelo, resumen y petición de envío al cerrar/ocultar. Se aplicaron y verificaron las columnas privadas de resumen en Supabase. No son mediciones del PC real del propietario ni un primer envío de juego confirmado. [Guía](KSP_DIAGNOSTICO.md).

### Validación de v1.7.3 «Permiso para compartir»

Decisiones de diálogo simuladas: aceptación explícita, rechazo, cierre, ausencia de interfaz y destino distinto. Se comprobó que no se autentica/sube/encola sin permiso, que reanudar no lo concede, que retirar bloquea el índice después de una petición en curso y que las sesiones revocadas no se reintentan. Chromium: indicador y retirada; proceso real sin escritorio/entrada: denegación y rechazo HTTP de reanudar. Falta revisar visualmente el aviso en Windows real. La autorización Supabase de los probadores sigue siendo independiente. [Guía](KSP_CONSENTIMIENTO.md).

### Pruebas automatizadas incluidas

| Suite | Último resultado registrado | Cobertura |
| --- | --- | --- |
| `python3 -m unittest discover -s test -v` | 74 pruebas aprobadas. | Planificación, obstáculos, esquinas, pendientes, datos reales, entradas y objetivos propios; contrato/frescura de telemetría y lecturas con cliente kRPC simulado; archivos de mapa, conversión SCANsat, huecos, procedencia, marco de rumbo y registro de sesiones/límites/fallos de disco. |
| `node test/directions.test.js` | 6 pruebas aprobadas. | Derecha/izquierda, ruta recta, agrupación de zigzags, objetivos intermedios, distancia 3D, rutas vacías y media vuelta. |
| `node test/ar-tracking.test.js` | 5 pruebas aprobadas. | Proyección relativa, radio del cuerpo, cruce de longitud, cambio de vehículo/cuerpo, rotación de calibración y distancia a la ruta. |
| `node test/replanning.test.js` | 4 pruebas aprobadas. | Paradas pendientes, nueva salida, rechazo fuera del mapa, progreso físico y origen KSP conservado. |
| `node test/ksp-geo.test.js` | 3 pruebas aprobadas. | Proyección nativa, altas latitudes, cruce de longitud y destinos con coordenadas de malla. |
| `node test/ksp-guidance.test.js` | 10 pruebas aprobadas. | Conectividad, agua/esquinas, avisos anticipados, llegada/parada, paso de largo, cola y caducidad de voz, sesiones y errores. |
| `node test/terrain-style.test.js` | 8 pruebas aprobadas. | Paleta/curvas, huecos, proyecciones, cuerpo/radio, límites geográficos y cobertura del CSV real. |
| `node test/ksp-global.test.js` | 4 pruebas aprobadas. | Escaneo completo, huecos, coordenadas esféricas, regiones seleccionadas y restricciones de tormenta. |

Total registrado: **114 pruebas**. No se necesita Node.js para ejecutar el servidor; es una herramienta opcional de desarrollo. Los comandos y la arquitectura están en [DESARROLLO.md](DESARROLLO.md).

### Comprobaciones de navegador realizadas

Se utilizó Chromium con Playwright como herramienta temporal. Los scripts históricos fueron temporales. Desde v1.7.0, `python3 scripts/check_duna_browser.py` reproduce la comprobación del explorador de Duna con Playwright y Chromium como herramientas opcionales.

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

CSV de prueba con el formato del exportador SCANsat 21.1: importación, huecos bloqueados, rechazo de columnas ambiguas y números no finitos, y conservación de coordenadas/alturas. En Chromium se comprobaron carga, salida manual, planificación, relieve 3D, descarga/reimportación, pérdida de conector y tamaño compacto sin errores JavaScript. Se repitió el flujo del conector con cuerpo y telemetría simulados. Ese registro inicial usó datos de prueba; la sesión posterior de SCANsat real, incluida arriba, completa el flujo de exportación e importación.

### Pruebas reales de KSP registradas en la bitácora

El registro de conexión y conducción del rover Crater Crawler con KSP 1.12.5 se trasladó a la [bitácora de colaboradores](KSP_COLABORADORES.md#2026-11-01--prueba-real-del-hud-ksp-1125). Allí se conservan el entorno, pasos, mediciones, incidencias y pendientes originales. Las nuevas experiencias con el juego se añaden en esa misma bitácora.

### Distribución y servicio público

`python3 scripts/build.py` ha generado correctamente la aplicación ejecutable, incluyendo las pantallas KSP y AR y el conector opcional. La salida es una aplicación Python, no un sitio que pueda planificar rutas con alojamiento exclusivamente estático.

Se verificaron en Render los recursos publicados y respuestas HTTP de salud, planificación y exportación, incluyendo puntos personalizados. La aplicación pública es un prototipo; no sustituye las pruebas físicas que faltan.

Las capturas del README documentan la interfaz web. Una captura o emulación de pantalla no acredita uso en un visor físico.

### Pendiente de validar

| Área | Falta por comprobar |
| --- | --- |
| KSP real | Pruebas parciales de versiones previas en Kerbin y Duna registradas arriba; rumbo v1.2.0 contrastado con la navball. Falta repetir con v1.4.0, confirmar llegada y detención, desconexión con guía activa, sesiones largas, audio y conducción sobre el mapa importado de SCANsat. |
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
