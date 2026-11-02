# v1.7.2 · Telemetría de misión

[Proyecto](../README.md) · [Conectar KSP](KSP_MAPA.md) · [Supabase](KSP_NUBE.md) · [Bitácora de pruebas](KSP_COLABORADORES.md)

El servidor local mide el equipo donde corre KSP y registra datos de la partida. Render sirve el sitio y prepara rutas; no puede medir tu PC ni leer KSP remotamente por sí solo. Las evidencias se envían del conector a tu Supabase privado si está configurado e iniciado con tu usuario.

## Actualizar y empezar

Desde el repositorio actualizado, en el PC del juego:

```powershell
.venv\Scripts\python.exe -m pip install -r integrations/requirements-ksp.txt
.venv\Scripts\python.exe integrations/ksp_cloud.py configure-project
.venv\Scripts\python.exe integrations/ksp_cloud.py login
.venv\Scripts\python.exe integrations/ksp_cloud.py doctor
.venv\Scripts\python.exe integrations/ksp_server.py
```

Si ya configuraste el proyecto y tienes sesión válida, basta con instalar las dependencias nuevas y reiniciar el conector. En macOS/Linux usa `.venv/bin/python`. Al iniciar el servidor, elige Permitir esta sesión o No permitir en el aviso de escritorio. La denegación conserva el diagnóstico local y bloquea envíos; [detalles](KSP_CONSENTIMIENTO.md). Activa kRPC en KSP 1 y abre `http://localhost:7173/ksp-map.html`; conecta el juego para ver **Estado del equipo y vuelo**. El conector solo escucha en loopback y no envía controles al juego.

## Datos y frecuencia

| Fuente | Datos | Frecuencia nominal |
| --- | --- | --- |
| Equipo con psutil | CPU total, RAM usada/total/porcentaje, disco libre/total del volumen de evidencias, memoria del conector | 5 s, hilo separado de kRPC |
| Procesos KSP | Detección y memoria/CPU de hasta cuatro procesos cuyos nombres coinciden con KSP 1 | 5 s; primera lectura CPU sin valor hasta disponer de intervalo |
| Juego, solo lectura | Posición, rumbo, velocidad, altura superficial y tiempo de lectura RPC | Bucle básico existente, hasta 5 lecturas/s antes de latencias |
| Vuelo y órbita | Altitud media, velocidades vertical/horizontal, g, pitch/roll, masa/empuje, situación, apoapsis/periapsis, periodo, inclinación, excentricidad y tiempos orbitales | 1 s nominal, compartiendo los objetos de vuelo existentes |
| Recursos y reloj | LiquidFuel, Oxidizer y ElectricCharge stock si están disponibles; tiempo universal del juego | Dentro del diagnóstico de vuelo |
| Navegador | Número, tiempo total y máximo de repintados/solicitudes HTTP medidos por el mapa | Resumen cada 30 s y al cerrar; solo en modo KSP conectado |

No se escanean recursos de mods arbitrarios ni se registra una lista de aplicaciones ajenas a KSP. Los datos ausentes se guardan como `null`; no equivalen a cero. CPU del proceso puede superar el 100% por uso de varios núcleos. **No se dispone de FPS fiables de KSP mediante kRPC**, ni se confunden tiempos de repintado web con FPS del juego. No se prometen medidas de GPU, temperatura o rendimiento del casco.

Si falta psutil o se deniega una lectura, el conector continúa con indicadores parciales. Los procesos se reconocen por nombre: instalaciones personalizadas o envoltorios pueden impedir su detección aunque kRPC esté conectado. Detección de proceso no certifica que el juego responda bien.

## Archivos y resumen

La sesión local en `ksp-sessions/<sesión>/` conserva:

- `telemetry.jsonl`: muestras básicas de juego, con diagnóstico adicional cuando esté disponible.
- `computer.jsonl` y `flight.jsonl`: mediciones con marcas de tiempo.
- `events.jsonl`: conexiones, pérdida de datos, actividad del mapa y eventos de navegación.
- `analysis.json`: máximos, conteos, situaciones de vuelo y recomendaciones por reglas. Se actualiza como máximo una vez por minuto por las mediciones, y en cierres/sincronizaciones de vista.
- Regiones, misiones y logs del conector; KSP.log/Player.log solo si configuraste sus rutas explícitamente.

El ZIP utiliza una lista permitida de archivos y mantiene el límite local de registro existente. La tabla privada `ksp_sessions` incorpora el resumen en `diagnostic_summary`, y `stopped_at` al finalizar el conector. La migración se aplicó al proyecto configurado; para otro proyecto usa el SQL actualizado de instalación. El resumen y los ZIP están sujetos a los permisos por usuario/administrador ya configurados.

Las recomendaciones avisan de CPU/RAM elevadas, lentitud de RPC/HTTP o repintados y problemas de conexión. Son indicadores para comparar sesiones/versiones y decidir cambios con pruebas. **No prueban causalidad, no entrenan un modelo y no cambian el código automáticamente.** Las pérdidas de conexión también pueden deberse a cambios de escena o al cierre normal del juego.

## Envíos durante el uso y al terminar

La subida periódica conserva el intervalo configurado, por defecto 300 s. Al ocultar/cerrar la vista KSP o perder kRPC se solicita un envío de las evidencias actuales, sin detener el juego ni el servidor. Los eventos de cierre del navegador son de mejor esfuerzo: un cierre forzado puede impedir la solicitud.

Al detener el conector con Ctrl+C o SIGTERM se cierra el muestreo, se guarda el resumen y se intenta una última sincronización. Se espera hasta 15 s al trabajador. Si no puede confirmarla, quedan las evidencias y el ZIP pendiente para reintentar al próximo arranque, con la misma cuenta/proyecto. Si había una instantánea anterior pendiente, se intenta completarla y después la final. Esto no garantiza envío si se corta la luz o se mata el proceso.

**Pausar subida y retirar/denegar el permiso se respetan también al salir.** La copia local permanece incluso después de un envío correcto. El cierre de la pestaña no apaga el conector: la recogida continúa mientras el servidor local esté ejecutándose. Ciérralo cuando termines la sesión de KSP.

## Privacidad y desactivación

No se recopilan nombres de usuario/equipo, IP, números de serie, comandos de procesos, capturas, teclas ni archivos personales. Sí se conservan nombres/identificadores del vehículo y del cuerpo como parte de la telemetría del juego. Los logs externos elegidos pueden contener texto propio: revísalos antes de compartirlos.

```powershell
# Navegación con diagnóstico adicional desactivado:
.venv\Scripts\python.exe integrations/ksp_server.py --no-computer-stats --no-flight-diagnostics
# Conservar los registros locales sin subir a Supabase:
.venv\Scripts\python.exe integrations/ksp_server.py --no-cloud-upload
```

`--no-session-log` evita el registro de disco y la subida; la telemetría necesaria para navegar continúa en memoria. Nunca pongas contraseñas o claves secretas en el repositorio ni en el navegador.

## Validación

66 pruebas Python y 40 JavaScript, con proveedores de equipo/kRPC/Supabase simulados, verifican permisos de lectura, campos ausentes, privacidad, exportación, pausa, cierre y persistencia ante fallo de red. Chromium verificó indicadores de equipo/vuelo y petición de envío al salir, con datos de prueba. Se comprobaron las columnas del proyecto Supabase real. Falta medir el coste en el PC real de KSP y confirmar su primer ZIP con mediciones reales. Registra esas pruebas en `docs/KSP_COLABORADORES.md`.
