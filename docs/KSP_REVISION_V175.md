# v1.7.5 · Guía de precisión

Revisión del [reporte de FULLY4425 asistido por Claude](KSP_COLABORADORES.md#2026-11-02--fully4425--duna-explorador-v172-en-firefox), commit `ee7e972`. Se conserva el reporte original y sus evidencias. El ensayo usó v1.7.2; no demuestra fallos de autenticación o consentimiento de las versiones posteriores.

| Hallazgo | Corrección |
| --- | --- |
| «0 m» cuando el objetivo queda en la misma celda de 2 km | El plan conserva los extremos geográficos exactos. Dos puntos a 600 m dentro de la misma celda producen 600 m de ruta; la llegada sigue exigiendo proximidad real y detención. Los tramos interiores usan la altura de la celda: no inventan relieve fino. |
| Recálculos y ETA variable cada 20 s | Se evita recalcular ante el mismo escenario. El ciclo de entrenamiento sigue siendo opcional y ahora muestra explícitamente que cambia cada 20 s y cómo detenerlo; sus activaciones quedan registradas. No es clima leído de KSP. Los factores .75/.5 explican cambios legítimos de ETA al cambiar a polvo/tormenta. |
| Conexiones nuevas al no existir vehículo durante el cambio de escena | Espera de 1 s en la misma conexión, telemetría no disponible y muestreo interrumpido. Los errores reales del transporte conservan la reconexión. |
| Faltan evidencias de avisos | Eventos `browser-arrival-confirmed`, `browser-destination-passed`, `browser-driving-advice` y `browser-region-exit` enviados al conector y guardados localmente por el mapa. Las subidas conservan el consentimiento existente. Un evento de texto no demuestra que la voz fuera audible. |
| Repintado más costoso | Caché por instantánea de alturas/curvas y clima, redimensionado del canvas solo cuando cambia su tamaño y supresión del dibujo regional oculto tras el atlas. |
| Abrir Render para conectar el juego | Aviso con la dirección `http://localhost:7173/ksp-map.html` junto al botón de conexión. |

## Comprobaciones y límites

84 pruebas Python, 47 pruebas JavaScript en ocho archivos, compilación y recorrido automatizado en Chromium del atlas/globo, texturas, rutas, clima, ensayo virtual, HUD y disposición compacta. Se añaden casos de dos puntos en una celda de 2 km, falta de altura, ETA repetible y continuidad de conexión sin vehículo; la guía/interpolación admite coordenadas fraccionarias.

Se reprocesaron las 17 misiones de distancia cero del ZIP del reporte: ahora muestran entre 172,3 y 1.583,2 m. Esta reproducción usa evidencias grabadas; no es una nueva conducción del juego.

No se midió una mejora de FPS en el PC del colaborador. Sigue pendiente comparar Firefox con la misma escena y navegador, comprobar llegada real detenido dentro del radio, escuchar la voz y medir FPS con una herramienta externa. kRPC no ofrece FPS: continúa mostrándose como no disponible.

Para repetir: actualizar el código, reiniciar el conector, abrir localhost en Firefox, dejar desactivado el ciclo de clima, probar primero dos destinos distintos dentro de una celda y luego una travesía. Revisar que no aparezcan recálculos `weather` sin cambios de escenario, detenerse dentro del radio durante 3 s, salir de la cobertura y cambiar de vehículo. Añadir el resultado y las evidencias a [la bitácora](KSP_COLABORADORES.md); no marcar esta revisión automática como prueba real del juego.
