# Validación

30 de octubre de 2026.

- `npm test`: cinco pruebas ejecutadas y aprobadas. Distancia diagonal, celdas ausentes y esquinas bloqueadas, límites de pendiente, cobertura de los 718 objetivos y ruta con terreno real.
- `npm run build`: archivos estáticos generados correctamente.
- Chromium headless con Playwright (herramienta temporal externa al proyecto): carga de 718 objetivos, selección y agregado de dos puntos, cálculo de recorrido, descarga JSON, diálogo de fuentes, filtro de vetas (441 objetivos), cambio de ancho a 390 px sin desbordamiento horizontal y limpieza de métricas. Sin errores JavaScript de página.
- Ejemplo Stornoway → Whaligoe con límite de 20°: aproximadamente 1310 m, +59.6 m de ascenso calculado y 50 minutos simulados. No incluye regreso. Estos valores dependen del muestreo y del modelo educativo.
- Capturas: `captura-escritorio.png`, `captura-movil.png`.

Las pruebas no certifican transitabilidad, exactitud absoluta del terreno ni seguridad de una misión. La consulta de imágenes originales es un enlace al archivo; no se ha automatizado la asociación de fotos.

## Migración a Python

Siete pruebas unittest aprobadas: distancia, barreras sin datos, esquinas, pendientes y límites, 718 posiciones, misión real y entradas inválidas. La API Python entrega estado y rechaza objetivos desconocidos; no sirve server.py ni metadatos de Git. La interfaz usa peticiones asíncronas y descarta resultados cuando se cambia el plan durante el cálculo. El generador ahora empaqueta una aplicación Python, no una página exclusivamente estática.
