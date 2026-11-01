# Investigación: guía de supervivencia y mapa marciano

## Objetivo

Integrar múltiples misiones y al menos tres tipos de información para apoyar una caminata científica local. Elegimos Glen Torridon en Gale para investigar cómo los fluidos modificaron las rocas, observando vetas y nódulos. La app combina datos ópticos derivados (relieve estéreo HiRISE y clasificaciones visuales RMI), topografía y contexto químico-geológico de ChemCam. No representa las clasificaciones como una capa mineralógica orbital.

## Fuentes consultadas

1. **Gasda, P. J. (2022), Database of Diagenetic Features in the Clay-Rich Unit of Gale Crater, Mars.** DOI: https://doi.org/10.17189/dw9v-xe39. Archivo: https://pds-geosciences.wustl.edu/msl/urn-nasa-pds-msl_gt_diagenesis_supplement/ . Contiene clasificación de objetivos, vetas, nódulos, estratos oscuros y cementos. Publicación asociada: https://doi.org/10.1029/2021JE007097 . Incluimos la tabla original, etiqueta XML y README de origen; descargamos y transformamos coordenadas, nombres, soles, formación y clasificaciones para la aplicación.
2. **MRO / HiRISE:** https://www.uahirise.org/dtm/dtm.php?ID=PSP_009294_1750 . Modelo y ortoimágenes de Gale. DTM verificado por etiqueta adjunta y lectura de valores nativos. Crédito: NASA/JPL-Caltech/University of Arizona. Se integró la ortofotografía `PSP_009149_1750_RED_C_01_ORTHO` como fondo local en blanco y negro, usando la misma proyección del DTM. [Metadatos del recorte](../public/imagery/metadata.json). La precisión absoluta sigue pendiente de verificación independiente.
3. **Archivo MSL:** https://pds-geosciences.wustl.edu/missions/msl/ . Índice de APXS, ChemCam, CheMin, DAN, SAM, cámaras, PLACES, RAD, REMS y SPICE. La publicación es periódica: no constituye telemetría en tiempo real.
4. **Archivo de imágenes y posiciones:** https://pds-imaging.jpl.nasa.gov/volumes/msl.html . Incluye PLACES, Navcam/Hazcam y Mastcam; colecciones MSAM de mosaicos y análisis estéreo. Su existencia fue verificada; no se verificó cada producto ni su alineación con nuestro mapa.
5. **MSL Analyst’s Notebook:** https://an.rsl.wustl.edu/msl/ . Acceso a datos en contexto de operaciones por sol, ubicación e instrumento. Enlace de consulta para imágenes; no se afirma que abra automáticamente una foto del objetivo seleccionado.
6. **Berger, J. A. (2024), APXS sols 3054–3712.** https://pds-geosciences.wustl.edu/msl/urn-nasa-pds-msl_apxs_supplement_sols_3054_3712/ . DOI del conjunto: 10.17189/1139-2w66. README y primeras filas consultadas. Composición, errores, preparación de superficie y contexto geológico. La etiqueta tiene una descripción inconsistente en Easting. No integrado: falta verificar la transformación y alineación para este conjunto independiente.
7. **CRISM:** https://pds-geosciences.wustl.edu/missions/mro/crism.htm . MTRDR: productos proyectados mediante modelos del terreno; TER: observaciones con correcciones; TRDR: datos calibrados. No se ha seleccionado un producto que cubra nuestra zona. No usar colores espectrales como composición confirmada sin interpretación.
8. **MOLA:** https://pds-geosciences.wustl.edu/missions/mgs/megdr.html . Contexto regional, no detección de rocas individuales; no integrado.
9. **NASA Mars Trek:** https://trek.nasa.gov/mars/ . Portal accesible como herramienta de exploración; no se ha validado una API o servicio de teselas para la app.
10. **Misiones:** https://science.nasa.gov/mission/msl-curiosity/ y https://science.nasa.gov/mission/mars-2020-perseverance/ . Gale/Curiosity es la zona elegida; Jezero/Perseverance fue alternativa, no se mezclan sus datos con Gale.

## Condiciones de misión

Una base o hábitat humano en esta zona es hipotético. La primera parada elegida representa la salida. Las rutas se calculan con A* en una cuadrícula muestreada; se penalizan los cambios de elevación y se excluyen pendientes excesivas y valores ausentes. Los tiempos no representan prestaciones de un traje espacial. No hay clima actual, mapa local de radiación ni cálculo de oxígeno.

No se certifica seguridad. Un DTM métrico tampoco permite detectar todos los obstáculos del tamaño de una bota. El muestreo reduce más ese detalle. No se verifica resistencia del suelo, polvo, sombras, comunicaciones o evacuación. No se deduce vida presente o pasada de una clasificación de vetas o nódulos.

## Próximas extensiones científicas

Verificar independientemente la exactitud absoluta de la ortofotografía y el terreno sobre el mismo recorte; vincular imágenes originales por sol/secuencia; localizar un producto CRISM con cobertura; documentar incertidumbre horizontal y vertical; evaluar un modelo de movilidad con parámetros explícitos. No rellenar capas faltantes con datos inventados.

## Reproducción

`scripts/collect-data.py` descarga la tabla y documentación, consulta un rango de bytes del DTM y genera JSON. Guarda fecha y SHA-256 de la tabla y rango descargado. Consulta `COBERTURA.md` para límites y ecuaciones. El producto completo permanece en el archivo original; no se versiona un IMG de 391 MB. Los scripts de recopilación son herramientas de investigación, no cambian los archivos originales de NASA.

## NASA Mars Facts: contexto añadido

Fuente consultada: https://science.nasa.gov/mars/facts/ (30 de octubre de 2026). El usuario compartió su traducción automática de Google; se consultó el original para conservar la atribución. El resumen español está guardado en `public/data/mars-facts.json` y se presenta en cuatro tarjetas.

Datos usados: duración aproximada del día de 24.6 h, atmósfera principalmente CO₂ con nitrógeno y argón, extremos planetarios aproximados de −153 a 20 °C e indicios de un pasado con agua. Son contexto general, no datos meteorológicos de la ruta. No se cambian los parámetros de movilidad ni se infiere seguridad a partir de estas cifras.

La página contiene afirmaciones sobre agua salobre superficial que requieren contrastarse con literatura actual antes de incorporarlas como hechos establecidos. No se han trasladado a la aplicación. Tampoco se incorporaron noticias o fechas de misiones como si fueran observaciones del recorrido.

## Referencias consolidadas y evolución de la interfaz

La [lista de referencias y créditos](REFERENCIAS.md) incluye la ortofoto local,
la textura global, dependencias y documentación de integración. Las nuevas
vistas 3D, personajes, indicaciones, voz y HUD KSP/AR no añaden validación
científica al modelo ni convierten los escenarios de KSP en datos de Marte.
Consulta [USO.md](USO.md) para operación y [VALIDACION.md](VALIDACION.md) para
evidencia y pendientes.
