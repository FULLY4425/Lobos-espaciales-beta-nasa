# Evidencias privadas en Supabase · v1.5.0

El conector puede enviar sus evidencias a un proyecto **de tu cuenta de Supabase**, conservando siempre la copia local. La navegación, la demo y Marte siguen funcionando sin configurar este servicio.

**Estado de entrega:** el cliente, la cola, los controles y el SQL están implementados y probados con respuestas simuladas. Todavía debes crear y configurar el proyecto de tu cuenta antes del primer envío real. No se ha creado un proyecto, aplicado el SQL ni enviado evidencias a una cuenta externa durante esas pruebas.

## 1. Crear el lugar donde recibirás los archivos

1. Entra en [Supabase Dashboard](https://supabase.com/dashboard), crea tu cuenta y un proyecto. Puedes llamarlo `lobos-espaciales-ksp` y empezar con el plan Free si sus límites te sirven. Revisa los límites/costos actuales; la aplicación no contrata un plan ni crea recursos pagados.
2. Ejecuta en **SQL Editor** el archivo [supabase/ksp_evidence.sql](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/blob/main/supabase/ksp_evidence.sql) del repositorio. Usa preferentemente un proyecto nuevo dedicado a estas evidencias. El SQL crea:
   - bucket **privado** `ksp-evidence`, con ZIP de hasta 50 MB;
   - tabla `ksp_sessions`, índice de sesiones con versión, usuario, fecha, muestras y ubicación del archivo;
   - tabla `ksp_testers`, usuarios autorizados;
   - políticas que limitan a cada probador a su carpeta, y permiten al administrador leer las de todos.
3. En **Authentication → Users**, crea un usuario de la aplicación para ti y otro para cada probador autorizado. Son cuentas de **Supabase Auth**, distintas de la cuenta con la que administras el proyecto. Configura sus contraseñas mediante el mecanismo del Dashboard; no las pongas en GitHub ni en este chat.
4. Copia el UUID del usuario e inclúyelo en la lista de autorizados desde SQL Editor:

   ```sql
   -- Tu usuario de la aplicación, para consultar todas las evidencias:
   insert into public.ksp_testers(user_id, role) values ('TU-UUID-DE-AUTH', 'admin');
   -- Cada colaborador, con acceso solo a sus propias evidencias:
   insert into public.ksp_testers(user_id, role) values ('UUID-DEL-PROBADOR', 'tester');
   ```

5. Desactiva el registro público de usuarios en los ajustes de Auth si solo participará tu equipo. Incluso una cuenta creada fuera de la lista no obtiene permiso de subida por esas políticas.
6. En **Settings / API Keys**, identifica la URL del proyecto y la clave **publishable** (o la `anon` pública antigua). No uses `service_role`, `sb_secret_*`, contraseña de base de datos ni tokens de administración.

El script está pensado para un proyecto dedicado. Si utilizas uno existente, revisa que otras políticas de Storage no concedan permisos más amplios sobre este bucket: las políticas permisivas pueden combinarse. No se eliminan políticas ajenas al proyecto KSP.

## 2. Configurar cada PC que ejecuta KSP

Actualiza el repositorio. Detén el conector antes de configurar o cambiar de usuario. Desde la raíz:

```powershell
# Windows: reemplaza URL y clave pública por las de tu proyecto.
.venv\Scripts\python.exe integrations/ksp_cloud.py configure --url https://TU-PROYECTO.supabase.co --key sb_publishable_TU_CLAVE --interval 300
.venv\Scripts\python.exe integrations/ksp_cloud.py login --email TU-CORREO
```

En macOS/Linux usa `.venv/bin/python`. La contraseña se pide de manera oculta en la terminal; utiliza la de tu usuario **Supabase Auth**, no tu contraseña de administración de Supabase. No se guarda esa contraseña: se conservan tokens de acceso/renovación en `.ksp-cloud/auth.json`.

La URL, clave pública e intervalo se guardan en `.ksp-cloud/config.json`. Toda la carpeta `.ksp-cloud/` está excluida de Git. Los archivos de autenticación se crean con permisos de propietario en sistemas POSIX; en Windows protégelos con los permisos de tu usuario y no compartas esa carpeta.

Reinicia el conector:

```powershell
.venv\Scripts\python.exe integrations/ksp_server.py
```

Si la configuración está habilitada, el envío comienza automáticamente: primera comprobación al arrancar y después cada 300 s (5 min). El intervalo permitido es 30–3600 s. No hay una promesa de subida en tiempo real.

### Incluir KSP.log y Player.log

Solo se recogen si eliges explícitamente sus rutas:

```powershell
.venv\Scripts\python.exe integrations/ksp_server.py --ksp-log "C:\ruta\Kerbal Space Program\KSP.log" --player-log "C:\ruta\Player.log"
```

Se toma una instantánea al preparar evidencias y al cerrar normalmente el conector, y se conserva en la sesión local para reintentos posteriores. Durante la sincronización también se recoge antes de comprobar la autenticación, de modo que un fallo de Internet/login no obliga a descartar esa copia.

Cada log externo admite hasta **16 MB**; si es mayor se incluyen los últimos 16 MB y el manifiesto indica `truncated: true`, tamaño original y bytes incluidos. Si una ruta deja de ser legible se conserva la última copia y el manifiesto la identifica como caché, no como lectura actual. Esto no captura cada cambio ni todos los reinicios del juego. Revisa o conserva aparte el archivo original si necesitas el historial completo; las credenciales, rutas o nombres presentes dentro de un log no se anonimizan automáticamente antes de la subida privada.

## 3. Cómo acceder a la información

Desde tu cuenta de administración del proyecto:

- **Table Editor → ksp_sessions:** cada fila corresponde a una sesión, con propietario, versión, inicio, muestras, fecha de la instantánea y ruta del ZIP.
- **Storage → ksp-evidence:** los archivos quedan bajo `UUID_DEL_USUARIO/ID_DE_SESION/SHA256.zip`. Puedes verlos y descargarlos con el Dashboard.
- Los archivos no tienen un enlace público. Cualquier enlace firmado que generes desde el servicio tiene el alcance/caducidad que le asignes.

El ZIP conserva `session.json`, telemetría JSONL, eventos, mapas, misiones y logs del conector; también KSP.log/Player.log si configuraste sus rutas. Los archivos de autenticación, configuración y cola local no forman parte de las evidencias.

Una sesión con `telemetry_samples = 0` puede ser un intento sin conexión al juego. El número de muestras o una subida correcta no certifican que se hayan realizado todas las pruebas.

## 4. Pausar, reintentar y comprobar

En el mapa local, abre **Sesiones y diagnóstico**:

- **Pausar subida:** persiste la pausa; sigue el registro local. Una transferencia que ya empezó puede terminar.
- **Reanudar:** vuelve a comprobar la cola.
- **Enviar ahora:** adelanta el siguiente intento cuando no esté pausado.
- El estado informa del último envío confirmado, error o próximo reintento. «Pendiente» no equivale a «enviado».

Los controles solo funcionan con tu conector local, no con la demo de Render. No se introducen claves ni contraseñas en el navegador.

```powershell
# Desactivar el envío para este arranque, conservando evidencias locales:
.venv\Scripts\python.exe integrations/ksp_server.py --no-cloud-upload
# Enviar también sesiones antiguas de la carpeta seleccionada:
.venv\Scripts\python.exe integrations/ksp_server.py --cloud-include-history
# Ver proyecto e intervalo sin mostrar tokens:
.venv\Scripts\python.exe integrations/ksp_cloud.py status
```

`--cloud-include-history` es una elección explícita: sin él se envían la sesión actual y las que ya estaban en cola. No cambia la propiedad de una sesión previamente vinculada a otro usuario o proyecto.

Para cerrar la sesión del usuario: detén primero el conector y ejecuta `python integrations/ksp_cloud.py logout` con el Python de tu entorno. Cambiar de usuario debe hacerse con una sesión nueva del conector.

## 5. Reintentos, integridad y conservación

La transferencia se ejecuta en un hilo separado; no hace llamadas de control a KSP ni mantiene el bloqueo del registrador durante la compresión o la red.

Antes de enviar se guarda un ZIP pendiente y su SHA-256 en la carpeta local. Si falla la red o la actualización del índice, se reintenta exactamente esa instantánea. La espera aumenta desde 30 s hasta un máximo de 15 min. El botón permite solicitar un reintento antes.

Primero se confirma el archivo y después el índice. Se mantiene una fila por sesión; al confirmar una nueva instantánea se elimina la anterior del bucket. Si la limpieza falla, queda pendiente de reintento. Puede haber instantáneas anteriores o huérfanas temporales durante fallos; revisa las cuotas del servicio. No se elimina la copia local por una subida correcta.

Al reiniciar, el conector recupera las sesiones ya puestas en cola desde la misma carpeta y configuración. No se envían automáticamente directorios arbitrarios o sesiones antiguas nunca autorizadas. Solo puede haber un proceso de subida por carpeta de configuración; usa el mismo directorio de sesiones o configuraciones separadas si ejecutas varios conectores.

Cerrar el conector no garantiza que se termine una transferencia en curso. La última parte queda local y se recupera en el siguiente arranque. Si no puedes esperar, conserva la carpeta hasta confirmar el último envío. Los límites de captura local siguen vigentes: una subida no recupera muestras descartadas previamente por alcanzar esos límites.

## 6. Verificar el primer envío real

Después de aplicar el SQL e iniciar sesión:

1. Arranca el conector y comprueba versión **1.6.0** (o posterior).
2. Abre una sesión KSP, solicita un mapa y una ruta; pulsa **Enviar ahora**.
3. Espera a que el estado indique el envío confirmado.
4. En Supabase comprueba la fila y descarga su ZIP; revisa el manifiesto y la presencia de telemetría/mapa/misión.
5. Pausa la subida y comprueba que sigue el registro local. Después reanuda.
6. Para probar aislamiento, utiliza dos probadores autorizados y verifica que cada cuenta solo puede consultar sus filas/archivos, mientras tu usuario administrador puede leer ambas.

**Pendiente de activar:** este último ensayo y la aplicación de las políticas deben hacerse contra el proyecto real que crearás. Las pruebas del repositorio usan un servicio simulado; no demuestran por sí solas que una cuenta externa esté configurada. Supabase conserva las evidencias; Render sigue alojando la web y no necesita guardar estos archivos en su disco temporal.
