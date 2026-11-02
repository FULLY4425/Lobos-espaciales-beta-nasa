# v1.7.3 · Permiso para compartir pruebas de KSP

[Proyecto](../README.md) · [Configurar Supabase](KSP_NUBE.md) · [Datos del equipo y vuelo](KSP_DIAGNOSTICO.md)

Al iniciar el conector en Windows aparece una ventana normal de escritorio titulada **Lobos Espaciales · Permiso para compartir**, con dos botones:

- **Permitir esta sesión**: autoriza enviar las evidencias descritas al proyecto indicado.
- **No permitir**: el mapa, KSP y el registro local continúan, pero no se envían evidencias.

No es una solicitud UAC ni necesita permisos de administrador de Windows. No añade un mod ni un aviso dentro del juego. En Python para Windows la ventana usa Tcl/Tk, incluido normalmente en el instalador oficial; asegúrate de tener activada esa opción. En otros sistemas también se intenta mostrar la ventana.

## Qué muestra el aviso

Indica el destino HTTPS concreto y las categorías de datos: vuelo/órbita, CPU/RAM/disco, rendimiento de KSP, rutas, errores y registros. KSP.log/Player.log solo se adjuntan si se eligieron sus rutas; pueden contener texto personal. No se recopilan capturas, teclas, contraseñas ni archivos personales. La opción negativa explica que los registros quedan en el PC.

El permiso dura **solo el arranque actual del conector**. No se guarda un «sí para siempre»: cada reinicio vuelve a preguntar. Cambiar de proyecto requiere el aviso correspondiente a ese destino. Los botones no activan controles del juego.

Cerrar la ventana, pulsar Escape o no disponer de interfaz nunca significa permitir. Si falta escritorio/Tk y hay terminal interactiva, se muestra el mismo texto y se exige escribir `PERMITIR`; Enter deniega. En procesos sin escritorio y sin entrada interactiva se deniega automáticamente. No existe una opción CLI `--yes` para saltarse la decisión.

## Iniciar y compartir

1. Detén el conector anterior y actualiza el repositorio en el PC del juego.
2. Configura `configure-project`, inicia sesión con `login` y comprueba `doctor` si aún no lo hiciste. [Comandos y cuentas](KSP_NUBE.md).
3. Ejecuta `python integrations/ksp_server.py` y elige en el aviso.
4. En `http://localhost:7173/ksp-map.html`, **Sesiones y diagnóstico** muestra si el permiso está concedido y el estado de la subida.

**Permitir no sustituye el acceso técnico al servidor.** Cada probador sigue necesitando su usuario Supabase Auth autorizado en `ksp_testers`. El aviso no crea usuarios ni otorga privilegios de administrador. Si se permite pero falta configuración o login, se informa de ello y no se afirma haber enviado datos.

`--no-cloud-upload` y `--no-session-log` desactivan el envío y no muestran el aviso. Las opciones para desactivar estadísticas de equipo o vuelo adicional siguen disponibles.

## Retirar el permiso

Pulsa **Retirar permiso de envío** en **Sesiones y diagnóstico**. Se bloquean nuevos envíos, autenticación automática para subir, reintentos y sincronización final. Pausar, reanudar o «Enviar ahora» no pueden volver a conceder el consentimiento: hace falta reiniciar y aceptar el aviso.

La retirada deja una marca `.cloud-revoked` en la sesión actual y en las pendientes identificadas del mismo usuario/proyecto. Estas sesiones no se reenvían automáticamente en el siguiente arranque, aunque se acepte compartir una sesión nueva. La marca no se incluye en el ZIP.

Una transferencia ya iniciada puede terminar; el programa no puede recuperar bytes ya enviados. Lo recibido antes no se borra al retirar permiso. La copia local permanece. Para retirar el acceso de una cuenta al servidor o borrar datos existentes se usan las funciones administrativas del propietario, por separado.

## Colas antiguas

Los reintentos de sesiones previas con consentimiento registrado se conservan bajo la cuenta/proyecto correspondientes. Las colas anteriores a v1.7.3 sin ese registro se omiten por defecto. Para incluirlas se necesita arrancar con `--cloud-include-history`; el aviso lo explica y hay que aceptar ese alcance. Una sesión marcada como revocada continúa excluida.

## Comprobaciones

74 pruebas Python + 40 JavaScript (114): cierre/denegación/error de aviso, alcance por destino, ausencia de autenticación/envío/cola sin permiso, retirada durante una transferencia, bloqueo antes de indexar y en el cierre, persistencia de revocación e histórico. Chromium verificó el estado del permiso y el botón de retirada. Se probó el conector sin escritorio ni terminal: bloquea subidas y rechaza reanudar por HTTP. Las decisiones de la ventana se simularon en estas pruebas; falta comprobar visualmente el diálogo en un escritorio Windows real.
