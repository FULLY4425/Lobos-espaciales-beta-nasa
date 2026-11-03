# Revisión de seguridad KSP · v1.7.6

Revisión del código de la web, conector, registro/subida de evidencias y permisos actuales de Supabase, el 2 de noviembre de 2026 (México). No equivale a una auditoría independiente, prueba de penetración completa ni garantía de ausencia de puertas traseras.

## Hallazgos corregidos

| Problema | Corrección y evidencia |
| --- | --- |
| El conector validaba origen solo en algunas escrituras y no restringía Host | Validación previa a todas las rutas: Host debe ser localhost/loopback con el puerto real; origen HTTP local permitido; origen externo/null y Sec-Fetch-Site cross-site rechazados. Pruebas GET/export/POST con Host adversario. Esto mitiga DNS rebinding. No autentica otros programas del mismo usuario en el PC. |
| HEAD heredado no usaba la restricción de GET; enlaces dentro de docs podían apuntar a rutas privadas | Una misma validación de archivos para GET y HEAD, incluyendo la ruta real del enlace. Pruebas de configuración privada, ruta codificada y symlink a auth.json. |
| Lecturas HTTP podían quedar esperando sin límite de socket | Timeout de 15 segundos. No constituye protección completa frente a DoS distribuido ni limita todos los trabajos de cálculo. |
| Errores de envío de eventos del navegador se descartaban | Lote con identificador estable, un envío simultáneo, reintento a 5 segundos; deduplicación de los últimos 512 lotes en la instancia receptora. Cola acotada, conservando el diario del navegador como alternativa local. |
| El servidor web de desarrollo escuchaba toda la red por defecto | Sin PORT escucha 127.0.0.1; Render con PORT mantiene 0.0.0.0. BIND_HOST permite configuración explícita. El conector KSP permanece siempre en 127.0.0.1. |

Se añaden `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer` y `X-Frame-Options: SAMEORIGIN`, preservando el mapa integrado del mismo origen.

## Qué se comprobó

- HTTPS hacia Supabase con validación TLS normal de Python y rechazo de redirecciones HTTP: no se reenvían tokens a una URL redirigida. El perfil público contiene una clave publicable, no una clave de servicio.
- El conector se conecta a kRPC en 127.0.0.1 y usa lecturas; no se encontraron comandos de pilotaje, ejecución remota de órdenes o descarga/ejecución de código en los módulos de integración revisados.
- Lista permitida de archivos ZIP, exclusión de symlinks y archivos de autenticación, límites de tamaño y rutas propias por identidad. Los logs de juego opcionales pueden contener información personal: revisarlos antes de compartir.
- SHA-256 del ZIP pendiente antes de enviar; la pasarela verifica el hash contra su nombre. La cola conserva el mismo archivo hasta indexarlo. Pruebas simulan red caída, fallo del índice, recepción sin respuesta y ZIP alterado. Las dos primeras ya existían; se añaden las dos últimas.
- Consulta real de Supabase: RLS activado en sesiones, probadores y tres tablas privadas; anon/authenticated sin permiso de ejecutar la función SQL de la pasarela, usuarios sin lectura de devices y bucket ksp-evidence privado con límite de 50 MiB. La Edge Function valida la identidad de cada operación; su registro inicial público está sujeto a cuotas, no concede permisos de administrador.
- Búsqueda de patrones de claves privadas, claves secretas Supabase, tokens GitHub y JWT en archivos de texto actuales versionados: sin coincidencias. No inspecciona todo el historial Git ni garantiza detectar secretos con formatos distintos.
- `pip-audit` sobre requirements-ksp.txt: krpc 0.7.0, psutil 7.0.0 y protobuf 7.36.2 resuelto, sin vulnerabilidades conocidas en el catálogo consultado. No certifica mods, binarios del juego, navegador ni sistema operativo. La versión de protobuf en el PC del probador puede ser distinta; repetir allí el análisis.

Validación final: 90 pruebas Python, 49 JavaScript y prueba automatizada en Chromium del mapa, globo, rutas, clima, HUD y diseño compacto. Las pruebas HTTP de seguridad se ejecutaron con acceso a loopback; no se omitieron por restricciones del entorno.

## Pérdida de paquetes y límites de entrega

HTTPS funciona sobre TCP, que retransmite paquetes perdidos; el programa no necesita UDP para subir los ZIP. Esto no garantiza que una petición finalice: los cortes y timeouts dejan pendiente el archivo para reintento. El hash detecta alteración del ZIP; no recupera muestras que nunca se leyeron del juego.

No se midió pérdida, latencia o calidad de Wi-Fi del PC del colaborador: no hay acceso a su conexión. No se afirma «0 % de pérdida». La telemetría es muestreo de lectura, no un registrador continuo garantizado.

Los eventos del mapa reintentan mientras la página sigue viva. Un cierre abrupto, la cola llena, un reinicio del conector o caída del navegador pueden dejar eventos solo en el diario local o perder los aún no guardados. La deduplicación es temporal por instancia, no una transacción durable entre navegador y disco. El ZIP/índice sí conserva su cola local durable. Conservar respaldos del disco; un disco roto no se recupera con reintentos.

Para comprobar la conexión real, registrar la hora del fallo y adjuntar el estado de subida, connector.log, analysis.json y la sesión a la bitácora. Comparar Internet por cable frente a Wi-Fi y comprobar si el archivo pendiente acaba indexado. Los pings por sí solos no prueban la entrega de HTTPS y algunos servidores bloquean ICMP.

## Pendientes y límites de seguridad

- Supabase informa **protección de contraseñas filtradas desactivada** para Auth. Revisar su disponibilidad/configuración en [Password security](https://supabase.com/docs/guides/auth/password-security#password-strength-and-leaked-password-protection). No se cambió el plan ni se afirma que esta opción ya esté activada.
- Los tres avisos informativos de [RLS sin políticas](https://supabase.com/docs/guides/database/database-linter?lint=0008_rls_enabled_no_policy) corresponden a tablas del esquema privado, deliberadamente inaccesibles a clientes; no deben abrirse con una política pública.
- El alta sin cuenta es un punto público que puede abusarse para agotar cuotas. Los límites existentes reducen el consumo, pero no sustituyen WAF/CAPTCHA ni eliminan ataques de denegación de servicio.
- Un programa malicioso que ya se ejecuta con el usuario del PC podría leer sus tokens o llamar al puerto local. El conector no ofrece aislamiento frente a malware local. No abrir puertos kRPC en el router ni exponerlos a Internet; comprobar el firewall del PC y restringir kRPC a loopback en su configuración. No se inspeccionó ese firewall.
- Windows usa permisos de la cuenta para proteger los archivos locales; no se validaron sus ACL ni se migraron tokens al almacén de credenciales del sistema. No compartir .ksp-cloud.
- ZIP recibidos son datos no confiables. Su validación estructural y hash no certifican que una prueba sea auténtica ni detectan todo contenido malicioso en un log. No ejecutar archivos extraídos.

Mantener activo el consentimiento; actualizar y reiniciar el conector para aplicar estas correcciones. No afecta al permiso de administración de evidencias del propietario.
