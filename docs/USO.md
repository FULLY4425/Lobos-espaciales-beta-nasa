# Guía de uso · Ojo de Marte

## Abrir el explorador

- En línea: https://lobos-espaciales-python.onrender.com/
- En tu PC: inicia el [servidor Python](INSTALACION_LOCAL.md) y abre http://localhost:5173/.

El sitio abre con el terreno 3D de Glen Torridon. El panel de control está a la izquierda y se adapta al tamaño de la ventana. El botón **Objetivos** abre la ficha y el selector científico. **Ampliar** ocupa la ventana; Escape devuelve el tamaño normal.

## Mapa, capas y cámaras

| Control | Uso |
| --- | --- |
| Mapa 2D / Terreno 3D | Cambia entre vista plana y relieve. |
| Vista orbital real | Activa la ortofoto HiRISE en blanco y negro; al desactivarla se representa el relieve calculado. |
| Relieve y elevación | Representación de alturas cuando no está activa la fotografía. |
| Pendientes | Colorea la inclinación calculada y las zonas que exceden el límite elegido. |
| Objetivos científicos | Muestra u oculta los marcadores; el selector permite consultar los registros sin pulsar el mapa. |
| Evidencia geológica | Filtra vetas o nódulos; los puntos propios siguen disponibles. |
| Globo | Gira Marte y usa el marcador turquesa para abrir el recorte local. |
| Panorámica / Cenital / Sobrevolar | Cámaras predefinidas del terreno. |
| Vuelo orbital | Rotación automática; pulsa de nuevo o interactúa con el terreno para detenerla. |
| + / − / ⌖ | Acerca, aleja o restablece la vista. |

En 3D, arrastra para girar e inclinar; Mayús + arrastre o botón derecho desplaza. La rueda amplía. Con entrada táctil, un dedo gira y dos dedos desplazan/amplían. En 2D, arrastra para desplazar y usa la rueda o los botones de zoom.

Con el lienzo 3D enfocado, las flechas giran/inclinan; W/A/S/D desplazan y 0 restablece. En la vista de superficie, arrastrar o las flechas permite mirar; W/A/S/D permiten desplazarse libremente sobre el terreno; al alejarse más de 30 m de la ruta se solicita un recálculo. También se puede navegar con los botones y selectores de la interfaz.

La alta resolución corresponde al recorte de Glen Torridon, no a todo el globo. La flecha/brújula muestra el rumbo de la vista orbital; la altitud de cámara se refiere al datum marciano y puede ser negativa.

## Preparar una misión

1. Pulsa **Objetivos** y selecciona un registro o toca un marcador del mapa.
2. Consulta su nombre, coordenadas, sol y contexto geológico.
3. Pulsa **Agregar al recorrido**; el primer punto representa la salida.
4. Repite hasta tener entre 2 y 20 paradas distintas.
5. Ajusta **Pendiente máxima simulada**, entre 5° y 40°.
6. Pulsa **Calcular recorrido**.

Si no hay un paso válido, el servidor muestra un error: no se dibuja una ruta inventada. Cambia las paradas o el límite y vuelve a calcular. Quitar una parada, crear un punto usado en el plan o cambiar la pendiente invalida el cálculo anterior.

### Ejemplo reproducible

**Stornoway → Whaligoe**, pendiente **20°**: aproximadamente **1310 m**, **59.6 m de ascenso** y **50 minutos simulados**, sin regreso. Los tiempos incluyen desplazamiento a 2 km/h y 10 minutos por parada posterior a la salida. El nombre de una formación o una clasificación de vetas no implica que el sitio sea seguro para caminar.

## Crear tus propios objetivos

1. En **Mis objetivos**, pulsa **Marcar punto en el mapa**.
2. Toca el terreno 3D, o cambia a **Mapa 2D** y toca una posición.
3. Escribe un nombre único y elige si quieres añadirlo al recorrido.
4. Pulsa **Guardar punto**.

**Agregar por coordenadas** abre el mismo formulario. Usa latitud planetocéntrica y longitud positiva al este en grados. El punto debe estar dentro del terreno y tener elevación válida. El servidor comprobará además si es accesible bajo la pendiente elegida.

Se guardan hasta 50 puntos propios en este navegador. Pulsa su nombre para seleccionarlo o **×** para eliminarlo. Si estaba en la ruta, se invalida el recorrido. No se comparten automáticamente con otras personas; exporta la misión para conservar las paradas utilizadas. Borrar los datos del sitio puede borrar esos puntos.

Un punto propio no recibe sol, clasificación ni procedencia ChemCam. Su elevación se obtiene del modelo del terreno.

## Astronautas y seguimiento

Con una ruta calculada, pulsa **Iniciar / pausar recorrido**. Dos personajes siguen la línea; **Seguir astronauta** acompaña al grupo desde una cámara cercana. El control **Avance** permite buscar un tramo y pausa la reproducción.

Las velocidades 1×, 5×, 20×, 100× y 200× son velocidades de reproducción. No cambian las métricas de la misión ni simulan las tareas científicas en cada parada. Las figuras se amplían 6× en vista aérea; en seguimiento y superficie tienen escala humana.

**Superficie** coloca la cámara a unos 1.7 m del modelo. Es una reconstrucción sobre una cuadrícula de ~12 m, con textura orbital: no son fotos panorámicas Street View y el cielo es ilustrativo.

## Indicaciones y voz

El aviso del mapa presenta la próxima maniobra, su distancia y lo que falta hasta el destino. En **Navegación paso a paso** puedes desplegar todas las instrucciones: salida, giros, paradas intermedias y llegada.

- **Activar voz:** habilita anuncios durante el recorrido.
- **Voz en español:** selecciona una voz disponible; se prioriza español de México.
- **Probar voz / Repetir indicación:** reproduce una muestra o el aviso actual.
- **Ritmo / Volumen:** ajusta la reproducción.

Usa 1× o 5× para escuchar con calma. A velocidades altas se evita acumular anuncios. Pausar, saltar a otro tramo o recalcular cancela la narración pendiente. Si el dispositivo no tiene síntesis de voz, siguen funcionando las indicaciones en pantalla. Algunos motores de voz requieren conexión.

Los avisos se agrupan para no anunciar cada pequeño zigzag de la cuadrícula. Los astronautas conservan la ruta completa calculada; la guía no usa GPS ni controla un traje o vehículo.

## Exportar y abrir KSP o AR

**Exportar misión** descarga JSON con coordenadas, paradas, parámetros, métricas, supuestos y fuentes. Incluye los objetivos personalizados usados en la ruta.

Con una ruta calculada:

- **Prueba KSP** abre una ventana auxiliar de prueba del HUD. Elige **Probar HUD sin juego** o conecta el juego con el conector local.
- **Modo AR** abre la pantalla experimental con vista previa, cámara HUD o maqueta WebXR según el dispositivo.

Ambos menús reciben la misión de esa pestaña y también aceptan importar el JSON exportado. Consulta [AR_KSP.md](AR_KSP.md) para instalar kRPC, calibrar y conocer los límites. La prueba KSP no pide cámara ni visor. El futuro casco no está implementado como un producto de hardware.

## Problemas frecuentes

| Situación | Qué hacer |
| --- | --- |
| Render tarda al abrir | El servicio gratuito puede estar despertando; espera y vuelve a intentar. |
| No hay WebGL | Usa Mapa 2D; el cálculo Python sigue disponible. |
| No aparece una ruta | Prueba el ejemplo Stornoway → Whaligoe con 20°. Revisa cobertura y pendientes. |
| No se escucha voz | Pulsa Probar voz, comprueba volumen y selecciona otra voz. Algunos navegadores requieren interacción del usuario. |
| No veo mis puntos en otro equipo | Se guardan por navegador, no en una cuenta compartida. |
| KSP no conecta desde Render | Ejecuta el conector en el PC del juego y abre su dirección local. |
| La guía KSP se pausa | Revisa telemetría, calibración y desvío de la ruta; no se recalcula sobre el terreno del juego. |
| Cámara o WebXR no disponibles | Usa vista previa; revisa permisos, HTTPS y soporte del dispositivo. |
| Sin conexión | Recupera la conexión al servidor para cargar recursos, calcular y exportar. |

## Recálculo y tormentas simuladas

**Probar desvío del astronauta** muestra el recálculo automático desde la nueva
posición; también se activa con movimiento libre en Superficie y desvíos de
telemetría KSP. En el mapa, la reproducción queda pausada tras el recálculo para
que puedas revisar e iniciar la nueva ruta.

**Entorno · simulación** ofrece despejado, polvo y tormenta local. Las zonas
rojas son exclusiones hipotéticas del ejercicio; el servidor las evita al
planificar. La evolución opcional cambia el escenario cada 30 s de demostración.
Si no hay un paso válido, se suspende la guía y se habilita reintentar.
Estos escenarios no provienen de meteorología actual. Consulta
[CLIMA_RECALCULO.md](CLIMA_RECALCULO.md) antes de presentar sus resultados.
