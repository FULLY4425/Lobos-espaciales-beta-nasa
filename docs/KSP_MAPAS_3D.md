# v1.6.0 «Atlas de relieve» · mapas, texturas y orientación

[Proyecto](../README.md) · [Configurar KSP](KSP_MAPA.md) · [Exportar alturas](KSP_MAPAS_DATOS.md) · [Bitácora de pruebas](KSP_COLABORADORES.md)

## Abrir el mapa

Desde v1.7.0, la página principal abre el **mapa completo de Duna** exportado del juego. Cambia al globo 3D o pulsa una zona escaneada y **Abrir región seleccionada** para planear rutas sobre su relieve. La última región del rover sigue precargada al volver a región. Marte queda en el botón secundario. [Explorador completo y funciones](DUNA_EXPLORADOR.md). También puedes abrir `/ksp-map.html` directamente. Ambos utilizan el mismo mapa, controles y motor de rutas. El explorador original de Marte conserva sus objetivos, caminatas, globo, clima simulado, voz y acceso a AR/HUD.

Selecciona **Duna · Travesía · última región del rover** en el catálogo y pulsa cargar. Obtienes la región y la imagen archivadas en las pruebas del equipo; no necesitas estar conectado al juego para preparar rutas. En este modo la salida es manual: no es la posición actual de un vehículo.

Para ubicarte en la partida, arranca el conector en el PC de KSP y abre la página en `http://localhost:7173/`. Conecta KSP y muestrea una región. El mapa usa cuerpo, radio, latitud, longitud y rumbo de kRPC. **Localizar vehículo** centra la cámara y **seguir vehículo** conserva esa posición como centro. Fuera de cobertura, sin telemetría fresca o en vuelo, se mantienen los bloqueos y avisos de la guía. El conector sigue siendo de solo lectura y no conduce el rover.

Puedes aplicar **solo la textura del catálogo** a tu región actual de Duna sin sustituir sus alturas de kRPC. Una textura de otro cuerpo o radio se rechaza. Preparar rutas en Render funciona con mapas archivados; Render no accede directamente al KSP de tu PC.

## Qué datos muestra cada mapa

| Archivo/fuente | Uso | Resolución y límites |
| --- | --- | --- |
| `public/imagery/mars-global.jpg` y sus metadatos | Globo de Marte, textura Solar System Scope con atribución CC BY 4.0 | Contexto visual; no es un DEM ni una exportación de KSP. |
| `public/imagery/metadata.json` y ortofoto HiRISE | Superficie de Glen Torridon en Marte | Imagen NASA/JPL/University of Arizona, alineada mediante la proyección PDS; el relieve visualizado conserva su muestreo de aproximadamente 12 m. |
| `docs/ksp-logs/2026-11-01-FULLY4425-travesia/duna-rover-scansat-2.json` | Última región real del rover en Duna | 17 × 17, 289/289 alturas, 2000 m/celda, 32 km de ancho. También se incluye la región inicial de esta sesión. |
| `scansat-duna-1919-altimetria.png` en esa carpeta | Altimetría del escaneo más reciente, con Ore | 1126 × 563, 529220 filas en su CSV (83.5% de píxeles globales); textura con cobertura parcial. |
| `docs/ksp-logs/2026-11-01-FULLY4425-scansat/duna-region-scansat.json` | Región real de Duna exportada del juego con SCANsat | 17 × 17, 280/289 alturas válidas, 2000 m/celda, 32 km de ancho. Preparación regional. |
| `scansat-duna-altimetria-1126x563.png` en esa misma carpeta | Textura de altimetría SCANsat con capa Ore | No es fotografía del suelo. Se proyecta con latitud/longitud; no mejora la resolución física del relieve. |

Las máscaras `public/imagery/ksp-duna-travesia-coverage.json` y `public/imagery/ksp-duna-scansat-coverage.json` derivan de las filas y columnas presentes en el CSV archivado. Evitan tratar la parte sin escanear de la imagen como textura válida. Se pueden regenerar con `python3 scripts/ksp_texture_coverage.py export.zip mask.json --width 1126 --height 563`. El porcentaje de cobertura corresponde a píxeles de la región con alturas válidas. Donde falta imagen se usan colores de altura; donde falta altura se conserva el hueco y el planificador no inventa un paso.

## Leer el relieve

- **2D / 3D:** la ruta y los destinos son los mismos; cambiar de vista no altera la misión.
- **Alturas / textura:** paleta de menor a mayor elevación, o imagen georreferenciada. Se muestran rango de alturas, metros por muestra y ancho de región.
- **Curvas de nivel:** intervalos elegibles de 5, 25, 50 o 100 m. En relieves extremos se amplía automáticamente el intervalo para limitarlo a unas 60 cotas. Son interpolaciones entre las muestras existentes.
- **Vertical 1× / 3× / 5×:** exageración exclusivamente visual en KSP 3D. Alturas consultadas, pendientes, distancias y rutas mantienen los valores físicos.
- **Malla:** muestra los triángulos reales del modelo. No añade muestras ni obstáculos pequeños.
- **Cámara:** arrastra para girar, rueda para acercar, Mayús + arrastrar o botón derecho para desplazar; flechas giran e inclinan, `+` / `-` acercan/alejan, `0` restablece. **Norte** ofrece una vista casi cenital orientada al norte.
- **Destinos:** en 2D pulsa para agregar una parada. En 3D pulsa el terreno para consultar altura y rellenar coordenadas; confirma con **Agregar coordenadas**. Los marcadores se amplían para facilitar su lectura.

El espacio Marte también ofrece fotografía, alturas o mezcla, con curvas de 10 m y leyenda; el terreno mantiene escala 1:1. Su globo conserva el contexto visual original. El programa se orienta usando coordenadas y proyecciones; no entrena un modelo de aprendizaje automático ni identifica por imagen dónde está el vehículo.

## Cargar una textura propia

En **Cargar textura propia**, selecciona PNG/JPG/WebP (hasta 16 MB y 20 millones de píxeles) y JSON de metadatos (hasta 16 KB). La imagen se procesa en el navegador y no se sube automáticamente a Supabase. Las evidencias del conector mantienen su configuración independiente.

Ejemplo de imagen equirectangular de Duna, norte arriba y longitud este:

```json
{
  "schema": "ksp-texture-v1",
  "body": "Duna",
  "bodyRadius": 320000,
  "projection": "equirectangular",
  "west": -180,
  "east": 180,
  "north": 90,
  "south": -90,
  "credit": "Autor, herramienta, fecha y licencia de la exportación"
}
```

Para una imagen ya reproyectada exactamente sobre una región local, usa `projection: "local-grid"` y sustituye los límites por:

```json
"grid": {
  "width": 17,
  "height": 17,
  "cellMeters": 2000,
  "center": {"lat": -13.268, "lon": -133.961}
}
```

Estos números deben coincidir con la región cargada; no reutilices el ejemplo sobre otra región. Las esquinas superiores corresponden a la primera fila de la malla. Indica siempre `schema`, `body`, `bodyRadius` y `credit`. `pixelConvention: "scansat"` se reserva para la convención de filas/columnas del exportador SCANsat del archivo incluido. El catálogo puede adjuntar una máscara de cobertura local con `coverageUrl`.

## Validación pendiente en el juego

Las pruebas automatizadas verifican proyección, huecos, cobertura, capas y controles, más regresiones de rutas con telemetría simulada. Las regiones y los CSV incluidos sí proceden de pruebas reales anteriores; la sesión Travesía registra conducción, llegada y recuperación con v1.4.0. Falta confirmar esta nueva visualización con un rover activo, comparar norte/rumbo con la navball y fotografiar posiciones reconocibles de la partida. Registra resultados reales y logs en `docs/KSP_COLABORADORES.md`, sin presentarlos como comprobados antes de probarlos.
