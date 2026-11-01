# Mapas descargables y fuentes de datos KSP

Disponible desde **v1.2.0 «Atlas KSP»**. Se mantienen el explorador de Marte, el mapa nativo, el HUD y AR.

## Qué se encontró y qué está integrado

Consulta de fuentes: 1 de noviembre de 2026.

| Fuente | Qué ofrece | Uso en el proyecto |
| --- | --- | --- |
| [kRPC](https://krpc.github.io/krpc/) | API de la partida: telemetría y alturas del cuerpo activo. | Conector local de solo lectura. Ahora puedes descargar la región muestreada y volver a cargarla. |
| [SCANsat](https://github.com/KSPModStewards/SCANsat) | Mod que escanea cuerpos y exporta imágenes y CSV con coordenadas y alturas. | Convertidor de CSV por regiones, importación, relieve 2D/3D y planificación sobre esas alturas. |
| [Sigma Cartographer](https://github.com/Sigma88/Sigma-Cartographer) | Herramienta para exportar imágenes de los cuerpos desde KSP. | Fuente investigada; sus imágenes no se importan como elevaciones ni se incluyen con el proyecto. |
| [KerbalMaps](https://github.com/FiniteMonkeys/kerbal-maps) | Visor tipo Google Maps, código del servidor y generación de teselas. | Referencia investigada. Su README indica que las teselas no están incluidas, que superan 11 GB solo para Kerbin y que hay que generarlas. No se depende de un servidor público de teselas no verificado. |

**La integración nueva es de datos de alturas, no de fotografías.** No se distribuyen archivos de KSP ni mapas de terceros como si fueran propios. SCANsat se instala por separado y exporta desde tu partida; no se necesita copiar su código al proyecto. Un PNG coloreado por elevación no contiene por sí solo alturas métricas utilizables para pendientes.

## Opción rápida: guardar una región de kRPC

1. Sigue [KSP_MAPA.md](KSP_MAPA.md), abre `http://localhost:7173/ksp-map.html` y conecta el juego.
2. Muestrea una región alrededor del rover.
3. Pulsa **Descargar mapa de alturas** y conserva `ksp-height-map.json`.
4. En el mapa KSP, usa **Cargar mapa KSP (.json)** para abrirlo de nuevo.

Si no hay juego conectado, se abre **PREPARACIÓN SIN JUEGO**: el marcador es una salida manual, inicialmente el centro del mapa. Cambia sus coordenadas, agrega destinos y calcula. Para esto sigue siendo necesario el servidor Python, local o en Render; «sin juego» no significa una página estática sin servidor ni instalación PWA.

Para volver a conducir, abre la aplicación en el servidor local del conector y pulsa **Conectar KSP usando este mapa**. Se exige que nombre y radio del cuerpo coincidan. La guía entonces usa telemetría actual, con recálculo al desviarse. Cambios de cuerpo, pérdida de conexión y salida de cobertura siguen pausando la guía. No basta el nombre para detectar cambios de mods: si cambias instalación, planetas o versión de terreno, vuelve a exportar o muestrear.

## Opción SCANsat: exportar datos de tu partida

1. Instala una versión de SCANsat compatible con tu KSP 1 y sus dependencias, preferiblemente mediante CKAN. [Releases oficiales](https://github.com/KSPModStewards/SCANsat/releases). La release consultada fue **21.1**; la documentación del proyecto indica KSP **1.12.x**.
2. Escanea el cuerpo de interés con los instrumentos del mod. No habrá datos exportados de zonas sin cobertura altimétrica.
3. En los ajustes de SCANsat activa **Export .csv File**. En **Big Map**, selecciona **Altimetry** y exporta el mapa.
4. Busca el archivo `*_data.csv` en `GameData/SCANsat/PluginData/`.
5. Confirma que la cabecera sea `Row,Column,Lat,Long,Height`, con comas como separador y punto decimal. Algunas configuraciones regionales pueden producir números ambiguos con comas decimales; el importador los rechaza.

El formato se verificó contra el [exportador de SCANsat 21.1](https://github.com/KSPModStewards/SCANsat/blob/21.1/SCANsat/SCAN_Map/SCANmapExporter.cs): omite coordenadas inválidas y puntos sin cobertura, y escribe alturas y coordenadas con tres decimales. La prueba de extremo a extremo con un archivo exportado por el juego sigue pendiente; las pruebas incluidas usan CSV de prueba con esa estructura.

### Convertir solo la región que necesitas

Desde la raíz del repositorio, sin instalar paquetes Python adicionales:

```bash
python3 scripts/import-scansat.py "Duna_elevation_8192x4096_data.csv" --output duna-region.json --body Duna --radius 320000 --lat 0 --lon 0 --size 33 --cell 250
```

En Windows puedes sustituir `python3` por `py -3`. **Las coordenadas 0,0 son un ejemplo**, no un lugar de aterrizaje recomendado. Cambia la salida y el centro por los de tu expedición. El radio de 320000 m es para Duna stock; usa el radio real de tu instalación si tiene mods. Para Kerbin stock es 600000 m. Añade `--ocean` solo si ese cuerpo tiene océano: entonces se marcan como agua las alturas negativas. No se deduce agua de alturas negativas en un cuerpo seco.

- `--size`: 17, 33 o 41 muestras por lado.
- `--cell`: metros por celda. No elijas una resolución más fina que la del CSV: crearías huecos, no detalle nuevo.
- Como orientación, un mapa rectangular de ancho W tiene un espaciado ecuatorial aproximado de `2π × radio / W`. En Duna, W=8192 equivale a unos 245 m; una malla de 250 m sigue siendo una aproximación y puede dejar huecos por la distinta alineación.
- La conversión lee el CSV línea a línea y solo guarda una región de hasta 1681 celdas. Un CSV global grande tarda más en leerse, pero no se carga completo en memoria.
- Se conserva la muestra más cercana al centro de cada celda entre las que caen dentro de ella. No se interpola para rellenar huecos. Una muestra puede quedar desplazada hasta media diagonal de celda: la ruta es aproximada a esa escala.
- Las zonas no escaneadas quedan como `null` y bloquean la planificación. Si no hay paso, revisa cobertura, resolución, pendiente o región. No fuerces detalle de rover a partir de un mapa orbital grueso; usa kRPC para muestrear cerca del vehículo.

Abre **Mapa KSP → Cargar mapa KSP (.json)** y selecciona `duna-region.json`. Puedes preparar destinos sin el juego o usarlo con telemetría local del mismo cuerpo. Las alturas importadas no alteran KSP.

## Formato y límites

El formato es `ksp-terrain-v1`, con un objeto `terrain`: cuerpo, radio, centro geográfico, dimensiones, tamaño de celda, proyección local azimutal equidistante, alturas, máscara de agua y fuente declarada (`KSP1-kRPC-bedrock`, `SCANsat-CSV` o `synthetic-ksp-demo`).

La API valida dimensiones de 3–41 por lado, tamaño, extensión local, números finitos y máscaras booleanas. Recalcula la identidad del mapa a partir del contenido e ignora sesiones o identificadores importados. La carga está limitada a 512 KB. No guarda archivos en Render ni ejecuta contenido del archivo. El mapa se descarga de nuevo si deseas conservarlo; no se almacena automáticamente en el navegador.

- `POST /api/ksp/maps/validate`: valida y normaliza un archivo de mapa.
- `POST /api/ksp/maps/plan`: recibe `{map, mission}` y calcula sobre sus alturas. La misión debe indicar el identificador normalizado, cuerpo y paradas nativas.

La procedencia indicada en un JSON es una declaración del archivo, no una firma que certifique que proviene del juego. No se presenta una salida manual como vehículo conectado ni una demo como terreno real. No hay una física propia de KSP, navegación orbital, detección de rocas pequeñas o API de clima de mods.

## Rendimiento y validación

No se descargan mapas globales al abrir la interfaz ni se consulta una API externa de mapas en cada movimiento. Se reutilizan el planificador Python y el renderizado local de mallas pequeñas. Se mantiene el muestreo de kRPC por bloques y la pausa al ocultar la página.

Se comprobaron importación/exportación, salidas manuales, planificación, 2D/3D y transición a telemetría simulada. Además, se corrigió el rumbo del conector para leer `vessel.flight().heading`, que usa el marco de superficie; las coordenadas y velocidad siguen leyéndose en el marco del cuerpo. La comparación de esta corrección con la navball en una partida real sigue pendiente.
