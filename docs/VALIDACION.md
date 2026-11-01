# Validación registrada y pruebas pendientes

Estado documental: **1 de noviembre de 2026**. Este documento recoge comprobaciones realizadas durante el desarrollo; no es una certificación científica, de seguridad, de rendimiento AR ni de compatibilidad de hardware.

## Pruebas automatizadas incluidas

| Suite | Último resultado registrado | Cobertura |
| --- | --- | --- |
| `python3 -m unittest discover -s test -v` | 13 pruebas aprobadas. | Planificación, obstáculos, esquinas, pendientes, datos reales, entradas y objetivos propios; contrato/frescura de telemetría y lecturas con cliente kRPC simulado. |
| `node test/directions.test.js` | 6 pruebas aprobadas. | Derecha/izquierda, ruta recta, agrupación de zigzags, objetivos intermedios, distancia 3D, rutas vacías y media vuelta. |
| `node test/ar-tracking.test.js` | 5 pruebas aprobadas. | Proyección relativa, radio del cuerpo, cruce de longitud, cambio de vehículo/cuerpo, rotación de calibración y distancia a la ruta. |

Total registrado: **24 pruebas**. No se necesita Node.js para ejecutar el servidor; es una herramienta opcional de desarrollo. Los comandos y la arquitectura están en [DESARROLLO.md](DESARROLLO.md).

## Comprobaciones de navegador realizadas

Se utilizó Chromium con Playwright como herramienta temporal. Estos scripts de navegador no forman parte de una suite versionada del repositorio.

- Carga de los 718 objetivos y de la ortofoto HiRISE; mapa 2D, terreno 3D, globo y cámaras.
- Recorrido Stornoway → Whaligoe a 20°: unos 1310 m, +59.6 m de ascenso y 50 minutos educativos. La distancia de la animación puede ser ligeramente mayor al considerar desplazamiento 3D; las métricas de misión usan distancia horizontal.
- Astronautas: reproducción, pausa, avance, llegada y limpieza de la ruta.
- Creación de objetivos propios en 2D/3D y por coordenadas, rechazo fuera de cobertura, persistencia al recargar, eliminación y ruta combinada con un objetivo científico.
- Indicaciones: selección de voz, inicio/pausa, llegada, recálculo y cancelación con motor de voz simulado. Alternativa de texto cuando no existe síntesis. No se afirma haber escuchado todas las voces de dispositivos reales.
- Menú KSP separado: transferencia de misión, estado sin conector y demostración del HUD. Se comprobaron cero solicitudes a cámara o consulta WebXR en esa página.
- HUD AR: misión cargada, interfaz móvil sin desbordamiento, simulación, inicio/cierre con cámara de prueba de Chromium y alternativa ante rechazo de sesión WebXR.
- KSP: calibración y pausa al salir del corredor con telemetría simulada, y respuesta `503` del conector cuando no hay juego/dependencia disponible.
- PWA en comprobaciones previas: manifiesto, control del service worker, consulta del mapa guardado sin red y rechazo de cálculo/exportación sin servidor.

## Distribución y servicio público

`python3 scripts/build.py` ha generado correctamente la aplicación ejecutable, incluyendo las pantallas KSP y AR y el conector opcional. La salida es una aplicación Python, no un sitio que pueda planificar rutas con alojamiento exclusivamente estático.

Se verificaron en Render los recursos publicados y respuestas HTTP de salud, planificación y exportación, incluyendo puntos personalizados. La aplicación pública es un prototipo; no sustituye las pruebas físicas que faltan.

Las capturas del README documentan la interfaz web. Una captura o emulación de tamaño móvil no acredita uso en hardware real.

## Registro del APK anterior

En una etapa previa se generó un APK de depuración y se comprobaron metadatos, contenido y firmas v2/v3 con herramientas oficiales Android. La huella está en [downloads/SHA256SUMS.txt](../downloads/SHA256SUMS.txt).

Ese APK no se ha recompilado para todas las funciones web posteriores y no se probó en Android físico ni emulador. Para el estado actual del proyecto, utiliza navegador/PWA. Consulta [android/README.md](../android/README.md) antes de instalar o recompilar.

## Pendiente de validar

| Área | Falta por comprobar |
| --- | --- |
| KSP real | Instalar una combinación compatible de KSP 1 y servidor/cliente kRPC, aceptar la conexión y conducir un vehículo con el HUD calibrado. |
| AR físico | Permisos, detección de superficies, estabilidad de maqueta, visibilidad, entrada y finalización en un teléfono/visor concreto. |
| Casco de astronauta | Hardware, SDK, sensores, óptica, latencia, interacción, ergonomía y ensayos específicos. No hay un casco integrado. |
| Rendimiento | FPS, consumo, temperatura y autonomía medidos en hardware real. Las optimizaciones actuales son de arquitectura y carga de recursos. |
| Android/PWA | Instalación física y compatibilidad de voz, WebGL y caché por dispositivo. |
| Ciencia | Precisión horizontal absoluta, alineación vertical de las alturas científicas, obstáculos pequeños y modelos de movilidad humana. |

La etiqueta PDS y la coincidencia numérica de coordenadas no demuestran por sí solas exactitud absoluta. Las rutas no validan resistencia del suelo, seguridad, comunicaciones, radiación ni autonomía de un traje.
