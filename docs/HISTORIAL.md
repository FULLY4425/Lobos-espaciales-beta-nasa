# Historial de actualizaciones

[Volver al proyecto](../README.md) · [Mapa KSP y configuración](KSP_MAPA.md)

## v1.7.10 «Ruta atenta» — 2 de noviembre de 2026 (hora de México)

- Revisión cruzada de las dos bitácoras nuevas de Claude, sus ZIP y cinco sesiones reales en Supabase. Llegadas/tormenta confirmadas; se conservan las evidencias originales.
- Integración de PR #4: estáticos revalidados con `no-cache`; API privada conserva `no-store`.
- Desvío por distancia configurable (75 m por defecto), persistencia de 1,5 s y espera de 10 s entre recálculos. Registro de salida de cobertura aunque no haya una misión activa o la guía esté bloqueada.
- Coordenadas/radio de la zona de tormenta y propuesta explícita de punto conectado; no cambia destinos automáticamente. Pausa de guía con estado de vuelo real incluso sobre mapas de celdas gruesas.
- Métricas separadas para peticiones correctas, fallidas, canceladas y timeout; menor espera potencial en TCP local. Los datos históricos no permiten atribuir una causa única a los picos.
- Calidad del resumen anotada en Supabase y en subidas nuevas; cuatro resúmenes históricos desfasados se identifican, sin editar muestras ni ZIP. Edge Function actualizada manteniendo sus controles de acceso.
- 103 pruebas Python y 57 JavaScript; navegador y caché 200/304. La prueba de symlinks se omite explícitamente cuando el sistema no permite crearlos, manteniendo las demás comprobaciones. [Detalle](KSP_REVISION_V1710.md).

## v1.7.9 «Siempre al día» — 2 de noviembre de 2026 (hora de México)

- Comprobación de la versión oficial de GitHub al iniciar y cada hora, con revisión fijada por SHA, HTTPS, límites de respuesta y tiempos de espera. Sin conexión, el programa sigue funcionando.
- Aviso en el mapa y aviso inicial de Windows que ofrece instrucciones; no instala ni ejecuta código descargado automáticamente. Opción `--no-update-check`.
- Actualizador explícito para clones Git: bloqueo compartido con el conector, origen oficial HTTPS, copia limpia, revisión/version verificadas y avance rápido únicamente; sin reset, clean, stash o hooks de repositorio.
- Lanzador Windows `actualizar-ksp.cmd`, instrucciones para ZIP y mod, y pruebas de versiones, red caída, bloqueo y protección de cambios locales. [Guía](KSP_ACTUALIZAR.md).

## v1.7.8 «Vientos de Duna» — 2 de noviembre de 2026 (hora de México)

- Escenario de viento con ráfagas, dirección y visibilidad; escenarios de polvo/tormenta con valores explícitos de entrenamiento. Flechas 2D/3D y franjas visuales discretas; modo ligero y HUD limitan los efectos.
- Rutas, ETA, voz y evidencias incluyen el escenario y viento. Se conserva el recálculo ante cambios y la restricción local de tormenta.
- Puente local de escenario hacia un mod opcional, protegido por las mismas comprobaciones de Host/origen y validación de parámetros. No da órdenes de pilotaje.
- Código C# y compilador/instalador Windows del mod de clima para KSP 1.12.x: polvo visual, ráfagas y fuerzas incrementales limitadas, desactivadas por defecto; interfaz propia y seguimiento opcional del mapa.
- 95 pruebas Python, 52 JavaScript, navegador y análisis sintáctico C#. **Pendientes:** compilación con bibliotecas reales de KSP y ensayo del mod dentro del juego. [Guía](KSP_CLIMA.md).

## v1.7.7 «Datos en acción» — 2 de noviembre de 2026 (hora de México)

- Revisión de dos sesiones reales recibidas en Supabase: máximo de repintado de 162 ms en v1.7.5 y diferencia de 33 muestras entre índice y resumen en v1.7.4. La prueba sintética se excluye del análisis del juego.
- Modo ligero conserva geometría, objetivos y navegación; reduce la resolución visual de región/atlas. El dibujo 3D reutiliza el tamaño del lienzo y la proyección mientras no cambien dimensiones o densidad de píxeles.
- Medias, p95 reciente y número de repintados de más de 50 ms, con separación por vista. El resumen diferencia un pico aislado de coste repetido y muestra métricas disponibles en KSP Map.
- Exportación de resumen y manifiesto bajo una misma instantánea; copia independiente de contadores para evitar cambios durante la compresión.
- Validación: 92 pruebas Python, 51 JavaScript y recorrido de navegador. No se afirma mejora medida en el PC del colaborador; [análisis y protocolo](KSP_ANALISIS_SUPABASE.md).

## v1.7.6 «Conexión protegida» — 2 de noviembre de 2026 (hora de México)

- Protección del conector contra Host externo, DNS rebinding y solicitudes de origen cruzado, incluidas lecturas y exportación.
- GET/HEAD comparten restricciones de archivos y destinos de enlaces simbólicos; cabeceras nosniff, referrer y marcos del mismo origen; tiempo de lectura limitado. El servidor web local escucha loopback por defecto; Render conserva su puerto público.
- Reintentos acotados de eventos del navegador y deduplicación por lote/instancia. Pruebas de corte tras recepción del ZIP y de archivo pendiente alterado.
- Auditoría de dependencias Python sin vulnerabilidades conocidas en las versiones resueltas, consulta real de permisos y avisos Supabase y revisión de patrones de secretos. Alcance y pendientes en [SEGURIDAD_KSP.md](SEGURIDAD_KSP.md).

## v1.7.5 «Guía de precisión» — 2 de noviembre de 2026 (hora de México)

- Correcciones basadas en el reporte real de Firefox: extremos exactos de ruta en celdas grandes, espera de cambios de escena sin conexiones en ráfaga y recálculo solo ante un escenario distinto.
- Ciclo climático opcional con intervalo visible y registro de activación; eventos de llegada, paso de largo, conducción y salida de cobertura.
- Caché de relieve/curvas/clima y menos dibujo oculto; aviso para abrir localhost al conectar el juego desde la web remota.
- Se conservan mapas, navegación, diagnóstico, consentimiento y recepción sin cuenta de v1.7.4.
- Validación y pruebas reales aún pendientes: [revisión del reporte](KSP_REVISION_V175.md).

## v1.7.4 «Compartir sin cuenta» — 2 de noviembre de 2026 (hora de México)

- Registro automático de una identidad técnica por instalación después del consentimiento. Los probadores no necesitan correo, contraseña ni alta manual en `ksp_testers`.
- Pasarela privada de evidencias con verificación de identidad, aislamiento entre instalaciones, validación de ZIP y cuotas. Las claves de administración permanecen en el servidor.
- Se conserva Permitir / No permitir y la retirada. Cerrar sesión pausa el registro automático hasta una nueva aceptación explícita.
- Se mantienen cuentas manuales, mapas, navegación, diagnóstico y archivos locales. No se añade una APK.
- Validación: 81 pruebas Python, scripts JavaScript y compilación; registro y subida sintéticos contra Supabase, rechazo del acceso entre instalaciones. Esto no certifica una sesión real de KSP ni la ventana en Windows.
- Guía: [Compartir sin cuenta](KSP_SIN_CUENTA.md).

## v1.7.3 «Permiso para compartir» — 2 de noviembre de 2026 (hora de México)

- Ventana de consentimiento del conector con destino y categorías de datos, Permitir esta sesión y No permitir. Cierre, error o ausencia de interfaz no autorizan compartir; alternativa de terminal interactiva con aceptación explícita.
- Permiso limitado al arranque y proyecto; no se recuerda una aceptación permanente ni sustituye Auth/RLS. El mapa y los registros locales funcionan al denegar.
- Bloqueo de autenticación de subida, cola automática, reintentos, acciones de reanudación y sincronización final sin consentimiento. Control de retirada en KSP Map y marcas persistentes para no reenviar sesiones revocadas.
- Colas heredadas sin registro de consentimiento omitidas por defecto; alcance de histórico explícito en el aviso. No se borran datos ya enviados ni se promete cancelar una petición en curso.
- Validación: 74 pruebas Python + 40 JavaScript (114), navegador con permiso/retirada y conector real sin escritorio. Falta verificación visual en Windows real. Se mantienen las funciones anteriores.
- Guía: [KSP_CONSENTIMIENTO.md](KSP_CONSENTIMIENTO.md).

## v1.7.2 «Telemetría de misión» — 2 de noviembre de 2026 (hora de México)

- Diagnóstico de equipo cada 5 s en un hilo independiente: CPU, RAM, disco de evidencias, memoria del conector y procesos de KSP de una lista permitida. Sin nombres de usuario/equipo, direcciones IP, comandos, capturas ni listado de otras aplicaciones.
- Datos adicionales de vuelo cada segundo, con valores ausentes explícitos: altitud, velocidad vertical/horizontal, orientación, fuerza g, masa/empuje, órbita, recursos stock y tiempo universal. Solo lecturas; se reutilizan los objetos de vuelo de la telemetría básica.
- Estado de equipo/vuelo y recomendaciones en KSP Map; estadísticas del repintado/peticiones del navegador enviadas periódicamente y al cerrar la vista.
- Archivos `computer.jsonl`, `flight.jsonl` y `analysis.json` en el ZIP privado; resumen por reglas y fecha de cierre en el índice Supabase, conservando RLS y permisos existentes. Migración de columnas aplicada y verificada.
- Solicitud de envío al ocultar/cerrar el mapa o perder la conexión del juego; intento final durante cierre ordenado del conector, con espera limitada y cola local durable. Se respeta la pausa manual.
- psutil 7.0.0 fijado como dependencia del conector; indicadores parciales si falta. Opciones para desactivar estadísticas del equipo o vuelo adicional. FPS de KSP no disponible: no se inventan métricas ni causas.
- Validación: 66 pruebas Python + 40 JavaScript (106), incluyendo privacidad, lecturas sin control, resumen/exportación, envío final, pausa y fallo de red. Chromium con datos simulados: indicadores, estado de vuelo, resumen y envío al salir. Pendientes mediciones y primer envío desde el PC real de KSP.
- Guía: [KSP_DIAGNOSTICO.md](KSP_DIAGNOSTICO.md).

## v1.7.1 «Evidencias de Duna» — 2 de noviembre de 2026 (hora de México)

- Integración del servidor de evidencias Supabase en la serie 1.7, conservando todas las funciones de Duna y Render. Actualización del estado del proyecto existente, sin crear otra cuenta ni exponer credenciales.
- Comando `ksp_cloud.py doctor` con comprobaciones independientes de autenticación, usuario autorizado, índice de sesiones y listado de su carpeta. Diagnóstico sin subir archivos, con código de salida y recomendaciones por etapa.
- SQL de verificación de bucket privado, RLS, funciones y políticas; ejemplo de configuración deshabilitado y sin claves reales para el proyecto del propietario.
- Validación: 58 pruebas Python y 40 JavaScript (98). Pruebas nuevas de diagnóstico correcto, falta de Auth, permisos/esquema y fallo de Storage, sin revelar tokens ni leer evidencias.
- Activación real: migración aplicada, nueve comprobaciones estructurales aprobadas, autorización del propietario confirmada y prueba transaccional de aislamiento entre probadores/administrador, revertida sin dejar datos de prueba. Funciones privilegiadas en esquema privado y RPC público invocador.
- Perfil público del proyecto y comando `configure-project` para configurar el PC sin copiar claves manualmente. La API bloquea el acceso anónimo; queda pendiente el primer envío real de archivos desde el conector.

## v1.7.0 «Duna Explorador» — 1 de noviembre de 2026 (hora de México)

- Publicación del PNG completo original de SCANsat, metadatos y las 529220 alturas del CSV, conservando huecos y cobertura del 83.5%. Página principal con atlas completo 2D, globo de Duna 3D y apertura de regiones a partir de coordenadas seleccionadas.
- Capas de textura, elevación y mezcla; objetivos documentados de las pruebas reales con filtro, evidencias y posibilidad de añadirlos al recorrido, además de destinos propios persistentes. No se transfieren objetivos ChemCam a Duna.
- Cámaras panorámica, sobrevuelo, seguimiento y superficie; vuelo orbital, explorador virtual visible y movimiento WASD sin conexión al juego. Ensayo de rutas con avance y velocidad de reproducción, reutilizando la guía de voz.
- Escenarios de polvo y tormenta hipotéticos, visibilidad y zona restringida para A*, conectividad y recálculo conservando destinos pendientes. Se mantienen separados de la telemetría y no modifican el clima de KSP.
- HUD compacto y acceso a maqueta WebXR de la región con sus propias alturas/textura, sin usar la ortofoto de Marte. Alternativa explícita si el dispositivo no ofrece AR.
- Conservación de conexión kRPC de solo lectura, evidencias, modos anteriores y bitácora como documento. Archivos completos descargables y generador reproducible del atlas desde el CSV archivado.
- Validación: 52 pruebas Python y 40 JavaScript (92), navegador con atlas/globo, selección de región, capas, objetivos, cámaras, restricciones/recálculo, recorrido virtual, HUD, alternativa AR y pantalla compacta. Pendientes la prueba de esta versión en KSP real y la maqueta en hardware WebXR.
- Guía: [DUNA_EXPLORADOR.md](DUNA_EXPLORADOR.md).

## v1.6.1 «Duna al inicio» — 1 de noviembre de 2026 (hora de México)

- La página principal abre directamente el mapa real de Duna exportado en la sesión Travesía, con alturas y textura, en 3D. No requiere seleccionar el catálogo ni cargar archivos manualmente.
- Marte queda como una opción secundaria, con sus funciones conservadas. El enlace al mapa independiente abre la misma región.
- Corrección de la vista inicial de v1.6.0, que todavía mostraba Marte por defecto.

## v1.6.0 «Atlas de relieve» — 1 de noviembre de 2026 (hora de México)

- Espacio KSP dentro de la página principal, con el mismo mapa nativo independiente y pausa de consultas/guía al ocultarlo. Se conserva el explorador original de Marte, globo, caminatas, clima simulado, voz, HUD y AR.
- Catálogo de tres regiones reales de Duna: las dos regiones del rover en la sesión Travesía (289/289 muestras) y la región previa de SCANsat (280/289), todas con muestreo de 2 km.
- Proyección de texturas por cuerpo, radio y coordenadas; máscaras de cobertura derivadas de los CSV reales, incluido el escaneo de 529220 muestras (83.5% global). Carga de PNG/JPG/WebP propios con metadatos validados, sin subida automática.
- Relieve KSP con colores de elevación, curvas, malla, orientación cardinal, etiquetas y escala vertical visual 1×/3×/5×. Alturas, distancias, pendientes y cálculo de rutas mantienen sus valores físicos.
- Localización y seguimiento del vehículo, rumbo y coordenadas, cámara libre y selección de coordenadas/altura sobre el terreno 3D. Reutilización de geometría y repintado bajo demanda.
- Capas de fotografía, alturas y mezcla, curvas y leyenda en el explorador de Marte. La textura mars-global sigue siendo contexto visual de Marte; no se presenta como terreno exportado del juego.
- Sincronización de los registros reales nuevos del equipo sin reescribir sus resultados. La bitácora continúa como documento.
- Validación: 47 pruebas Python + 36 JavaScript (83), construcción de distribución y Chromium con mapas reales archivados/telemetría simulada: catálogo, texturas, 2D/3D, controles, interfaz compacta, pausa, métricas de ruta, llegada, pérdida/recuperación y evidencias. Falta comprobar esta visualización v1.6.0 en KSP real y su voz audible.
- Guía: [KSP_MAPAS_3D.md](KSP_MAPAS_3D.md).

## v1.5.0 «Evidencias KSP» — 1 de noviembre de 2026 (hora de México)

- Cliente opcional de Supabase con autenticación individual de probadores, renovación de sesión y rechazo de claves de administrador en el conector.
- Subida en segundo plano, ZIP pendiente durable, reintentos, índice por sesión y limpieza de instantáneas anteriores tras confirmación; se conserva la copia local.
- Controles de pausa, reanudación y envío manual en el mapa local, con estado y sin credenciales en el navegador.
- SQL para bucket privado, usuarios autorizados, índice de sesiones y políticas de acceso por usuario/administrador.
- Inclusión explícita de KSP.log/Player.log mediante rutas elegidas, con límites y recortes declarados; exclusión de archivos privados de configuración/autenticación.
- Registro persistente de metadatos y compresión fuera del bloqueo de telemetría. Se mantienen los modos anteriores y la bitácora como documento.
- Validación: 45 pruebas Python y 28 JavaScript (73 en total), más navegador con Supabase simulado. Falta crear el proyecto del propietario, aplicar el SQL y verificar el primer envío y aislamiento reales. No se ha enviado información a una cuenta externa sin esa configuración.
- Guía: [KSP_NUBE.md](KSP_NUBE.md). Esta entrada usa la fecha local de México; las anteriores conservan sus fechas registradas.

## v1.4.0 «Travesía KSP» — 2 de noviembre de 2026

- Avisos anticipados de velocidad cerca de giros/destino y del borde de cobertura; umbrales ajustables, sin enviar controles al vehículo.
- Llegada por distancia física y parada continua de 3 s; detección de paso de largo y separación entre velocidad estimada y aviso de conducción.
- Capas 2D de conectividad, pendiente y elevación, consulta por celda y recarga de región conservando destinos pendientes.
- Cola de voz con prioridades y caducidad, estado de reproducción y corrección de mensajes de error/conexión.
- Pausa deliberada al ocultar la vista, recuperación con datos frescos y diferenciación frente a una desconexión real.
- Registro local automático del conector con sesiones únicas, telemetría, regiones, rutas, eventos y ZIP; sesiones del navegador recuperables y descargables con límites y contadores explícitos.
- Diagnóstico de versión, instancia y puertos; mensaje claro ante puerto ocupado. Métricas de CPU de repintado y consultas HTTP en el paquete del navegador.
- Incorporación del análisis de las pruebas reales de Duna y SCANsat; reproducción automatizada del CSV/región/ruta real archivado, sin inventar evidencias.
- Mensaje explícito para vehículos en vuelo/fuera de cobertura, bloqueo del cálculo terrestre en ese contexto y descripción de la fuente importada corregida.
- Aclaración del log del conector antiguo ausente.
- Validación: 35 pruebas Python y 28 JavaScript (63 en total), más navegador con telemetría simulada. La conducción con esta versión y con un rover sobre el mapa SCANsat siguen pendientes.
- Guía: [KSP_TRAVESIA.md](KSP_TRAVESIA.md). Se mantienen las funciones previas de Marte, KSP, HUD y AR; la bitácora permanece como documento.

## v1.3.1 «Bitácora KSP» — 2 de noviembre de 2026

- La bitácora pasa a ser únicamente un documento en `docs/KSP_COLABORADORES.md`, por preferencia del equipo.
- Retirada de la página de reportes, sus scripts, estilos, formulario de issues y pruebas específicas.
- Plantilla detallada para experiencias, logs, resultados, errores, mejoras y sugerencias; registro compartido mediante commits o pull requests.
- Unificación de todo el contenido de `VALIDACION.md` en la bitácora, junto con la prueba real de KSP 1.12.5, conservando mediciones, errores, comprobaciones y pendientes. Retirada del archivo separado y actualización de sus enlaces.
- Accesos del mapa y HUD dirigidos al documento. Se conservan las funciones del proyecto de Marte, mapas KSP, conector, HUD y AR.
- Comprobación de enlaces y distribución; la suite vigente conserva 49 pruebas.

## v1.3.0 «Bitácora KSP» — 1 de noviembre de 2026

- Apartado exclusivo para experiencias de pruebas reales de la integración KSP, accesible desde mapa y HUD.
- Informe con entorno, versiones, mods, pasos, experiencia observada, errores, mejoras y matriz de comprobaciones sin marcar pruebas como aprobadas por defecto.
- Revisión local de archivos de logs, extractos, descarga de textos completos y paquete JSON; diagnóstico puntual del conector.
- Formulario GitHub con confirmación de alcance y campos obligatorios. Publicación y adjuntos confirmados por el probador con su cuenta, y seguimiento mediante issues/comentarios persistentes.
- Listado bajo demanda de reportes KSP, con acceso al historial completo y alternativa si falla la API pública.
- Guía de colaboradores, recopilación de logs y diferencias entre preparar, descargar y publicar.
- Se conservan Marte, mapas, integración KSP, HUD y AR. No se añade almacenamiento efímero de reportes en Render.
- Validación: 31 pruebas Python y 26 JavaScript (57 en total), más comprobaciones de navegador con archivos y respuestas de prueba; sin publicar informes ficticios.

## v1.2.0 «Atlas KSP» — 1 de noviembre de 2026

- Investigación de kRPC, SCANsat, Sigma Cartographer y KerbalMaps, con fuentes y diferencias entre imágenes y alturas documentadas.
- Descarga y carga de regiones `ksp-terrain-v1` de kRPC; reutilización con telemetría del mismo cuerpo.
- Convertidor de CSV de SCANsat por regiones, con lectura línea a línea, muestras cercanas, máscara opcional de océano y huecos bloqueados sin interpolación.
- Preparación de rutas sobre mapas importados con salida manual y sin juego, conservando 2D/3D, destinos, exportación y el servidor Python.
- API acotada de validación y planificación de mapas, con identidad derivada del contenido y procedencia declarada explícita.
- Corrección del rumbo: lectura en el marco de superficie de kRPC, conservando posición y velocidad en el marco del cuerpo.
- Conservación de las funciones anteriores de Marte, KSP, HUD y AR.
- Validación: 31 pruebas Python y 18 JavaScript (49 en total); navegador con mapas y telemetría de prueba. El CSV exportado por una partida y la corrección del rumbo frente a la navball requieren validación real.

### Registro de prueba real incorporado entre versiones

El [merge cbdc7ce](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/commit/cbdc7ce) añadió la prueba parcial del HUD anterior con KSP 1.12.5 y kRPC 0.7.0: conexión, conducción, avisos y recálculo; también registró el error de rumbo abordado en v1.2.0. Es una prueba del HUD anterior, no del mapa nativo nuevo. Véase la [sesión en la bitácora](KSP_COLABORADORES.md#2026-11-01--prueba-real-del-hud-ksp-1125).

## v1.1.0 «Horizonte KSP» — 1 de noviembre de 2026

Esta versión convierte el proyecto en un explorador de Marte y una guía de superficie para **KSP 1**, conservando las funciones anteriores. Implementación principal: [92c7046](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/commit/92c7046).

### Añadido

- Mapa KSP independiente en `/ksp-map.html`, con vistas 2D y relieve 3D.
- Lectura de coordenadas, radio y alturas del cuerpo activo mediante kRPC; muestreo por bloques con progreso y cancelación.
- Destinos guardados por cuerpo, planificación según pendiente y agua, indicaciones por voz y recálculo automático desde la posición actual.
- Importación de destinos del mismo cuerpo y exportación de misiones con coordenadas, ruta y procedencia de datos.
- Demo pública marcada como sintética, sin necesidad de instalar KSP.
- Guía de configuración, arquitectura y validaciones del nuevo mapa.
- Número y nombre de versión en el README, la interfaz y `package.json`, junto con este historial.

### Conservado

Explorador de Marte con HiRISE y ChemCam, globo, objetivos propios, astronautas, voz, recálculo, escenarios de polvo, HUD de entrenamiento y AR experimental. El APK y la instalación PWA siguen retirados.

### Comprobado y pendiente

42 pruebas automatizadas aprobadas, comprobaciones de navegador y contrato HTTP con telemetría simulada. La prueba dentro de una partida real de KSP sigue pendiente. El juego requiere el conector local; Render ofrece la web y la demo. La guía es de superficie, no controla el vehículo y no proporciona navegación orbital ni meteorología real del juego.

## Actualizaciones anteriores

Antes de v1.1.0, `package.json` indicaba **1.0.0**, pero los cambios no tenían versiones individuales ni nombres oficiales. Se registran aquí por fecha y commit, con títulos descriptivos añadidos al preparar este historial. No representan publicaciones numeradas retrospectivas.

Orden: de la actualización anterior más reciente a la primera.

| Fecha | Actualización | Cambios | Commit |
| --- | --- | --- | --- |
| 2026-11-01 | Proyecto web sin APK | Retirada del APK, Android y mecanismos de instalación PWA; conservación del proyecto web, KSP, AR y las funciones de Marte. | [0041b9a](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/commit/0041b9a) |
| 2026-11-01 | Calibración y clima | El HUD de entrenamiento exige calibración KSP antes de aplicar un cambio de escenario meteorológico. | [35b8ce7](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/commit/35b8ce7) |
| 2026-11-01 | Reproducción tras recálculo | Corrección para permitir reanudar la reproducción tras recalcular sobre la misma geometría de malla. | [aeeea9a](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/commit/aeeea9a) |
| 2026-11-01 | Reanudar con ruta nueva | Recálculo antes de reanudar después de caminar libremente. | [f866717](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/commit/f866717) |
| 2026-11-01 | Progreso al caminar | Corrección para alinear el progreso con la posición del astronauta movido manualmente. | [c7bc1ab](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/commit/c7bc1ab) |
| 2026-11-01 | Recálculo y polvo | Recálculo desde posiciones fuera de la ruta y escenarios explícitamente simulados de polvo y tormenta. | [ed9f48e](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/commit/ed9f48e) |
| 2026-11-01 | Documentación unificada | Guías de instalación y uso, referencias, arquitectura y registro de validaciones consolidados. | [2f1ed15](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/commit/2f1ed15) |
| 2026-11-01 | Menús KSP y AR | Separación del laboratorio auxiliar de KSP y del flujo experimental para un futuro casco AR. | [a273ae9](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/commit/a273ae9) |
| 2026-11-01 | HUD AR y puente KSP | HUD mínimo, modo maqueta WebXR y conector local de KSP 1 mediante kRPC, de solo lectura. | [19ccd0a](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/commit/19ccd0a) |
| 2026-11-01 | Guía por voz | Indicaciones de giro y voces españolas seleccionables para la navegación. | [699e084](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/commit/699e084) |
| 2026-11-01 | Destinos propios | Objetivos personalizados integrados en las rutas y en la exportación de misiones. | [22f2bad](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/commit/22f2bad) |
| 2026-11-01 | Globo y astronautas | Globo de Marte, astronautas que siguen la ruta y navegación de superficie. | [783c999](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/commit/783c999) |
| 2026-11-01 | Exploración inmersiva | Cámaras panorámicas y navegación orbital para explorar el terreno. | [9087d2d](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/commit/9087d2d) |
| 2026-11-01 | Relieve 3D | Terreno tridimensional con textura orbital real. | [6648fd6](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/commit/6648fd6) |
| 2026-11-01 | Fotografía orbital | Imágenes HiRISE reales y controles interactivos del mapa. | [788242e](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/commit/788242e) |
| 2026-10-30 | Python en Android — histórico | Se documentó la ejecución con Pydroid y Termux. La documentación móvil se retiró al abandonar el APK y la aplicación instalable. | [f02608c](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/commit/f02608c) |
| 2026-10-30 | APK histórico — retirado | Se añadió un APK Android de depuración con datos de Marte y conexión Python. Fue retirado en 0041b9a. | [ef7e723](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/commit/ef7e723) |
| 2026-10-30 | PWA histórica — retirada | Se incorporaron instalación PWA, mapa sin conexión y guía móvil. Estas funciones de instalación se retiraron posteriormente en 0041b9a. | [0875988](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/commit/0875988) |
| 2026-10-30 | Propósito del proyecto | Explicación en español de los objetivos educativos y científicos. | [950c6ce](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/commit/950c6ce) |
| 2026-10-30 | Contexto de Marte | Información planetaria con fuentes de NASA y contexto científico. | [54aea92](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/commit/54aea92) |
| 2026-10-30 | Instalación local | Guía en español para instalar, ejecutar y probar el proyecto en una computadora. | [6b9ef1e](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/commit/6b9ef1e) |
| 2026-10-30 | Servidor Python | Servidor, planificación de rutas y exportación de misiones trasladados a Python. | [3702d7c](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/commit/3702d7c) |
| 2026-10-30 | Primer mapa científico | Guía de campo de Glen Torridon con datos verificados de relieve y objetivos científicos, y documentación de investigación. | [84a916a](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/commit/84a916a) |

## Cómo registrar las siguientes versiones

Cada actualización publicada debe añadir una entrada al inicio con número, nombre, fecha, funciones añadidas, correcciones, retiradas y validación. Se mantendrá el mismo número en `package.json`, README e interfaz. Las correcciones compatibles incrementan el último número; las funciones compatibles, el segundo; los cambios incompatibles, el primero.
