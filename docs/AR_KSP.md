# Ojo de Marte: AR y Kerbal Space Program 1

## Qué está implementado

- **Cámara HUD:** un aviso de navegación sobre la cámara, sin seguimiento espacial.
- **AR espacial WebXR:** coloca una maqueta del terreno HiRISE y la ruta en una
  superficie detectada. Un punto muestra el avance simulado o recibido de KSP.
- **Vista previa:** la misma interfaz mínima sin pedir acceso a la cámara.
- **KSP 1 / kRPC:** conector local de solo lectura de posición, rumbo, velocidad,
  cuerpo celeste y altitud del vehículo activo. No toca mandos ni piloto automático.

No equivale a caminar físicamente por Marte ni a proyectar una ruta marciana a
escala real sobre la calle. El HUD no usa GPS. El seguimiento espacial de WebXR
coloca una maqueta; la posición en la misión viene del simulador o del control
manual. El juego no recibe órdenes del navegador.

## Abrir una misión en AR

1. Calcula una ruta en el mapa y pulsa **Modo AR**.
2. Elige **Iniciar AR espacial**, **Abrir cámara HUD** o **Vista previa**.
3. Oculta **Ajustes** para dejar solo el siguiente aviso. Puedes variar su opacidad.
4. Activa la voz si la necesitas. No se reproduce automáticamente.
5. Usa **Simular** para una reproducción de dos minutos o mueve el control de avance.

También puedes importar el JSON generado por **Exportar misión**. El archivo
se valida contra la cuadrícula local, tiene un máximo de 2 MB y no se sube al
servidor. La página AR no carga el globo ni la lista completa de objetivos.

En AR espacial, busca una superficie y toca el círculo para colocar la maqueta.
El tamaño inicial es de 0.5 m de ancho y puede ajustarse entre 0.2 y 1 m. Usa
**Recolocar maqueta** para buscar otra superficie. El mapa y las distancias de
la misión no cambian cuando redimensionas la maqueta.

## Compatibilidad de dispositivos

La cámara necesita HTTPS o `localhost`, permisos y un navegador compatible con
`getUserMedia`. WebXR requiere `immersive-ar` y detección de superficies
(`hit-test`). Se comprueba la capacidad en el navegador y el inicio puede ser
rechazado si faltan permisos o funciones del visor.

Android con un navegador compatible y servicios AR del dispositivo es una
opción para probar. La disponibilidad de passthrough/AR en Quest u otras gafas
depende de su navegador, sistema y soporte WebXR; no se garantiza por marca.
Si no hay WebXR se ofrecen cámara HUD y vista previa. No se instala un SDK
nativo de visor ni se usa una captura de cámara sin autorización.

## Por qué KSP 1

Se ha elegido KSP 1 por su integración mediante mods y kRPC. Este conector
**no es para KSP 2**. Las propiedades usadas se comprobaron en el cliente
Python kRPC 0.7.0. Instala una versión del mod de servidor kRPC compatible con
ese cliente y con tu instalación de KSP 1.

- Mod y versiones: https://github.com/krpc/krpc/releases
- Cliente Python: https://pypi.org/project/krpc/0.7.0/

## Ejecutar el conector en el PC del juego

Desde la raíz del proyecto:

```sh
python3 -m venv .venv
# Activa el entorno virtual según tu sistema operativo.
python3 -m pip install -r integrations/requirements-ksp.txt
python3 integrations/ksp_server.py
```

1. Abre KSP 1, selecciona un vehículo/rover y activa el servidor del mod kRPC.
2. Mantén kRPC en `127.0.0.1`, RPC 50000 y stream 50001.
3. Abre `http://localhost:7173/`, calcula una ruta y entra en **Modo AR**.
4. En los ajustes de AR, elige **KSP 1 · kRPC local**.
5. Con el vehículo en el lugar que quieras usar como salida, pulsa **Calibrar
   inicio de ruta**. A partir de ahí, desplázalo usando los controles del juego.

Puedes cambiar los puertos del cliente local:

```sh
python3 integrations/ksp_server.py --port 7173 --rpc-port 50000 --stream-port 50001
```

La conexión HTTP y la RPC se limitan al equipo local de forma predeterminada.
El conector ofrece la misma aplicación y `/api/ksp`, evitando conexiones del
navegador desde Render al puerto local del juego. El servicio público en Render
no puede acceder a tu KSP: muestra un mensaje para iniciar el conector local.

Para usar un teléfono o visor conectado al PC hace falta servir esta misma
aplicación/conector mediante HTTPS de confianza accesible en tu red privada,
por ejemplo con un proxy inverso hacia `127.0.0.1:7173`. Los dispositivos deben
confiar en su certificado y poder alcanzar el PC. Eso requiere configuración
adicional de la red/visor; no se habilita automáticamente ni se evita TLS.
No publiques el servidor kRPC en Internet.

## Calibración y límites del seguimiento

Duna, Kerbin y Marte no comparten mapa ni dimensiones. Se usa el radio real
que devuelve KSP para convertir el cambio local de latitud/longitud en metros,
y se asocia la posición inicial del vehículo con el primer punto de la misión.
**Rotación del escenario KSP** permite ajustar la orientación de esa asociación.
Esto es una correspondencia local calibrada, no una conversión científica de
Duna a Marte ni una comprobación de obstáculos del juego.

El conector consulta como máximo unas cinco muestras por segundo; el HUD pide
una actualización cada 500 ms sin solapar solicitudes. Si cambia el vehículo,
el cuerpo celeste o la conexión, hay que recalibrar. Datos de más de tres
segundos dejan de considerarse conectados en el servidor. Si el desvío respecto
a la ruta supera 30 m, se ocultan las instrucciones y se pausa la voz. No se
recalcula una ruta sobre el terreno real de KSP.

## Menos consumo y menos elementos en pantalla

- Pantalla AR independiente, sin globo, paneles laterales ni astronautas complejos.
- Voz opcional, un aviso compacto, opacidad ajustable y controles de al menos 44 px.
- El modo cámara HUD no usa WebGL ni un bucle de dibujo de vídeo en JavaScript.
- WebXR carga Three.js solo cuando está disponible y usa una malla de terreno
  pequeña, sin sombras ni efectos de posprocesado. Renderiza al ritmo del visor.
- La cámara, la reproducción y las consultas se detienen al salir; al ocultar
  la página se detiene la cámara HUD y el sondeo de KSP.

## Validación realizada y pendiente

Pruebas automatizadas de rutas, coordenadas relativas, cambio de vehículo,
datos obsoletos y lecturas del adaptador con un cliente simulado. Pruebas de
navegador de HUD, permisos/cierre de cámara con dispositivo de cámara simulado,
importación de misión, telemetría simulada y rechazo de sesión WebXR.

**Pendiente:** prueba de aceptación en un visor/teléfono AR real y en una partida
real de KSP 1 con el mod kRPC. Este entorno no dispone de esos dispositivos ni
del juego; no se afirma validación física ni rendimiento medido en visor.
