# Cómo descargar y probar Lobos Espaciales en tu computadora

No necesitas una cuenta de NASA, claves de API, Node.js ni instalar paquetes con pip. Los datos necesarios ya están incluidos. Necesitas **Python 3.10 o posterior** y un navegador moderno.

## 1. Descargar el proyecto

### Opción sencilla: archivo ZIP

1. Abre https://github.com/FULLY4425/Lobos-espaciales-beta-nasa .
2. Pulsa el botón **Code** y después **Download ZIP**.
3. Extrae el ZIP en una carpeta de tu computadora. No ejecutes el proyecto dentro del archivo comprimido.
4. Abre la carpeta extraída. Debes ver `server.py`, `README.md`, `mars`, `src` y `public`.

Si el repositorio es privado, inicia sesión en GitHub con una cuenta que tenga acceso. Una invitación pendiente debe aceptarse antes de descargarlo.

### Alternativa: usar Git

Si ya tienes Git instalado:

```bash
git clone https://github.com/FULLY4425/Lobos-espaciales-beta-nasa.git
cd Lobos-espaciales-beta-nasa
```

## 2. Instalar o comprobar Python

### Windows

Descarga Python desde https://www.python.org/downloads/ e instálalo. Si aparece la opción **Add Python to PATH**, márcala. Abre una nueva ventana de PowerShell después de instalarlo.

Comprueba la versión:

```powershell
py -3 --version
```

Debe mostrar Python 3.10 o una versión posterior. Si `py` no está disponible, prueba `python --version` y usa `python` en lugar de `py -3` en los siguientes comandos.

### macOS y Linux

En Terminal:

```bash
python3 --version
```

Si falta Python o la versión es anterior a 3.10, instala una versión actual desde https://www.python.org/downloads/ (macOS) o mediante el gestor de paquetes de tu distribución (Linux).

## 3. Iniciar la aplicación

### Windows: PowerShell

Abre la carpeta que contiene `server.py` en el Explorador de archivos. Haz clic en la barra de dirección, escribe `powershell` y presiona Enter. En esa ventana ejecuta:

```powershell
py -3 server.py
```

### macOS y Linux: Terminal

Entra en la carpeta extraída usando `cd`. Por ejemplo, si la guardaste en Descargas:

```bash
cd ~/Downloads/Lobos-espaciales-beta-nasa-main
python3 server.py
```

Adapta la ruta si la carpeta está en otro lugar. También puedes escribir `cd ` y arrastrar la carpeta a la Terminal para insertar su ruta.

### Abrir el mapa

Cuando aparezca `Lobos Espaciales · Python · port 5173`, abre esta dirección **en el navegador de tu propia computadora**:

```text
http://127.0.0.1:5173
```

Mantén abierta la terminal mientras pruebas la aplicación. Para detenerla, vuelve a la terminal y presiona **Ctrl+C**.

No abras `index.html` con doble clic: el mapa y las rutas necesitan el servidor Python. No uses `python -m http.server`: ese servidor no ejecuta nuestra API de planificación.

## 4. Hacer una prueba completa

1. Espera a que el mapa indique **718 objetivos**.
2. En el selector del cuaderno de campo, elige **Stornoway** y pulsa **Agregar al recorrido**.
3. Elige **Whaligoe** y agrégalo también.
4. Deja el límite de pendiente en **20°** y pulsa **Calcular recorrido**.
5. Debe aparecer una ruta de aproximadamente **1.31 km** y un tiempo simulado de **50 minutos**. No incluye regreso.
6. Prueba la capa **Pendientes**, el filtro **Vetas** y **Exportar misión** para descargar un JSON.
7. Abre **Fuentes** para consultar la procedencia y las limitaciones de los datos.

La aplicación usa un recorte real de HiRISE y observaciones de Curiosity. Las rutas son educativas; no certifican seguridad. Las imágenes originales se consultan mediante enlaces externos. El mapa y el cálculo funcionan con los datos locales; esos enlaces y las tipografías remotas necesitan internet, con fuentes de respaldo si estas últimas no cargan.

## 5. Si algo falla

| Problema | Solución |
|---|---|
| Python no se reconoce | Instala Python, vuelve a abrir la terminal y comprueba su versión. En Windows prueba `py -3` o `python`. |
| No encuentra `server.py` | Ejecuta el comando dentro de la carpeta que contiene ese archivo. |
| No encuentra `mars` o los datos | Extrae el proyecto completo, conservando su estructura; no copies únicamente `server.py`. |
| La página no abre | Comprueba que la terminal sigue abierta y no muestra errores. Usa `http`, no `https`, en la dirección local. |
| Error de puerto ocupado | Detén otra instancia con Ctrl+C o utiliza otro puerto, como se indica abajo. |
| No aparece una ruta | Prueba Stornoway → Whaligoe con 20°. Algunos pares no tienen un recorrido permitido bajo el límite seleccionado. |
| GitHub muestra 404 o acceso denegado | Comprueba la dirección y que tu cuenta tenga acceso si el repositorio es privado. |

### Cambiar el puerto

Windows PowerShell:

```powershell
$env:PORT = "5174"
py -3 server.py
```

macOS / Linux:

```bash
PORT=5174 python3 server.py
```

Después abre `http://127.0.0.1:5174`.

## 6. Actualizar y ejecutar las pruebas (opcional)

Si descargaste un ZIP, descarga y extrae la nueva versión en otra carpeta. Si usaste Git, desde la carpeta del proyecto ejecuta `git pull --ff-only` cuando no tengas cambios propios pendientes. Reinicia el servidor para usar la nueva versión.

Windows:

```powershell
py -3 -m unittest discover -s test -v
```

macOS / Linux:

```bash
python3 -m unittest discover -s test -v
```

Deben completarse las siete pruebas sin errores.

## Compartirlo con otras personas

Comparte el enlace del repositorio y esta guía. Cada persona puede descargarlo y ejecutarlo en su computadora; `127.0.0.1` siempre apunta al equipo de quien abre la dirección, no al tuyo. Si el repositorio es privado, necesitarán acceso.

Este servidor es para desarrollo y pruebas locales. No requiere abrir puertos del router ni desplegar un sitio público. Escucha en todas las interfaces para permitir su uso en entornos de desarrollo; evita ejecutarlo en redes no confiables o exponerlo a internet.
