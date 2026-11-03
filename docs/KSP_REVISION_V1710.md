# v1.7.10 · Ruta atenta

Revisión cruzada del 2 de noviembre de 2026 (México): bitácoras nuevas `da52239` (v1.7.9) y `9e92d79` (tormenta), ZIP asociados y resúmenes privados de cinco sesiones reales en Supabase. La validación sintética de cero muestras queda excluida. No se publican identidades ni archivos privados de Supabase.

## Confirmaciones y límites de los datos

- Las dos bitácoras registran llegadas a 6,4 y 7,2 m, además de paso de largo. Los `events.jsonl` de ambos ZIP contienen un `browser-arrival-confirmed` y un `browser-destination-passed` cada uno; el de tormenta añade tres cambios de escenario.
- La tormenta se probó en el mapa, no mediante el mod dentro de KSP. Bloqueó una zona y redujo la velocidad planificada a 1 m/s. No hay prueba de viento físico en el juego: el mod no fue instalado.
- En Supabase, las dos sesiones v1.7.9 tenían repintado 2D medio de 1,15–1,42 ms y p95 reciente de 1,8–2,2 ms. No hay evidencia de lentitud sostenida del dibujo 2D en esas muestras. No son FPS de KSP ni prueban el rendimiento de todas las vistas.
- Los máximos históricos de petición rondaban 2.510–2.515 ms. Las estadísticas recientes de peticiones correctas eran menores. El código anterior mezclaba solicitudes canceladas con medidas completadas; no se puede atribuir cada máximo histórico a cancelación, pérdida de paquetes o carga del PC.
- La sesión de tormenta incluye muestras en vuelo y un pico de 84,1 m sobre el terreno. La guía debe atender al estado `flying`, aunque la celda de 2 km diera una tolerancia vertical de 100 m.
- Los ZIP curados muestran resumen de 246 frente a manifiesto de 249 muestras y de 376 frente a 406. Los registros locales periódicos y las instantáneas subidas no siempre corresponden al mismo momento. No se corrigen los contadores originales inventando muestras.

## Correcciones aplicadas

| Hallazgo | Cambio |
| --- | --- |
| Nuevo `ksp-map.js` con un módulo de clima viejo en caché | Integración de [PR #4](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa/pull/4). GET/HEAD de estáticos revalidan con `no-cache`, incluyendo respuestas 304; API sigue sin almacenarse. Una página ya abierta debe recargarse. |
| Desvíos tolerados hasta 3 km en celdas de 2 km | Umbral en metros, configurable entre 15 y 250 (75 por defecto), con 1,5 s fuera del trazado y al menos 10 s entre solicitudes de recálculo. Registra distancia lateral, umbral y resolución. No confiere precisión adicional al relieve. |
| Evento de salida de región ausente si la guía estaba bloqueada o no había ruta | La transición de cobertura se registra al aceptar la telemetría, independientemente de la misión o su bloqueo. La prueba real aún debe repetirse. |
| Tormenta deja destinos sin paso | Mostrar centro geográfico y radio de su zona; botón que prepara coordenadas de una celda conectada. El usuario debe sustituir/agregar el destino y calcular para confirmar. No evita rocas menores que la celda ni controla el rover. |
| Muestras en vuelo bajo el límite de altura de un mapa grueso | El estado de vuelo `flying/sub_orbital/orbiting/escaping` pausa la guía de superficie; se conserva el criterio de altura como alternativa. |
| Picos de petición ambiguos | Medición de red hasta terminar JSON, antes del dibujo; categorías `httpRequest`, `httpError`, `httpTimeout` y `httpCancelled`. Se activa TCP_NODELAY en el servidor para evitar esperas de agrupación de pequeñas escrituras. No se promete una mejora medida ni ausencia de pérdida. |
| Prueba falla por permisos Windows | Los casos normales GET/HEAD siguen ejecutándose. La prueba específica de symlink se omite con motivo explícito si Windows no permite crearlo; no se cuenta como ataque bloqueado sin haber creado el enlace. |

## Calidad de las evidencias en Supabase

Se añadió `diagnostic_summary.dataQuality` con comparación `index-vs-summary`, ambos contadores, estado y resultado booleano. La comprobación se aplica en la pasarela del servidor a nuevas subidas y en el cliente para el modo de cuenta manual. Si falta un contador válido, el estado es `unknown`.

Se anotaron cinco sesiones reales existentes: cuatro `stale-summary` y una `consistent`. En la consulta final, la sesión activa ya tenía 744 muestras tanto en índice como en resumen. Sus datos siguen cambiando al continuar la prueba.

La marca es una comprobación de **consistencia de contadores declarados**, no una certificación de autenticidad, cobertura total o ausencia de pérdidas. Se mantienen los valores originales y todos los ZIP. Los avisos de un resumen desfasado deben interpretarse según su fecha; no describen necesariamente toda la instantánea más reciente. Se conservan permisos, identidad, consentimiento y bucket privado; no se crean tablas ni se amplían accesos.

## Validación y próxima prueba real

103 pruebas Python, 57 JavaScript y recorrido Chromium del atlas/globo, rutas, viento/tormenta, HUD y modo ligero. `scripts/check_ksp_deviation.py` verifica además que un desvío persistente en la demo produzca un solo recálculo desde la nueva posición. La prueba de caché comprueba 200 + `no-cache`, revalidación 304 y API `no-store`. Se prueban desvío persistente/cooldown, celda conectada, estado de vuelo y clasificación de peticiones. En este entorno se ejecutaron las pruebas HTTP con loopback y la prueba de symlink real.

La pasarela `ksp-device` se desplegó como versión 3 y la consulta posterior confirmó las anotaciones. No se alteraron los archivos de evidencia originales.

Para repetir en el PC: actualizar, cerrar/reiniciar conector, recargar el mapa y conducir a más de 75 m del trazado durante varios segundos. Confirmar `browser-route-deviation` y `browser-route-created` con motivo `deviation`; salir de la región y comprobar `browser-region-exit`, incluso con guía pausada. Probar destino restringido y punto propuesto; comparar las nuevas métricas de peticiones. La prueba de voz y el mod meteorológico siguen pendientes.
