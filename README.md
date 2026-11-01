# Lobos Espaciales · Mars Field Guide

Aplicación educativa en español para explorar **Glen Torridon, cráter Gale, Marte**, y planear una caminata científica con datos reales de NASA/PDS.

## ¿De qué trata el proyecto?

**Lobos Espaciales** busca mostrar cómo un astronauta podría planear una caminata científica en Marte. Inspirado en el reto de NASA Space Apps, reúne datos reales de Curiosity y Mars Reconnaissance Orbiter en un mapa de Glen Torridon, dentro del cráter Gale.

El usuario puede explorar el relieve, conocer 718 objetivos científicos y seleccionar paradas para investigar vetas y nódulos: características de las rocas que ayudan a estudiar la historia del agua en la región. A partir de esas paradas, Python calcula recorridos considerando pendientes y estima distancias y tiempos con supuestos explícitos.

La meta es conectar **exploración, planificación y ciencia** en una experiencia accesible. Es un prototipo educativo: no representa una misión humana existente, no certifica seguridad y no implica afiliación ni aprobación de NASA.

## Descargar y probar en tu computadora

Sigue la **[guía de instalación local para Windows, macOS y Linux](docs/INSTALACION_LOCAL.md)**. Incluye descarga ZIP o Git, instalación de Python, inicio del servidor, una misión de ejemplo y soluciones a errores comunes.

## Android

Incluye una versión instalable como **PWA**, con iconos, modo independiente y caché del mapa. [Cómo probar e instalar en Android](docs/ANDROID.md). La instalación requiere HTTPS; el cálculo y la exportación siguen ejecutándose en el servidor Python. También hay un **[APK de prueba descargable](downloads/LobosMarte-debug.apk)** para Android 8.0 o posterior. [Instrucciones del APK](android/README.md).

## Python directamente en el celular

Puedes ejecutar el proyecto en Android con **Pydroid 3 o Termux**, sin computadora. Consulta la [guía de Python en Android](docs/PYTHON_EN_ANDROID.md), con instrucciones para abrirlo en el navegador o conectar el APK al servidor del mismo teléfono.

## Ejecutar

Para que tus compañeros accedan con un enlace público, consulta la
[guía de despliegue desde GitHub en Render](docs/DESPLIEGUE.md).

Requiere **Python 3.10 o posterior**. No necesita Node.js, pip, paquetes externos ni claves de API.

```sh
python3 server.py
```

Abre el puerto 5173 en tu entorno de desarrollo. `PORT` permite cambiarlo. Para preparar una distribución: `python3 scripts/build.py`. Ejecuta `python3 server.py` dentro de `dist/`. Se requiere un servidor Python: el alojamiento exclusivamente estático ya no es suficiente. `python3 -m unittest discover -s test -v` verifica navegación, obstáculos, entradas y datos reales. Los comandos npm se conservan solo como atajos opcionales.

## Uso

1. Activa las capas de relieve, pendientes y objetivos científicos.
2. Selecciona un punto del mapa o usa el selector accesible de objetivos.
3. Agrega dos o más objetivos al recorrido, en orden. El primero es la salida.
4. Ajusta el límite de pendiente simulado y calcula la ruta.
5. Exporta coordenadas, fuentes, parámetros y métricas en JSON.

Las rutas siguen una cuadrícula de elevación real muestreada a unos 12.1 m. Se evitan celdas sin datos, pendientes superiores al límite y cruces diagonales por esquinas bloqueadas. La función de costo penaliza desniveles. No se afirma que sea una ruta certificada ni óptima para humanos.

## Datos e investigación

- [Investigación y fuentes](docs/INVESTIGACION.md)
- [Verificación de cobertura](docs/COBERTURA.md)
- [Procedencia y hashes](public/data/provenance.json)
- [Tabla científica original](public/data/target_classification.csv)
- [Reproducir la recopilación](scripts/collect-data.py): `python3 scripts/collect-data.py` (solo biblioteca estándar).

Los datos pequeños están incluidos; la app no necesita consultar NASA durante el uso. Las tipografías remotas son opcionales y tienen fuentes de respaldo. El mapa muestra por defecto una **ortofotografía orbital real HiRISE en blanco y negro**, con zoom y arrastre. Al desactivar la fotografía se muestra el relieve calculado. [Procedencia de la imagen](public/imagery/metadata.json). Las imágenes se consultan en el archivo original mediante el enlace de contexto; todavía no se vinculan automáticamente por objetivo.

## Contexto de Marte

Incluye un resumen en español de [NASA Mars Facts](https://science.nasa.gov/mars/facts/): día marciano, atmósfera, temperaturas e historia del agua. Es información planetaria general, separada de los datos locales y de las simulaciones de misión.

## Capturas

![Vista de escritorio](docs/captura-escritorio.png)

[Validación realizada](docs/VALIDACION.md).

## Alcance

Implementado: elevación, pendientes calculadas, observaciones químico-geológicas de ChemCam, filtros de vetas y nódulos, ficha científica, recorridos y exportación. Dos misiones: MRO y MSL/Curiosity.

No integrado: capa mineralógica CRISM, clima, radiación, navegación 3D/HUD, posiciones APXS transformadas o autonomía de trajes. Se investigaron como extensiones, pero requieren comprobar cobertura y calibración. Los tiempos usan **2 km/h y 10 min por parada posterior a la salida**; no incluyen regreso. No se estima oxígeno. Las alturas publicadas de objetivos y del DTM no se comparan como si compartieran una alineación vertical ya validada.

Proyecto independiente inspirado en NASA Space Apps. No implica afiliación ni aprobación de NASA. Conservar créditos de NASA/JPL-Caltech/University of Arizona y Gasda et al. al reutilizar los datos. Consultar las condiciones de cada fuente; no se asigna una licencia propia a los datos de terceros.

## Arquitectura Python

- `server.py`: servidor HTTP y API JSON, sirve únicamente recursos públicos. Es un servidor de desarrollo; un despliegue público requiere endurecimiento e infraestructura adecuados.
- `mars/planner.py`: A* con cola de prioridad, pendientes, validación de objetivos, métricas y generación de misiones.
- `scripts/collect-data.py`: descarga y validación científica de datos NASA/PDS.
- `scripts/build.py`: prepara la distribución ejecutable.
- `test/test_planner.py`: pruebas con unittest, sin dependencias.
- HTML/CSS y JavaScript: presentación, interacción y dibujo en canvas. El JavaScript ya no calcula rutas ni métricas.

API: `GET /api/health`, `POST /api/plan`, `POST /api/export`. Los POST aceptan `{"stops":["Stornoway","Whaligoe"],"maxSlopeDegrees":20}`. El servidor usa sus propios datos de terreno y objetivos, valida de 2 a 20 nombres distintos y pendientes de 5° a 40°, y devuelve errores 400 cuando el recorrido no existe o los parámetros no son válidos.

## Terreno 3D

Selecciona **Terreno 3D** en el mapa para explorar el modelo HiRISE con su
ortofotografía real. Arrastra para girar e inclinar; Mayús + arrastre o botón
derecho para desplazar; rueda o botones +/− para acercar. En móvil, un dedo
gira y dos dedos desplazan y amplían. Con el lienzo enfocado: flechas para
girar, W/A/S/D para desplazar y 0 para restablecer.

Las alturas se representan en metros a escala 1:1, sin exageración vertical.
La geometría utiliza la cuadrícula de ~12.1 m; la fotografía conserva ~1 m/píxel.
Los huecos de elevación no generan superficie. Las rutas y objetivos comparten
las coordenadas del mapa 2D. La vista es un recorte local de Glen Torridon.
Requiere WebGL; el mapa 2D sigue disponible en equipos sin soporte.
Three.js 0.170.0 está incluido localmente, con su licencia MIT en
`src/vendor/THREE-LICENSE.txt`; no requiere CDN durante el uso.

### Ojo de Marte

El explorador abre en 3D con paneles plegables de **Capas y ruta** y
**Objetivos**. **Ampliar** ocupa la ventana; Escape vuelve al tamaño normal.
Las cámaras Panorámica, Cenital y Sobrevolar tienen transiciones animadas.
**Vuelo orbital** gira automáticamente alrededor del recorte; vuelve a pulsarlo
o arrastra el terreno para detenerlo. La brújula sigue el giro y la altitud
de cámara se expresa respecto al datum marciano, que puede ser negativa.
El vuelo recorre el mismo modelo local; no extiende la cobertura cartográfica.

### Globo, astronautas y vista de superficie

El panel de control permanece a la izquierda del mapa en escritorio; en móvil
aparece debajo para conservar espacio para el mapa.

- **Globo:** esfera giratoria de Marte con textura global de Solar System Scope
  ([CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)). El marcador
  turquesa abre Glen Torridon; la alta resolución está limitada al recorte local.
- **Terreno 3D:** vista aérea del relieve HiRISE y la ruta calculada por Python.
- **Seguir astronauta:** cámara que acompaña a dos personajes sobre la ruta.
- **Superficie:** cámara a 1.7 m sobre la ruta, con arrastre para mirar. Es una
  reconstrucción a partir del modelo de ~12 m y la ortofotografía, sin fotos
  panorámicas Street View. El cielo es un fondo ilustrativo.

Calcula una ruta de al menos dos objetivos y pulsa **Iniciar / pausar recorrido**.
El control de avance permite saltar a un tramo; las velocidades 20×, 100× y
200× aceleran la reproducción de una caminata base de 2 km/h. Esta animación no
simula los tiempos de investigación en las paradas ni cambia las métricas de
misión. Al modificar la ruta se reinicia la reproducción. Los personajes siguen
la línea de la ruta, con interpolación entre sus vértices; en vista aérea se
amplían 6× para identificarlos, y en seguimiento y superficie tienen escala
humana. La altitud indicada corresponde a la cámara, no a un sensor real.

Procedencia y atribución de la textura global:
[`public/imagery/mars-global-metadata.json`](public/imagery/mars-global-metadata.json).

### Objetivos personalizados

En **Mis objetivos**, pulsa **Marcar punto en el mapa** y toca el terreno 3D
o cambia a Mapa 2D y toca una posición. También puedes elegir **Agregar por
coordenadas**. Asigna un nombre y confirma si quieres añadirlo al recorrido.
Puedes mezclar estos puntos con los objetivos ChemCam y usar la misma función
de cálculo, exportación y caminata animada.

Los puntos se guardan en el navegador (hasta 50) y se pueden seleccionar o
eliminar desde el panel. No se sincronizan entre compañeros. La exportación
de misión incluye las coordenadas de los puntos usados. El servidor valida
coordenadas finitas, cobertura, elevación y pendiente usando sus propios datos;
las alturas enviadas por el cliente se ignoran. Cada ruta admite 2–20 paradas.
Los puntos propios no se presentan como observaciones científicas.

La API mantiene las paradas científicas como cadenas y acepta puntos propios:
`{"stops":["Stornoway",{"type":"custom","name":"Mi punto","lat":-4.73324341,"lon":137.3998236}],"maxSlopeDegrees":20}`.

### Indicaciones y voz

Al calcular una ruta, el mapa muestra el siguiente giro, su distancia y lo que
falta hasta el destino. En **Navegación paso a paso** puedes consultar la lista
de instrucciones y pulsar **Activar voz**, **Probar voz** o **Repetir indicación**.
La guía anuncia derecha, izquierda, giros suaves o pronunciados, media vuelta,
objetivos intermedios y llegada. Se sincroniza con el avance de los astronautas.

La voz utiliza SpeechSynthesis del navegador, sin claves de API. Se priorizan
las voces españolas de México; puedes seleccionar cualquier voz española
disponible y ajustar ritmo y volumen. Las preferencias se guardan localmente,
pero la voz se activa mediante un botón para respetar las políticas de audio
del navegador. El nombre y la calidad de las voces dependen del dispositivo.
Algunos motores necesitan conexión; si el navegador no ofrece síntesis, la
guía de texto continúa funcionando.

Para oír cada indicación usa las velocidades 1× o 5×. En reproducción acelerada
no se acumula una cola de anuncios: se prioriza el aviso actual. Pausar, cambiar
de cámara, buscar otro tramo o modificar la ruta cancela la narración pendiente.
Las instrucciones se calculan sobre la ruta devuelta por Python. Se agrupan
pequeños zigzags de la cuadrícula para evitar un anuncio por celda; esto no
modifica la geometría que siguen los astronautas. Las distancias del avance
consideran las alturas del modelo. Esta guía corresponde a la simulación local
y no utiliza GPS ni representa navegación operativa en Marte.

Pruebas de direcciones (Node.js, solo para desarrollo):
`node test/directions.test.js`. La ejecución del servidor sigue requiriendo
únicamente Python.

## AR y Kerbal Space Program 1

Calcula una misión y pulsa **Modo AR**. La pantalla dedicada muestra una sola
indicación, voz opcional y ajustes plegables. Ofrece cámara HUD, vista previa y
maqueta espacial mediante WebXR cuando el dispositivo admite AR con hit-test.
La versión AR evita cargar el globo y los paneles del explorador.

Se incluye un conector local de solo lectura para **KSP 1 + kRPC**, con
calibración entre la salida de la misión y la posición del vehículo. Requiere
ejecutarlo en el PC del juego; Render no accede a tu instalación local de KSP.
Consulta [instalación, compatibilidad y límites AR/KSP](docs/AR_KSP.md).

La cámara HUD no localiza al usuario sobre Marte y el globo de Duna no se
considera equivalente a Marte. La integración se ha probado con telemetría
simulada; faltan las pruebas con un visor real y una partida de KSP.
