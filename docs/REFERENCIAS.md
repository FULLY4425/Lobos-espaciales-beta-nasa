# Referencias, datos y créditos

Este documento distingue los recursos incorporados de los investigados como posibles extensiones. Las referencias científicas describen Marte; las rutas, el HUD, los personajes y las métricas son productos del prototipo.

## Datos incorporados

| Recurso | Referencia original | Uso y límites |
| --- | --- | --- |
| Objetivos de Glen Torridon | Gasda, P. J. (2022), *Database of Diagenetic Features in the Clay-Rich Unit of Gale Crater, Mars*. [DOI 10.17189/dw9v-xe39](https://doi.org/10.17189/dw9v-xe39), [archivo NASA/PDS](https://pds-geosciences.wustl.edu/msl/urn-nasa-pds-msl_gt_diagenesis_supplement/). | 718 registros, soles 2300–3007: nombres, coordenadas, formación y clasificación de rasgos diagenéticos. No son una capa mineralógica orbital. |
| Publicación asociada | [DOI 10.1029/2021JE007097](https://doi.org/10.1029/2021JE007097). | Contexto científico de la base de rasgos. No se deduce transitabilidad ni presencia de vida a partir de las clasificaciones. |
| Modelo digital de terreno | MRO/HiRISE, `DTEEC_009149_1750_009294_1750_U01`. [Página del producto](https://www.uahirise.org/dtm/dtm.php?ID=PSP_009294_1750), [directorio PDS](https://www.uahirise.org/PDS/DTM/PSP/ORB_009100_009199/PSP_009149_1750_PSP_009294_1750/). | Modelo nativo de ~1.012 m; la cuadrícula incluida se muestrea cada 12 píxeles (~12.14 m). Crédito: NASA/JPL-Caltech/University of Arizona. |
| Fotografía orbital local | `PSP_009149_1750_RED_C_01_ORTHO`: [JP2 original](https://www.uahirise.org/PDS/DTM/PSP/ORB_009100_009199/PSP_009149_1750_PSP_009294_1750/PSP_009149_1750_RED_C_01_ORTHO.JP2), [etiqueta PDS](https://www.uahirise.org/PDS/DTM/PSP/ORB_009100_009199/PSP_009149_1750_PSP_009294_1750/PSP_009149_1750_RED_C_01_ORTHO.LBL). | Recorte de 1464 × 864 píxeles, banda RED en escala de grises. Comparte proyección, escala y offsets con el DTM. Crédito: NASA/JPL/University of Arizona. No es color natural ni imagen de superficie. |
| Textura global de Marte | [Solar System Scope](https://www.solarsystemscope.com/textures/), [imagen 2K](https://www.solarsystemscope.com/textures/download/2k_mars.jpg). | Contexto del globo; licencia [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Se conserva como recurso separado de HiRISE. |
| Contexto planetario | [NASA Science · Mars Facts](https://science.nasa.gov/mars/facts/). | Resumen español sobre día, atmósfera, temperaturas e historia del agua. No es clima actual de Glen Torridon ni telemetría de misión. |

## Trazabilidad dentro del repositorio

- [Tabla científica original](../public/data/target_classification.csv).
- [Procedencia y SHA-256 de los datos](../public/data/provenance.json): descarga registrada el 30 de octubre de 2026.
- [Metadatos y SHA-256 del recorte orbital](../public/imagery/metadata.json).
- [Atribución de la textura global](../public/imagery/mars-global-metadata.json).
- [Cobertura, proyección y ecuaciones](COBERTURA.md).
- [Recopilación de tabla y terreno](../scripts/collect-data.py).

La tabla y el rango del DTM tienen huellas registradas; el IMG completo de cientos de MB no se incluye en Git. La ortofoto local se recortó desde el JP2 usando las coordenadas descritas en los metadatos y se convirtió a WebP. `collect-data.py` no vuelve a generar por sí solo esa ortofoto. Los datos pequeños ya están incluidos para ejecutar la aplicación.

## Archivos de consulta y líneas de investigación

| Fuente | Para qué se consultó | Estado en el prototipo |
| --- | --- | --- |
| [MSL Analyst’s Notebook](https://an.rsl.wustl.edu/msl/) | Imágenes y operaciones por sol, instrumento y ubicación. | Enlace de contexto. No se abre automáticamente una foto asociada a cada objetivo. |
| [Archivo MSL / PDS](https://pds-geosciences.wustl.edu/missions/msl/) | ChemCam, APXS y otros instrumentos. | Referencia de archivo; no telemetría en tiempo real. |
| [PDS Imaging / MSL](https://pds-imaging.jpl.nasa.gov/volumes/msl.html) | Navcam, Hazcam, Mastcam, PLACES y mosaicos. | No se ha alineado ni incorporado cada producto. |
| [APXS, soles 3054–3712](https://pds-geosciences.wustl.edu/msl/urn-nasa-pds-msl_apxs_supplement_sols_3054_3712/) | Composición y contexto geológico. DOI: [10.17189/1139-2w66](https://doi.org/10.17189/1139-2w66). | No integrado; transformación y alineación pendientes. |
| [CRISM](https://pds-geosciences.wustl.edu/missions/mro/crism.htm) | Posible mineralogía orbital. | No hay producto local seleccionado con cobertura validada. |
| [MOLA / MEGDR](https://pds-geosciences.wustl.edu/missions/mgs/megdr.html) | Relieve regional. | No integrado en la navegación local. |
| [NASA Mars Trek](https://trek.nasa.gov/mars/) | Referencia de exploración planetaria. | No se utiliza una API ni teselas de este portal. |
| [Curiosity](https://science.nasa.gov/mission/msl-curiosity/) y [Perseverance](https://science.nasa.gov/mission/mars-2020-perseverance/) | Selección y contexto de misión. | Se eligió Gale/Curiosity; no se mezclan datos de Jezero como si pertenecieran a Gale. |

El análisis y las limitaciones originales están en [INVESTIGACION.md](INVESTIGACION.md). Las capas investigadas no se rellenan con datos inventados.

## Tecnología y documentación de integración

- **Python:** [documentación oficial](https://docs.python.org/3/). El servidor y el planificador principal usan la biblioteca estándar.
- **Three.js 0.170.0:** [documentación](https://threejs.org/docs/), [licencia MIT incluida](../src/vendor/THREE-LICENSE.txt). El módulo se distribuye localmente; no hace falta un CDN para visualizar.
- **Síntesis de voz:** [SpeechSynthesis](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis). Voces del navegador/dispositivo, no audios de NASA ni una voz clonada de Google Maps.
- **Cámara HUD:** [getUserMedia](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia). Requiere permiso y contexto seguro compatible.
- **AR espacial:** [WebXR Device API](https://developer.mozilla.org/en-US/docs/Web/API/WebXR_Device_API). Se solicita `immersive-ar`, hit-test y, cuando está disponible, superposición DOM. La compatibilidad se comprueba en ejecución.
- **KSP 1 / kRPC:** [proyecto y releases](https://github.com/krpc/krpc/releases), [cliente Python 0.7.0](https://pypi.org/project/krpc/0.7.0/). Las propiedades del adaptador se revisaron en ese cliente; no se ha probado una partida real.
- **Render:** [servicios web](https://render.com/docs/web-services), [despliegues](https://render.com/docs/deploys), [comprobaciones de salud](https://render.com/docs/health-checks). Ver [configuración del proyecto](DESPLIEGUE.md).

La interacción toma como referencia exploradores de mapas y globos como Google Maps/Google Earth. No utiliza imágenes, teselas ni API de Google para representar Marte, ni implica una relación con esos servicios.

## Reutilización

Conserva la atribución de cada recurso y consulta las condiciones del archivo original. La textura global tiene su propia licencia CC BY 4.0 y Three.js conserva su MIT. No se declara una licencia única para todos los datos, imágenes, código e instrumentos de terceros. El proyecto no tiene afiliación ni aprobación de NASA, KSP, Meta o Google.

## Escenarios de polvo

[CLIMA_RECALCULO.md](CLIMA_RECALCULO.md) distingue el contexto planetario de NASA de los parámetros sintéticos de entrenamiento. Las zonas de exclusión, velocidades y efectos de neblina no son productos meteorológicos observados.

## Terreno nativo del juego

El [mapa KSP](KSP_MAPA.md) obtiene alturas mediante `CelestialBody.bedrock_height`, propiedades del cuerpo y telemetría del cliente kRPC 0.7.0. No usa datos de NASA para representar cuerpos de KSP. La demo nativa tiene procedencia `synthetic-ksp-demo`; no se atribuye a una partida observada.
