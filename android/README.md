# APK Android · Lobos Marte

> El APK disponible es una compilación de depuración anterior a las últimas funciones web de 3D, voz, AR y KSP. No se ha recompilado ni probado para todas ellas. Usa el navegador/PWA actual para evaluar el estado vigente del proyecto.

La aplicación Android incluye interfaz, terreno HiRISE y 718 objetivos ChemCam. Usa Android WebView y un servidor de recursos dentro del proceso, limitado a 127.0.0.1. Android 8.0 o posterior. No incluye intérprete Python: las rutas y su exportación las genera el servidor Python en la computadora o un despliegue HTTPS.

## Descargar e instalar

Descarga **[LobosMarte-debug.apk](../downloads/LobosMarte-debug.apk)** desde el repositorio (abre el archivo en GitHub y pulsa descargar archivo sin procesar). En el teléfono abre el APK y, si Android lo solicita, habilita instalar aplicaciones de esa fuente. Es una compilación de prueba firmada con una clave de depuración, no una versión de Google Play. No desactives Play Protect. Para distribuir una versión de producción necesitarás firma de lanzamiento y pruebas en dispositivos.

## Usar

1. Abre **Lobos Marte**. El mapa funciona con los datos incluidos.
2. En la computadora inicia `python3 server.py` o `py -3 server.py`.
3. En el teléfono pulsa **Configurar servidor Python**. Introduce la dirección completa de la computadora, por ejemplo `http://192.168.1.25:5173`, o un servidor público HTTPS. Ambos equipos deben estar en la misma Wi-Fi privada si usas una IP local.
4. Selecciona Stornoway y Whaligoe, agrégalos al recorrido y calcula la ruta.
5. Exportar abre el selector de documentos de Android para guardar el JSON generado por Python.

La app permite HTTP para desarrollo en una red privada. Usa HTTPS para conexiones públicas. No se almacena ninguna clave ni se permite introducir credenciales en la dirección. No abras puertos del router para esta prueba. Para vaciar el servidor configurado, guarda el campo sin texto.

## Servidor Python en el mismo celular

También puedes iniciar Python con Pydroid 3 o Termux en el propio Android y configurar `http://127.0.0.1:5173` en el APK. Consulta la [guía completa](../docs/PYTHON_EN_ANDROID.md) y sus limitaciones de conectividad. No requiere una computadora.

## Compilar

Instala JDK 17+ y Android SDK con `platforms;android-35` y `build-tools;35.0.0`, aceptando las licencias de Android. Configura `ANDROID_SDK_ROOT` y ejecuta:

```bash
python3 scripts/build_apk.py
```

Requiere herramientas SDK para tu sistema operativo; el script actual usa los nombres de ejecutables de Linux/macOS. La clave de depuración se conserva en `android/build/debug.keystore` (ignorada por Git). Si compilas con otra clave, Android puede exigir desinstalar el APK anterior antes de instalar el nuevo.

La compilación y firma se verifican con herramientas oficiales. Una verificación de firma no sustituye una prueba de ejecución en un dispositivo Android físico.

## Evidencia de compilación

APK generado con plataforma Android 35, Build Tools 35.0.0 y compilador Eclipse ECJ 3.40.0 sobre OpenJDK 21 (alternativa a javac mediante `ECJ_JAR`). Herramientas descargadas de Google y Maven Central verificando sus checksums oficiales. `apksigner verify --verbose` confirmó firmas v2 y v3. `aapt2 dump badging` confirmó paquete, actividad, versión y SDK mínimo. Se verificó que el APK contiene las 718 observaciones y las funciones de exportación nativa. La huella SHA-256 del APK se guarda en `downloads/SHA256SUMS.txt`. **No se ejecutó en dispositivo físico ni emulador Android**; requiere prueba de instalación y funcionamiento.
