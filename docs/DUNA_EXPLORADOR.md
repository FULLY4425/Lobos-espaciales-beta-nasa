# v1.7.0 «Duna Explorador»

[Proyecto](../README.md) · [Configurar KSP](KSP_MAPA.md) · [Texturas y relieve](KSP_MAPAS_3D.md) · [Bitácora](KSP_COLABORADORES.md)

La página principal muestra el **escaneo completo exportado de tu partida**, conservando el explorador de Marte como opción secundaria. Las funciones de exploración se aplican a los datos de Duna; no se colocan imágenes HiRISE ni los 718 objetivos ChemCam sobre otro cuerpo.

## Mapa completo publicado en GitHub

- [PNG original completo](../public/imagery/duna-global.png): copia exacta, sin recortar, de `docs/ksp-logs/2026-11-01-FULLY4425-travesia/scansat-duna-1919-altimetria.png`.
- [Todas las alturas exportadas](../public/data/duna-global.json): cuadrícula 1126 × 563, 529220 muestras válidas, índices norte-arriba; los enteros se multiplican por `heightScale: 0.1` para obtener metros.
- [Metadatos y SHA-256](../public/imagery/duna-global-metadata.json) y [CSV original archivado](ksp-logs/2026-11-01-FULLY4425-travesia/scansat-duna-1919-csv.zip).

**Completo significa todo el archivo aportado**, que cubre el 83.5% de los píxeles del planeta. Las zonas sin escaneo se conservan; no se inventa el 16.5% restante. La imagen representa altimetría con Ore de SCANsat, no fotografía ni una exportación de la textura visual de la superficie del juego.

Para regenerarlo: `python3 scripts/build_duna_atlas.py`. El proceso no requiere instalar KSP, SCANsat ni bibliotecas externas; lee el ZIP archivado. Las pruebas comparan el hash del PNG y cuentan las muestras.

## Del planeta a la ruta

1. Abre el atlas 2D, amplía con la rueda y arrastra. Tiene retícula de latitud/longitud y puntos de las pruebas del equipo.
2. Cambia a **Globo 3D** para girar Duna. El globo usa sus alturas y la misma imagen. Para mantener fluidez, su geometría toma una muestra cada cuatro píxeles; el archivo descargable conserva todas las alturas.
3. Pulsa una zona escaneada y **Abrir región seleccionada**. Se genera una malla local de 17 × 17 a 2 km/celda, consultando el píxel de altura más próximo, sin rellenar datos ausentes. La validación y el planificador conservan los huecos como bloqueados. El atlas global no calcula una ruta planetaria sobre una proyección plana.
4. Añade destinos en 2D, pulsa el terreno 3D para rellenar coordenadas y confirma, o utiliza el formulario. Ajusta pendiente y calcula la ruta.
5. Para una guía de conducción más detallada, abre el servidor del conector en el PC del juego y muestrea con kRPC una región fina. El escaneo global de aproximadamente 1.8 km/píxel en el ecuador no detecta rocas, edificios ni obstáculos pequeños.

Los botones **Mapa completo / Globo** vuelven al contexto global y **Volver a región** recupera el mapa local. Las otras regiones de las pruebas permanecen en el catálogo.

## Funciones de exploración

| Función | Duna |
| --- | --- |
| Texturas y alturas | Imagen original SCANsat, paleta de elevación y mezcla en la región; imagen o paleta en el atlas/globo. Carga de texturas propias georreferenciadas según el contrato del mapa. |
| Objetivos y cuaderno | Cuatro puntos documentados de las sesiones, con tipo, coordenadas, descripción y enlace a evidencia; filtro y control de visibilidad. Añade un objetivo al recorrido o abre su región. No son descubrimientos científicos nuevos. |
| Destinos propios | Marcado, coordenadas, persistencia por cuerpo, eliminación, importación/exportación de misiones y planificación con pendientes/agua. |
| Navegación | Indicaciones de giro, voces del sistema, recálculo por desvío, avisos de velocidad/borde, llegada y pausa por pérdida de conexión. |
| Cámaras | Panorámica, sobrevuelo, seguimiento, superficie, giro orbital y orientación norte. La vista de superficie es un render del DEM, no Street View fotográfico. |
| Explorador | Figura virtual ampliada en la vista aérea. WASD mueve al explorador virtual únicamente sin juego y dentro de la región. No controla al Kerbal ni al rover. |
| Recorridos | Ensayo virtual sobre una ruta importada, pausa, avance y reproducción 1×/20×/100×/1000×. Claramente separado del seguimiento real. |
| Polvo y tormenta | Escenarios hipotéticos; reducen contraste y estimaciones de velocidad, añaden una zona restringida y recalculan conservando paradas pendientes. Un destino dentro de la restricción produce una pausa, no una ruta inventada. La evolución cambia cada 20 s y se detiene al ocultar la vista. |
| HUD | Presentación compacta que oculta el panel lateral y mantiene el mapa/guía. Usa **Salir del HUD** para recuperar los controles. |
| AR | Maqueta WebXR de la región, con textura propia o colores de altura, ruta y avance. Solo solicita sesión tras pulsar el botón; requiere `immersive-ar`, hit-test y un dispositivo compatible. Tiene cierre y limpieza al ocultar/cambiar de región. |
| Evidencias | Se mantienen sesiones, logs y envío opcional al almacenamiento privado configurado; el atlas y las texturas no se suben automáticamente. |

Con el juego conectado la posición procede de kRPC. El ensayo virtual y WASD no están habilitados para conducir el vehículo real. Los escenarios meteorológicos no provienen de KSP ni de sensores: son supuestos de entrenamiento y no alteran la partida.

## Verificación y pendientes

52 pruebas Python y 40 JavaScript comprueban datos completos, hash de la imagen, proyección, alturas/huecos, coordenadas esféricas, restricciones, rutas y regresiones existentes. En Chromium se verificaron atlas/globo, selección de región, objetivos, capas, cámaras, recálculo, ensayo, HUD y alternativa ante AR no disponible. No se afirma haber validado esta versión con KSP abierto ni en un casco físico. Registra esas pruebas y sus logs en `docs/KSP_COLABORADORES.md`.

Para repetir la comprobación local de navegador, instala Playwright y Chromium como herramientas de desarrollo y ejecuta `python3 scripts/check_duna_browser.py`. El script inicia un servidor temporal local y comprueba la interfaz con archivos archivados; no abre KSP ni valida hardware AR.
