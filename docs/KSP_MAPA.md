# Mapa y guía nativos para KSP 1

**Nuevo en v1.6.0:** [mapas 2D/3D, texturas, curvas de nivel y orientación](KSP_MAPAS_3D.md).

El proyecto conserva **dos espacios de navegación**:

- **Explorador de Marte:** HiRISE, ChemCam, globo, objetivos, astronautas, voz,
  recálculo y escenarios de polvo hipotéticos.
- **Mapa KSP:** coordenadas, radio y alturas del cuerpo activo de tu partida.
  No utiliza las imágenes ni las elevaciones de Marte para planificar en KSP.

El [HUD de entrenamiento](../ksp.html) anterior sigue disponible: su proyección
local de una ruta marciana es un ejercicio distinto. La nueva guía nativa no
necesita calibrar Duna como si fuera Marte.

## Abrir el mapa

En el explorador pulsa **Mapa KSP** o visita `/ksp-map.html`.

- [Demo pública](https://lobos-espaciales-python.onrender.com/ksp-map.html): pulsa
  **Probar demo sintética** para evaluar la interfaz sin instalar el juego.
- Con el conector ejecutándose en tu PC: abre
  **http://localhost:7173/ksp-map.html** y pulsa **Conectar KSP local**.

La demo tiene alturas y vehículo generados para la prueba; no es una captura ni
telemetría de una partida. Está marcada como `synthetic-ksp-demo` en pantalla y
exportaciones. Render no puede conectarse directamente al juego de tu PC.

## Guardar y cargar mapas

Desde v1.2.0 «Atlas KSP» puedes descargar la región muestreada, volver a cargarla y convertir archivos de alturas SCANsat. Consulta [mapas descargables y fuentes de datos](KSP_MAPAS_DATOS.md). Se admite preparación sin el juego con una salida manual, y reutilización del mapa con telemetría local del mismo cuerpo. El modo sin juego sigue necesitando el servidor Python para calcular rutas.

## Asistencia de conducción y evidencias

Desde v1.4.0 «Travesía KSP», el mapa avisa según velocidad, distingue llegada física y paso de largo, muestra zonas alcanzables y permite recargar cobertura conservando destinos. Las sesiones se registran localmente y se pueden descargar. Consulta [KSP_TRAVESIA.md](KSP_TRAVESIA.md) para umbrales, guardado, recuperación y límites. Actualiza y reinicia el conector para activar el registro en disco.

## Preparar el conector

Sigue la [instalación de KSP 1 y kRPC](AR_KSP.md). Se mantiene el mismo cliente
Python de `integrations/requirements-ksp.txt` y los puertos RPC 50000 / stream
50001 en `127.0.0.1`. El proceso HTTP del conector usa el puerto 7173.

Si ya tenías una versión anterior, actualiza el repositorio, detén el proceso
con Ctrl+C y reinicia el conector para cargar las nuevas rutas HTTP:

```powershell
# Windows, desde la raíz del repositorio:
.venv\Scripts\python.exe integrations/ksp_server.py
```

```bash
# macOS/Linux:
.venv/bin/python integrations/ksp_server.py
```

El protocolo del conector actual es `ksp-surface-v1`. Si el navegador informa
que el conector es antiguo, comprueba qué carpeta y entorno estás ejecutando.

## Muestrear y planificar

1. Carga una partida y selecciona un rover o un astronauta en superficie.
2. Activa kRPC y conecta el mapa. Comprueba el cuerpo, vehículo y coordenadas.
3. Elige 17, 33 o 41 muestras por lado y un tamaño de celda de 5–250 m.
4. Pulsa **Muestrear alrededor del vehículo**. El progreso muestra las alturas
   leídas; puedes cancelar sin enviar órdenes al vehículo.
5. Pulsa el mapa 2D para crear destinos o introduce sus latitudes/longitudes.
   El primer punto de la ruta será siempre el vehículo actual.
6. Elige pendiente, velocidad de estimación y si quieres evitar agua.
7. Pulsa **Calcular ruta KSP**. Conduce desde el juego mientras observas el mapa,
   el rumbo, el rastro, los avisos y la voz opcional.

La región estándar es de **33 × 33 muestras a 25 m**, unos **800 m de ancho**.
La configuración máxima de 41 × 41 a 250 m cubre unos 10 km, con mucho menos
detalle. Se limita también el tamaño relativo al radio del cuerpo para que la
proyección siga siendo local. No se ofrecen mapas globales texturizados de KSP.

El muestreo lee `CelestialBody.bedrock_height` y las propiedades del cuerpo
mediante kRPC. Cuando el cuerpo tiene océano, las alturas de roca bajo el nivel
del mar se marcan como agua. El aspecto topográfico/3D es una representación
del muestreo, no una fotografía. En el agua se representa el lecho en azul.

Los cuerpos sin superficie sólida se rechazan. Las alturas no válidas permanecen
como celdas ausentes, sin interpolar una superficie inventada para planificar.

## Mapa y destinos

- Arrastra y usa la rueda para desplazar/ampliar el mapa; **Centrar región**
  restablece la vista. Las flechas, +/− y 0 también están disponibles.
- **Relieve 3D** muestra la misma malla, con giro, zoom y marcadores. Agrega los
  puntos desde 2D o desde el formulario; la vista 3D no usa imágenes HiRISE.
- Los destinos se guardan en el navegador, separados por nombre y radio del
  cuerpo. No se mezclan los puntos de Marte con los de KSP.
- Se admiten hasta 19 destinos más el vehículo actual. Puedes eliminar o limpiar
  puntos. Los que queden fuera de la región requieren otra región que los cubra.
- **Exportar misión KSP** guarda coordenadas, ruta, métricas, procedencia y una
  instantánea de alturas. La misión usa el esquema `ksp-surface-mission-v1`.
- **Importar destinos** recupera las paradas del mismo cuerpo. No confía en una
  ruta o alturas importadas: se vuelve a calcular con los datos del servidor.
  Las misiones marcianas y las de otro cuerpo se rechazan en este modo.

## Guía, voz y recálculo

La guía utiliza la posición del juego directamente en una proyección local
azimutal equidistante. El cálculo A* evita pendientes, huecos y, por defecto,
agua. Las velocidades del formulario solo sirven para estimar duración; no
cambian acelerador, frenos ni velocidad del juego. No hay piloto automático.

Si el desvío supera **máximo(30 m, 1.5 × tamaño de celda)**, se solicita otra
ruta desde la posición actual hasta los destinos pendientes. El umbral se
adapta a la resolución para no tratar el ajuste a una celda gruesa como un
nuevo desvío constante. El HUD anuncia el recálculo cuando la voz está activa.

La guía se pausa si pierde telemetría, si no encuentra un paso, si el vehículo
sale de la región o si cambia el cuerpo. Al cambiar de vehículo se invalida
la ruta anterior. Una conexión kRPC nueva requiere volver a muestrear la región.
En vuelo por encima de máximo(30 m, mínimo(100 m, 2 × celda)), la guía terrestre se suspende;
no se convierte en un navegador orbital o de aterrizaje.

Después de un fallo revisa el mensaje, corrige el contexto y pulsa **Reintentar**
o carga una región nueva. No se inventa una ruta ni se deja correr una cola de
solicitudes de recálculo. Las consultas se pausan al ocultar la página.

## Meteorología y entrenamiento

Se conserva el [modo de escenarios de polvo](CLIMA_RECALCULO.md) en el explorador
marciano y el HUD de entrenamiento. El mapa nativo no presenta esos escenarios
como clima de KSP: no se ha implementado una API de mods meteorológicos ni un
modelo atmosférico de conducción.

## API local

| Endpoint | Resultado |
| --- | --- |
| `GET /api/ksp` | Telemetría reciente, protocolo y capacidades. |
| `POST /api/ksp/terrain` | Inicia un trabajo con `size` y `cellMeters`; devuelve un identificador. |
| `GET /api/ksp/terrain` | Estado, progreso y malla cuando termina. |
| `POST /api/ksp/terrain/cancel` | Cancela solo el trabajo cuyo `jobId` se envía. |
| `POST /api/ksp/plan` | Planifica con `terrainId`, `body`, paradas nativas, pendiente, velocidad y agua. |
| `GET /api/ksp/demo/terrain` | Región sintética de la demo; disponible también sin conector. |
| `POST /api/ksp/demo/plan` | Planifica sobre esa demo, con procedencia sintética explícita. |

El conector consulta alturas por bloques pequeños y sigue actualizando la
telemetría entre bloques. Un cambio de cuerpo/vehículo durante el muestreo lo
invalida. Las peticiones de planificación comprueban contexto y frescura. Las
operaciones solo leen datos de KSP; cancelar solo detiene trabajo del conector.

## Compartir una prueba con el equipo

Usa [Bitácora de pruebas KSP](KSP_COLABORADORES.md) para documentar una sesión con el juego real, adjuntar logs y proponer mejoras. Los menús del mapa y del HUD enlazan al documento; añade tu sesión y sus evidencias mediante un commit o pull request.

## Límites y validación

El muestreo no detecta rocas, edificios, vehículos, resistencia del suelo,
tracción, estabilidad o capacidad real de cada rover. Una ruta sobre una celda
no garantiza paso físico entre todos los detalles de esa celda. La proyección
es local y las métricas aproximadas. El modo no reemplaza un navegador orbital.

Se verificaron la geometría geográfica, muestreo, agua, pendientes, rechazo de
contextos incorrectos y de datos obsoletos, así como el flujo HTTP del conector
con un cuerpo y telemetría simulados. En navegador se probaron 2D/3D, destinos,
exportación, persistencia y recálculo. Hay [pruebas parciales en una partida real de versiones anteriores](KSP_COLABORADORES.md#2026-11-01--fully4425--mapa-nativo-en-duna-y-conector-v120). El flujo SCANsat real ya está documentado y su CSV se reproduce automáticamente. Falta conducir con las funciones nuevas de v1.4.0 y sobre esa región importada; este entorno no tiene el juego instalado.
