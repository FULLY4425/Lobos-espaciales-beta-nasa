# v1.7.4 · Compartir evidencias sin cuenta

Los probadores no necesitan crear una cuenta ni introducir correo o contraseña. El conector del proyecto oficial registra una identidad técnica distinta por instalación **solo después de pulsar Permitir esta sesión**. No es una cuenta de administrador ni una identificación del hardware.

## Para quien prueba KSP

1. Actualiza tu copia del repositorio e instala las dependencias según [la instalación KSP](AR_KSP.md).
2. Inicia el conector como de costumbre: `python integrations/ksp_server.py`.
3. Lee el aviso de escritorio y pulsa **Permitir esta sesión** para compartir. El perfil oficial se configura automáticamente; no ejecutes `login`.
4. Usa el mapa. La sincronización periódica, la solicitud al salir y el intento al cerrar el conector conservan la copia local y reintentan cuando vuelve Internet. Un cierre forzado puede impedir el envío final.

**No permitir**, cerrar el aviso o no disponer de una forma de aceptar explícitamente impiden el registro y la subida. El permiso vuelve a solicitarse al arrancar. Puedes retirarlo desde KSP Map; una petición ya iniciada podría terminar. Lo enviado anteriormente no se borra al retirar el permiso. `logout` pausa también el registro automático hasta una nueva aceptación explícita al arrancar o un login manual.

Esto sigue siendo el conector Python y la web; no requiere instalar una APK ni un nuevo mod para el aviso. La comprobación visual del diálogo en Windows y una sesión real del juego siguen pendientes.

## Qué se recibe y dónde consultarlo

En [Supabase del proyecto](https://supabase.com/dashboard/project/crwzshdtvsqukheckxai), el propietario puede consultar **Table Editor → ksp_sessions** y **Storage → ksp-evidence**. Cada fila enlaza el ZIP mediante `archive_path`. Authentication muestra identidades técnicas `device-…@ksp.lobos.invalid`; no son correos de los probadores y no se envían mensajes.

Se comparten los archivos permitidos de la sesión: telemetría, vuelo/órbita, CPU/RAM/disco, consumo de KSP, eventos, mapas y rutas utilizados, análisis y registros del conector. Los logs externos del juego conservan su activación específica. No se recopilan todos los archivos del PC, capturas, contraseñas ni el listado de otras aplicaciones. [Detalle y límites del diagnóstico](KSP_DIAGNOSTICO.md).

Los datos ayudan a detectar fallos y proponer mejoras; no cambian automáticamente el código. Una prueba sintética del servidor tiene cero muestras de telemetría y no debe interpretarse como vuelo real. Falta confirmar una sesión del PC de un colaborador.

## Identidad privada y límites

`.ksp-cloud/device.json` contiene un secreto aleatorio y `.ksp-cloud/auth.json` los tokens locales; la carpeta está excluida de Git. No la publiques, adjuntes ni compartas. Se usa permiso 600 en sistemas POSIX; en Windows se depende de los permisos del usuario. Perder estos archivos pierde la identidad anterior: no se atribuyen sus colas a otra instalación.

La pasarela `ksp-device` autentica las operaciones y permite escribir únicamente evidencias de esa instalación. Los dispositivos no reciben el rol de probador manual ni acceso directo a tablas/Storage. El administrador de evidencias conserva su acceso global. Las claves de servicio solo existen en el entorno de la función.

La ruta pública de registro valida consentimiento y credenciales aleatorias. Aunque la verificación JWT de plataforma está desactivada para permitir ese registro inicial, cada operación de datos verifica el usuario y su identidad activa en el servidor. No es una ruta pública de lectura.

Límites actuales: 50 registros/hora y 200/día; ZIP de hasta 50 MiB, 128 MiB descomprimidos y 1.024 archivos de la lista permitida; 100 MiB activos por instalación, 500 MiB globales en el registro de dispositivos y 200 MiB diarios por instalación. Al alcanzar límites, la copia permanece local. Son límites de la aplicación, no una garantía de disponibilidad ni un cambio de plan de Supabase.

La pasarela elimina versiones anteriores respetando el archivo actualmente indexado. Si el propietario borra archivos directamente en Storage, puede quedar una reserva en el registro de cuotas; su conciliación automática todavía no está implementada. No borres tablas privadas para intentar liberar espacio.

## Despliegue y comprobación

El SQL de soporte está en `supabase/ksp_devices.sql` y la función en `supabase/functions/ksp-device/`. Complementan `supabase/ksp_evidence.sql`; no sustituyen sus permisos del propietario. Las tablas de dispositivos están en el esquema privado, con RLS sin políticas para clientes, deliberadamente sin acceso. Los proyectos propios y las cuentas manuales siguen usando [la configuración avanzada](KSP_NUBE.md).

La implementación se probó con 81 pruebas Python, scripts JavaScript, compilación y un registro/subida sintéticos contra el proyecto real. Se verificó que otra instalación no pudiera tomar el identificador de sesión ni borrar archivos ajenos. No se afirma que los datos del amigo ya hayan llegado: debe actualizar el conector y aceptar el aviso.
