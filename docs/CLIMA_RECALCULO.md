# Desvíos, recálculo y escenarios de polvo

## Qué cambia en la navegación

Si el astronauta se aparta más de **30 m** de la ruta, el mapa detiene la
reproducción y solicita a Python una ruta desde esa posición hasta las paradas
pendientes, en el mismo orden. El destino final se conserva. Las indicaciones,
el tiempo y la distancia se reemplazan por los del nuevo cálculo.

Puedes demostrarlo con **Probar desvío del astronauta**. En **Superficie**, W/A/S/D
permiten moverlo libremente sobre el modelo; las flechas y el arrastre permiten
mirar. El botón de prueba desplaza al personaje a una posición local válida a
más de 30 m, no lo vuelve a colocar artificialmente sobre la ruta.

En el laboratorio KSP, la posición procede de telemetría calibrada. El recálculo
conserva el origen de esa calibración aunque cambie el inicio de la nueva ruta.
No envía comandos al rover. KSP debe seguir siendo conducido por el usuario.
El resultado sigue perteneciendo al terreno marciano del prototipo, no al
terreno físico del juego.

Si no hay telemetría reciente, la posición está fuera del mapa o no existe un
paso con los límites actuales, se suspende la guía. La ruta anterior no debe
usarse para continuar. **Reintentar desde posición actual** o **Reintentar
recálculo** permite volver a solicitarlo. No se acumulan peticiones automáticas
tras un fallo; los cambios de contexto cancelan resultados pendientes.

## Escenarios meteorológicos

Los parámetros se distribuyen en
[weather-scenarios.json](../public/data/weather-scenarios.json), con origen
`synthetic` y modelo `training-scenarios-v1`. El servidor utiliza ese mismo
archivo para calcular restricciones y tiempos; no confía en restricciones
arbitrarias enviadas desde el navegador.

| Escenario | Efecto visual / de planificación | Velocidad educativa |
| --- | --- | --- |
| Despejado | Sin zona restringida ni reducción de contraste simulada. | 2 km/h |
| Polvo atmosférico | Neblina/contraste reducido en el explorador; sin zona de exclusión. | 1.5 km/h |
| Tormenta local | Neblina y un círculo rojo de exclusión hipotético. A* evita sus celdas y cruces diagonales por sus esquinas. | 1 km/h |

**Estos valores son supuestos de entrenamiento, no mediciones, previsiones ni
límites validados de movilidad humana.** La zona de tormenta se coloca de forma
determinista en el recorte para poder repetir la demostración; no es una
tormenta observada en esa posición. Su radio es de 11 celdas del terreno, unos
134 m en el recorte incluido.

El cambio de escenario recalcula desde la posición actual. Si esa posición ya
está dentro de la zona restringida, se pausa: el programa no inventa una salida
que atraviese celdas declaradas bloqueadas. Un personaje o vehículo que entre
en esa zona también detiene la guía.

**Evolución del escenario** cambia despejado → polvo → tormenta → despejado
cada 30 segundos. Es una secuencia acelerada para demostración, no una escala
temporal de evolución atmosférica. Se detiene al ocultar o abandonar la página.
El HUD KSP/AR muestra el escenario y los avisos sin añadir partículas o neblina
sobre la cámara real, para mantener la interfaz poco invasiva.

## Por qué polvo, no una tormenta terrestre

Marte tiene tormentas de polvo; [NASA Science · Mars Facts](https://science.nasa.gov/mars/facts/)
ofrece contexto planetario. La [investigación de instrumentos MSL](INVESTIGACION.md)
incluye referencias a REMS, pero este prototipo no descarga ni asimila sus
observaciones meteorológicas.

No se simulan fuerzas de viento, presión dinámica, temperatura de un traje,
electrificación del polvo, deposición, producción solar ni pérdida real de
comunicaciones. Tampoco se presenta una tormenta marciana como si tuviera las
condiciones de una tormenta de arena terrestre. La neblina es un efecto visual;
no se ha calibrado contra profundidad óptica ni alcance visual observado.

## Demostración para una presentación

1. Calcula Stornoway → Whaligoe con 20° y escenario despejado.
2. Inicia la caminata o selecciona un tramo con Avance.
3. Pulsa **Probar desvío** y observa el nuevo inicio y el destino conservado.
4. Cambia a **Tormenta local**: muestra el círculo de restricción y la nueva ruta.
5. Exporta el JSON: incluye `environment`, `planningContext`, supuestos y fuentes.
6. Explica por separado los datos reales (DTM, ortofoto y ChemCam), el algoritmo
   de planificación y las condiciones hipotéticas del ejercicio.

En el ejemplo completo desde la salida inicial, la ruta despejada es de unos
1310 m y 50 min; con el escenario de tormenta configurado, unos 1320 m y 90 min.
Si ya has avanzado o te has desviado, el nuevo inicio cambia esos valores.

Para presentar el sistema como una herramienta científica de predicción o
seguridad harían falta datos meteorológicos trazables, modelos físicos,
incertidumbre, criterios operativos y validación independiente. El objetivo
actual es demostrar adaptación del plan ante condiciones explícitas, no
atribuir al prototipo aprobación de NASA ni precisión que no ha sido medida.
