# v1.4.0 «Travesía KSP»

Actualización basada en la [sesión real de Duna](KSP_COLABORADORES.md#2026-11-01--fully4425--mapa-nativo-en-duna-y-conector-v120). Se conservan el explorador de Marte, los mapas KSP, importación SCANsat, HUD, voz y AR. La bitácora sigue siendo un documento.

## Actualizar y arrancar

Actualiza el repositorio y reinicia el conector. Abre `http://localhost:7173/ksp-map.html`. En **Sesiones y diagnóstico** se muestran versión, instancia y puertos. También puedes consultar `/api/ksp/info` sin tener el juego conectado.

Si el puerto está ocupado, el arranque indica cómo consultar el conector que lo usa y pide detenerlo antes de reiniciar. No inicia una segunda conexión al juego detrás de un servidor HTTP que no pudo arrancar.

## Avisos de conducción y llegada

- **Avisar por encima de:** umbral orientativo, 5 m/s inicialmente. Es independiente de la velocidad usada para estimar la duración de la ruta.
- **Anticipación:** 6 segundos inicialmente. Cerca de un giro o destino se avisa si se supera el umbral; la distancia de anticipación es el máximo entre 30 m y velocidad × segundos elegidos.
- **Radio de llegada:** 8 m inicialmente, ajustable entre 3 y 25 m. La llegada requiere proximidad física al destino, velocidad de 0.5 m/s o menos y una parada continua de 3 s. El tamaño de una celda no se utiliza como radio de llegada.
- Si el vehículo se acerca y después se aleja a velocidad, puede aparecer **Destino sobrepasado**. Se utiliza la distancia física observada, no se anuncia llegada por alcanzar el final proyectado de una línea.
- La guía puede recalcular al desviarse; no frena ni dirige el rover. Los avisos no son un modelo físico de frenado, tracción o estabilidad y no garantizan una velocidad segura en una pendiente.

La voz anticipa indicaciones en función de la velocidad. Los estados de recálculo y la indicación siguiente se ordenan en una cola breve; los avisos urgentes pueden interrumpir. Indicaciones pendientes antiguas caducan a los 8 s. Al pausar, ocultar o cambiar de ruta se limpian los mensajes que ya no corresponden. El estado de voz indica cuándo está hablando.

## Terreno alcanzable y cobertura

En el mapa 2D puedes elegir **Zonas alcanzables**, **Pendiente en grados** o **Elevación**. La capa de conectividad distingue:

- Verde: conectado con la celda actual del vehículo.
- Ámbar: celda permitida, pero sin conexión según las restricciones actuales.
- Rojo: bloqueada por pendiente, altura ausente u otra restricción de la malla.
- Azul: agua; su transitabilidad depende de **Evitar agua**.

La conectividad usa las reglas de pendiente de celda, desnivel de cada paso y esquinas diagonales del planificador. Se almacena en caché hasta cambiar de celda, región o restricciones. Pasa el puntero para consultar altura, pendiente y estado. La capa es 2D; la vista 3D conserva el relieve. No detecta rocas o edificios ni certifica que el rover pase.

La guía muestra distancia al borde y avisa con anticipación. **Cargar nueva región conservando pendientes** guarda los destinos aún pendientes, muestrea alrededor del vehículo y vuelve a planificar si están dentro de la región nueva. Si no caben, conserva los puntos y pide ampliar cobertura. El tamaño de celda y malla siguen siendo elegidos por el usuario: no se reduce silenciosamente la resolución. Salir de cobertura sigue suspendiendo la guía.

## Ocultar la ventana y recuperar la conexión

Ocultar la vista pausa consultas y voz de forma deliberada, sin presentarlo como una avería de kRPC. Al volver se solicita telemetría fresca antes de seguir. Una desconexión real pausa la guía; la recuperación espera datos válidos. El tiempo oculto o desconectado no cuenta como parada confirmada en el destino.

## Evidencias automáticas del conector

Cada arranque crea una carpeta nueva en `ksp-sessions/FECHA-IDENTIFICADOR/`:

- `telemetry.jsonl`: muestras del juego hasta una vez por segundo.
- `events.jsonl`: conexión, muestreo, fallos y eventos enviados por la vista.
- `terrain-*.json`: regiones completadas.
- `mission-*.json`: rutas calculadas por el planificador nativo.
- `connector.log`: mensajes del conector, con fecha y hora.

Los archivos de terreno/misión tienen nombres únicos y no se sobrescriben al recalcular. Reiniciar crea otra sesión. **Descargar evidencias del conector** obtiene el ZIP de la sesión actual con un manifiesto que informa versión, errores y registros descartados. Las sesiones anteriores permanecen en el disco del PC, en sus carpetas.

Los JSON/JSONL tienen un límite de 32 MB por sesión; al alcanzarlo se dejan de guardar registros y el estado lo indica. El log textual rota a 1 MB con dos copias adicionales. El número de carpetas históricas no se limita automáticamente: revisa y archiva las sesiones que quieras conservar.

```bash
# Carpeta distinta, por ejemplo en un disco con espacio:
python3 integrations/ksp_server.py --session-dir /ruta/a/mis-pruebas-ksp
# Desactivar el registro en disco:
python3 integrations/ksp_server.py --no-session-log
```

En Windows sustituye `python3` por el ejecutable de tu entorno. La carpeta predeterminada está excluida de Git. Copia únicamente evidencias revisadas a `docs/ksp-logs/AAAA-MM-DD-usuario/` para compartirlas en la bitácora.

**KSP.log y Player.log no se capturan automáticamente**: el conector no conoce la ruta de instalación. Recógelos aparte antes de reiniciar el juego. Un fallo al guardar evidencias se comunica sin convertirlo en un fallo de telemetría.

## Sesiones del navegador

El mapa inicia una sesión identificada como `live`, `demo` u `offline`. Conserva telemetría observada, eventos, regiones y misiones en IndexedDB, localmente, con guardado cada 5 s. **Descargar sesión del mapa** obtiene `ksp-test-session-v1`; **Ver sesiones anteriores** permite recuperar las guardadas tras recargar.

Límites: 6 sesiones por navegador, 7200 muestras, 500 eventos, 4 regiones y 12 misiones por sesión. Al superar un límite se conservan los elementos más recientes y se incrementa el contador `dropped`. Los paquetes exponen esos contadores: no representan una sesión íntegra cuando hay recortes. Al cerrar abruptamente pueden faltar los últimos segundos desde el guardado más reciente. Si el almacenamiento no está disponible, se avisa y la descarga de la sesión en memoria sigue disponible.

Se incluyen tiempos de CPU de repintado y duración de consultas HTTP, con cuenta, suma y máximo. Son medidas del navegador; no equivalen a FPS del juego ni tiempo GPU. No se añade un bucle de renderizado continuo en reposo.

Los eventos de visibilidad permiten distinguir ocultación de un fallo de red. Una sesión `live` puede recoger un intento sin conexión: comprueba sus muestras y estados; la etiqueta por sí sola no demuestra una prueba real. Revisa posiciones, nombres y otros datos antes de compartir. No se suben automáticamente a GitHub o Render.

## API local añadida

| Ruta | Función |
| --- | --- |
| `GET /api/ksp/info` | Versión, instancia, inicio, puertos y estado del registro. |
| `GET /api/ksp/session` | Estado y límites del registro en disco. |
| `GET /api/ksp/session/export` | ZIP de evidencias de la sesión actual. |
| `POST /api/ksp/session/events` | Eventos de la interfaz, acotados y del mismo origen. |

En Render, los endpoints locales devuelven indisponibilidad; las sesiones de la demo o preparación se guardan en el navegador. El conector mantiene su enlace exclusivamente en `127.0.0.1` y todas las lecturas del juego siguen siendo de solo lectura.

## Validación y siguientes pruebas reales

Se probaron avisos, llegada física, paso de largo, conectividad, cola de voz, límites de registro, recuperación, cambio de región, ZIP y persistencia del navegador con datos simulados. Se conservan las evidencias reales anteriores de Duna, que corresponden a versiones previas.

Falta repetir con v1.4.0 en el juego: llegar y detenerse, desconectar/reconectar, conducir cerca del borde, escuchar la voz y medir rendimiento con hardware real. También sigue pendiente escanear Duna con SCANsat y convertir una exportación real. La excepción registrada de DynamicBatteryStorage pertenece a ese mod y no se atribuye a la aplicación.
