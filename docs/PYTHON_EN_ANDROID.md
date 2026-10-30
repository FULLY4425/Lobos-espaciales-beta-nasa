# Ejecutar el proyecto con Python en el celular

Puedes ejecutar el servidor Python **en el propio teléfono Android** con Pydroid 3 o Termux. Así no necesitas una computadora para calcular rutas. Este procedimiento usa el mismo proyecto y los datos incluidos; no requiere pip, Node.js ni claves de NASA.

Necesitas Android, Python 3.10 o posterior, un navegador actualizado y el proyecto completo extraído. Estas instrucciones no aplican a iPhone. La disponibilidad y los permisos dependen de la aplicación Python y la versión de Android.

## Opción 1: Pydroid 3

1. Instala **Pydroid 3 – IDE for Python 3** desde su ficha oficial en Google Play. Comprueba que el editor sea **Lider Soft KZ**. No necesitas los complementos de paquetes científicos para este proyecto.
2. Descarga el ZIP del repositorio: https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/archive/refs/heads/main.zip . Si es privado, descarga desde GitHub con una cuenta autorizada.
3. Extrae el ZIP con el administrador de archivos. Conserva toda la carpeta: `server.py`, `mars`, `public`, `src` e `index.html` deben permanecer juntos. No abras únicamente `server.py` desde dentro del ZIP.
4. En Pydroid 3, abre **Terminal** desde su menú. Comprueba la versión:

```sh
python --version
```

Debe ser 3.10 o posterior. Si es anterior, actualiza Pydroid desde su fuente oficial.

5. Desde la terminal entra en la carpeta extraída. Por ejemplo:

```sh
cd /storage/emulated/0/Download/Lobos-espaciales-beta-nasa-main
python server.py
```

La ruta puede variar. Usa la ubicación real indicada por tu administrador de archivos. Si Android solicita acceso a la carpeta, concédelo mediante su selector de archivos o los permisos de Pydroid. Si la aplicación no permite acceder a Descargas, utiliza una carpeta que Pydroid pueda leer y copia allí **todo** el proyecto. No necesitas root.

6. Espera a ver `Lobos Espaciales · Python · port 5173`.
7. Sin cerrar Pydroid, abre Chrome y escribe:

```text
http://127.0.0.1:5173
```

La dirección apunta al servidor dentro de tu propio teléfono. Mantén Pydroid ejecutándose mientras usas el mapa. Para detener el servidor, vuelve a su terminal y envía **Ctrl+C** con el teclado o los controles de la terminal.

## Opción 2: Termux

1. Instala Termux desde una fuente oficial recomendada en https://termux.dev/ . Sigue sus indicaciones actuales de instalación; no mezcles aplicaciones y complementos de fuentes distintas.
2. En Termux instala Python y Git:

```sh
pkg update
pkg install python git
```

3. Descarga el repositorio y ejecútalo:

```sh
git clone https://github.com/FULLY4425/Lobos-espaciales-beta-nasa.git
cd Lobos-espaciales-beta-nasa
python --version
python server.py
```

Si el repositorio es privado, la clonación necesita autenticación de GitHub. Como alternativa, descarga el ZIP desde el navegador, extrae el proyecto completo, ejecuta `termux-setup-storage`, autoriza el acceso solicitado por Android y entra en la carpeta extraída:

```sh
cd ~/storage/downloads/Lobos-espaciales-beta-nasa-main
python server.py
```

4. Abre `http://127.0.0.1:5173` en el navegador del teléfono. Mantén Termux ejecutándose. Para detener el servidor usa **Ctrl+C**.

La instalación inicial de Python/Git y la descarga requieren internet. Una vez instalados y descargado el proyecto, los datos del mapa y el cálculo de rutas no requieren acceder a NASA. Los enlaces externos y las tipografías remotas sí usan internet; hay fuentes de respaldo.

## Usar el APK con el servidor en el mismo teléfono

También puedes usar la interfaz de **Lobos Marte** en lugar del navegador:

1. Inicia `python server.py` en Pydroid o Termux como se explica arriba.
2. Abre el APK.
3. Pulsa **Configurar servidor Python**.
4. Guarda esta dirección:

```text
http://127.0.0.1:5173
```

5. Selecciona objetivos y calcula una ruta.

En este caso `127.0.0.1` es correcto porque Python y el APK están en el mismo teléfono. Si Python está en una computadora, debes usar la dirección de esa computadora en la red Wi-Fi.

**Limitación del APK actual:** el cálculo comprueba el estado de conexión informado por Android WebView. En modo avión puede avisar que no hay conexión aunque el servidor local esté activo. Para uso totalmente sin internet en ese caso, abre la interfaz directamente en el navegador mediante `http://127.0.0.1:5173`; si el navegador también informa modo sin conexión, será necesario adaptar esa comprobación antes de garantizarlo. No se ha validado este comportamiento en un dispositivo físico.

## Prueba rápida

Selecciona **Stornoway**, agrégalo al recorrido, selecciona **Whaligoe** y agrégalo también. Con límite de **20°**, calcula la ruta: aproximadamente **1.31 km** y **50 minutos simulados**, sin regreso. En la versión del navegador, la exportación descarga un JSON; en el APK abre el selector de documentos de Android.

## Problemas comunes

| Problema | Qué revisar |
|---|---|
| No encuentra `server.py` | La terminal debe estar en la carpeta extraída que contiene ese archivo. |
| No encuentra `mars` o los datos | Copia y extrae el proyecto completo, sin cambiar su estructura. |
| Permission denied en Descargas | Revisa el permiso de archivos de la app o utiliza una carpeta accesible para ella. |
| Address already in use | Hay otro servidor en el puerto. Detén la instancia anterior o inicia `PORT=5174 python server.py` y usa el puerto 5174. |
| Funciona y luego deja de responder | Android puede suspender Pydroid o Termux en segundo plano. Vuelve a la app, comprueba la terminal y reinicia Python si se detuvo. Revisa las opciones de batería de esa app si necesitas mantenerla activa. |
| El APK no calcula | Comprueba primero `http://127.0.0.1:5173/api/health` en el navegador del mismo teléfono; debe mostrar `status: ok`. Revisa luego la dirección guardada en el APK. |

El servidor es de desarrollo y escucha en todas las interfaces. Úsalo en una red de confianza y no abras puertos del router. No necesitas exponer el teléfono a internet para usarlo localmente.

## Estado de comprobación

El servidor y sus siete pruebas se ejecutaron en Python de escritorio. Pydroid 3, Termux y la comunicación entre aplicaciones en Android **todavía requieren prueba en un dispositivo físico**. El proyecto usa únicamente la biblioteca estándar y Python 3.10+, pero eso no garantiza los permisos de archivos ni el manejo de procesos de cada teléfono.
