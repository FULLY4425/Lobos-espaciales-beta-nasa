# Probar e instalar en Android

Lobos Espaciales incluye una **aplicación web progresiva (PWA)**: se puede instalar desde un navegador compatible, con icono propio y ventana independiente. Esta guía describe la PWA. También puedes instalar el **[APK de prueba](../downloads/LobosMarte-debug.apk)**; consulta [sus instrucciones](../android/README.md). Ninguna de las dos versiones está publicada en Google Play.

## Instalación desde un sitio HTTPS

Cuando el proyecto esté desplegado con su servidor Python detrás de HTTPS:

1. Abre la dirección pública en Chrome para Android.
2. Espera a que carguen el mapa y sus 718 objetivos.
3. Pulsa **Instalar app** si aparece, o abre el menú de Chrome y busca **Instalar aplicación / Añadir a pantalla de inicio**. El texto depende de la versión del navegador.
4. Abre **Lobos Marte** desde tu pantalla de inicio.

El botón solo aparece cuando el navegador informa que puede instalarla. La primera carga necesita conexión. Este repositorio no incluye una dirección pública desplegada; subir el código a GitHub no inicia el servidor. GitHub Pages no ejecuta la API Python.

## Prueba en tu red local sin desplegar

1. Inicia `python3 server.py` en tu computadora (Windows: `py -3 server.py`). Consulta `INSTALACION_LOCAL.md`.
2. Conecta el teléfono y la computadora a la misma red Wi-Fi privada de confianza.
3. Busca la dirección IPv4 local de la computadora: en Windows usa `ipconfig`; en Linux, `hostname -I`; en macOS consulta Wi-Fi → Detalles → TCP/IP.
4. En Chrome del teléfono abre, por ejemplo, `http://192.168.1.25:5173`, sustituyendo la IP por la de tu computadora.
5. Si el firewall pregunta, permite Python únicamente en la red privada. No abras puertos del router ni expongas este servidor de desarrollo a internet.

La computadora debe permanecer encendida. `localhost` y `127.0.0.1` en el teléfono apuntan al teléfono, no a tu computadora. Algunas redes aíslan sus dispositivos y no permiten esta prueba.

**Importante:** en HTTP sobre una IP de la red local podrás probar el mapa y la API, pero normalmente no el service worker ni la instalación PWA completa. Para instalabilidad y caché sin conexión se necesita un origen seguro, normalmente HTTPS. No desactives las comprobaciones de seguridad del navegador. La excepción localhost solo aplica al dispositivo que ejecuta el navegador.

## Funciona sin conexión / requiere conexión

Tras una carga completa y la activación correcta del service worker en HTTPS, se guardan interfaz, terreno, objetivos y tarjetas de contexto. Puedes volver a abrir el mapa, seleccionar objetivos y consultar sus fichas sin conexión.

**Calcular y exportar misiones requiere conexión al servidor Python.** Las consultas a NASA y documentos que no estén guardados también necesitan conexión. La caché puede ser eliminada por el navegador o por el usuario; no se garantiza almacenamiento permanente. No se incluye un motor Python dentro del teléfono.

## Actualizaciones y desinstalación

Los recursos se consultan por red cuando hay conexión y usan la copia guardada cuando no la hay. Si el navegador detecta una actualización del service worker, puede necesitar cerrar todas las ventanas de la app y abrirla de nuevo para activarla.

Desinstala desde los ajustes de Android o manteniendo pulsado el icono, según el dispositivo. Los datos guardados del sitio pueden eliminarse desde los ajustes de Chrome.

## Validación

Se prueba la interfaz con emulación móvil Chromium, manifest y service worker, carga sin conexión de los datos y advertencia de conexión. Esto no sustituye una prueba en un teléfono Android físico; no se afirma que se haya realizado esa prueba ni generado un APK.
