# Bitácora de pruebas de integración KSP

Disponible en **v1.3.0 «Bitácora KSP»**. [Abrir la sección](https://lobos-espaciales-python.onrender.com/ksp-tests.html) · [Ver reportes publicados](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/issues?q=is%3Aissue+%22%5BKSP%5D%5BPRUEBA%5D%22+in%3Atitle).

## Quién debe usarla

Colaboradores que hayan probado la integración con una partida real de **KSP 1**: mapa nativo, conector kRPC, HUD conectado al juego o mapas SCANsat usados junto a KSP. Una conexión fallida también puede reportarse: describe el intento real, el entorno y el motivo del bloqueo.

Marca la confirmación de prueba real. La declaración del probador delimita el alcance; no se verifica automáticamente que haya ejecutado KSP. Las experiencias del explorador de Marte, de AR sin KSP o de la demo sintética se documentan en sus otros canales.

La página se abre desde **Mapa KSP → Bitácora de pruebas KSP** y **HUD KSP → Reportar experiencia KSP**. Para capturar el estado de tu conector, utiliza **http://localhost:7173/ksp-tests.html**, con el conector actualizado y ejecutándose. La página pública de Render no puede leer el juego de tu computadora.

## Preparar un informe detallado

1. Indica título, usuario, fecha de la sesión y versión de la aplicación o commit probado.
2. Anota versión y distribución de KSP, versiones del mod/cliente kRPC, sistema, navegador, equipo y mods relevantes. Usa la versión que probaste, aunque sea anterior a la actual.
3. Identifica cuerpo, rover/astronauta, área de integración y resultado: funcionó, funcionó parcialmente o prueba bloqueada.
4. Describe la configuración, pasos reproducibles, resultado esperado y lo observado. Relaciona cada error con la hora y el paso correspondiente.
5. Completa las comprobaciones: conexión, posición, rumbo/navball, alturas, destinos, recálculo, desconexión, voz, importación y rendimiento. El estado inicial es **No probado**; no se marca una función como correcta automáticamente.
6. Adjunta logs o pega extractos. Si no fue posible obtenerlos, explica qué faltó y qué otras evidencias tienes.
7. Escribe mejoras y sugerencias con su utilidad y prioridad. Si no tienes propuestas, indícalo.
8. Pulsa **Preparar informe para revisión**. Verás el texto completo, podrás copiarlo y descargar un paquete JSON con el informe, diagnóstico y archivos revisados.

Los datos del formulario no se guardan automáticamente al cerrar o recargar la página. Descarga el paquete antes de salir si necesitas conservar el trabajo. Modificar un campo invalida la vista previa anterior para evitar publicar un informe desactualizado.

## Qué logs y evidencias aportar

- **`KSP.log`**, en la carpeta de instalación del juego, correspondiente a la sesión del problema. Si usas `Player.log`, añade de qué instalación y sesión procede.
- **Salida del conector Python**, con mensajes de inicio, conexión y errores. Puedes guardarla al ejecutar:

  ```bash
  # macOS/Linux, desde la raíz del repositorio:
  .venv/bin/python -u integrations/ksp_server.py > ksp-connector.log 2>&1
  ```

  ```powershell
  # Windows, desde la raíz del repositorio:
  .venv\Scripts\python.exe -u integrations/ksp_server.py *> ksp-connector.log
  ```

  Mantén el proceso abierto durante la prueba; detén con Ctrl+C al terminar. En estos ejemplos la salida se escribe en el archivo en vez de mostrarse en la terminal.
- **Errores de consola del navegador**: copia el mensaje completo y su momento; una captura puede complementar el texto.
- **Misión y mapa exportados**, si el fallo depende de destinos, alturas, pendiente o cobertura.
- **Capturas o video** que comparen lo que indica la guía con el juego/navball, especialmente para problemas de rumbo o posición.
- **Diagnóstico puntual**: el botón consulta `/api/ksp` y `/api/ksp/terrain` una vez. Incluye estado, protocolo, telemetría disponible y resumen de muestreo. No graba una sesión completa ni sustituye `KSP.log` o la salida del conector. Un estado sin conexión se registra como tal y no demuestra una prueba real.

### Revisión local de archivos

Se admiten hasta 3 archivos `.log`, `.txt`, `.json` o `.csv`, cada uno de hasta 2 MB y con un total de hasta 5 MB. Se leen como texto UTF-8. Para logs grandes, capturas y ZIP utiliza los adjuntos del formulario de GitHub.

La página oculta algunos patrones habituales de tokens, contraseñas y nombres de carpeta personal. Esta revisión no garantiza anonimización completa. **Descargar revisado** obtiene el texto procesado completo de cada archivo. El paquete JSON también conserva los textos revisados completos; el informe Markdown incluye extractos de hasta 2000 caracteres por archivo y señala los recortes. Los extractos pegados admiten hasta 6000 caracteres.

Revisa especialmente rutas personales, correos, nombres de usuario y claves antes de adjuntar archivos. Los archivos originales de tu computadora no se modifican.

## Publicar y colaborar

GitHub conserva los informes, adjuntos y comentarios de los probadores. No se guardan en el disco temporal de Render ni se necesita configurar una base de datos o dar un token de GitHub a la página.

1. Revisa el informe y descarga los logs procesados que quieras compartir.
2. Pulsa **Abrir formulario de GitHub** e inicia sesión con tu cuenta. El formulario es **Prueba de integración KSP**, con prefijo `[KSP][PRUEBA]`.
3. Si el informe es largo, pulsa **Copiar informe** y pégalo en **Informe detallado**. La página avisa cuándo es necesario: no recorta el informe para encajarlo en una URL.
4. Completa los campos pendientes. **Arrastra los archivos completos revisados al campo «Logs y evidencias adjuntas»**. Puedes adjuntar el paquete JSON. Espera a que termine la subida.
5. Confirma el alcance y publica en GitHub. Comprueba el número de issue: abrir el formulario o descargar un paquete no publica un reporte.
6. Añade actualizaciones como comentarios en ese mismo issue: nueva versión probada, logs posteriores y si se resolvió. Los mantenedores pueden responder y cerrar el reporte al terminar.

El repositorio y los reportes son **públicos**. La publicación y los permisos los gestiona GitHub; la sección no crea un espacio privado ni una verificación de pertenencia al equipo. Mantiene un canal temático para pruebas KSP. No se publica nada de forma automática desde el navegador ni se utilizan credenciales compartidas del propietario.

**Cargar reportes de GitHub** consulta la API pública bajo demanda, muestra hasta 20 reportes con el prefijo KSP entre las últimas 100 entradas y excluye pull requests. **Ver todos** abre el historial completo, incluyendo abiertos y cerrados. Si GitHub limita la API o falla la red, puedes seguir usando ese enlace. La lista muestra títulos, autor, estado y número; los adjuntos y comentarios se consultan en GitHub.

## Formato y mantenimiento

- Página: `ksp-tests.html`, accesible también desde el servidor local del conector.
- Lógica de informe y filtrado: `src/ksp-reports.js`; interfaz: `src/ksp-tests.js` y `src/ksp-tests.css`.
- Formulario nativo de GitHub: `.github/ISSUE_TEMPLATE/ksp-integration.yml`, con confirmación de KSP real y campos requeridos para versión, área, resultado, informe, logs/evidencias y mejoras.
- Paquete descargado: `ksp-integration-report-v1`. `publication: not-submitted-by-this-download` identifica que la descarga no equivale a publicación.
- La interfaz no ejecuta HTML de los reportes ni de los logs. El listado acepta únicamente enlaces de issues del repositorio esperado.

Se probaron preparación, validaciones, límites, revisión de archivos, copia/descarga, cambios posteriores, diagnóstico con respuestas simuladas y listado público con respuestas de prueba. No se publicaron reportes ficticios para validar la función. La confirmación y la subida final se hacen en GitHub por cada probador.
