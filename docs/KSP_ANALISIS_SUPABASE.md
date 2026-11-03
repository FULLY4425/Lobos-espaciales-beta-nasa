# v1.7.7 · Datos en acción

Análisis del índice privado y los resúmenes recibidos en Supabase, realizado el 2 de noviembre de 2026 (México). Se consultaron `ksp_sessions` y `diagnostic_summary` mediante la conexión autorizada; no se hicieron públicos los ZIP, las identidades ni las claves. No se descargaron ni revisaron los logs completos privados para este análisis.

## Evidencia observada

Instantáneas de las 17:43 y 18:08 del 2 de noviembre (23:43 y 00:08 UTC). Las dos sesiones tienen `stopped_at` vacío: son instantáneas recibidas durante el uso, no cierres confirmados.

| Dato | Sesión v1.7.4 | Sesión v1.7.5 |
| --- | ---: | ---: |
| Muestras en el índice | 2.321 | 1.350 |
| Muestras en el resumen | 2.288 | 1.350 |
| Muestras de PC en el resumen | 493 | 294 |
| CPU máxima del equipo | 58,9 % | 41,4 % |
| RAM máxima del equipo | 85,6 % | 66,3 % |
| Lectura kRPC máxima | 47,42 ms | 67,68 ms |
| Repintado máximo informado | Sin dato | 162 ms |
| Petición local máxima informada | Sin dato | 532,4 ms |
| Máxima velocidad registrada | 0,02 m/s | 21,81 m/s |

Una segunda consulta a las 18:13 (00:13 UTC) ya mostró 1.626 muestras en el índice de v1.7.5 frente a 1.625 en su resumen, conservando el máximo de 162 ms. Confirma que la sesión sigue recibiendo datos y que el desfase del resumen no era exclusivo de v1.7.4. Las mejoras de v1.7.7 todavía no se estaban ejecutando en ese PC.

La instantánea inicial de v1.7.5 incluye 19 instantáneas de rendimiento, dos misiones y una conexión kRPC registrada. Sus cinco eventos `browser-connection` no equivalen a cinco reconexiones de kRPC: pueden reflejar visibilidad o reapertura de la vista. No hay evidencia aquí para atribuir esos eventos a pérdida de paquetes.

Se excluyó la validación sintética v1.7.3 de cero muestras. Ninguno de estos resúmenes mide FPS del juego. Los picos de CPU/RAM no muestran duración: no prueban saturación persistente ni justifican alterar la física o los controles del rover.

## Cambios derivados de los datos

1. **Resumen coherente con el ZIP.** Había 33 muestras de diferencia en v1.7.4. El resumen periódico en disco podía quedarse detrás del manifiesto vivo. Ahora `export()` crea `analysis.json` y el manifiesto mientras mantiene la misma exclusión de escritura; copia los contadores antes de comprimir. Se conserva el resumen periódico local, pero el ZIP usa el actualizado. No se modificaron las evidencias antiguas ni sus filas históricas.
2. **Menos trabajo de dibujo.** Región 3D y globo evitan repetir `setSize` y recalcular la proyección si no cambian dimensiones o densidad de píxeles. El atlas 2D evita reiniciar el lienzo al conservar su tamaño. No se reducen las alturas ni se simplifican las rutas.
3. **Modo ligero opcional.** Reduce a 1 la densidad de píxeles de dibujo frente al máximo normal de 1,5 en 3D y 2 en 2D. Puede verse menos nítido en pantallas densas. No cambia los gráficos del juego ni los datos originales. Se activa en el panel «Estado del equipo y vuelo» y puede desactivarse para comparar.
4. **Medición útil para el siguiente ensayo.** Se guardan cantidad, media, máximo, número de muestras de más de 50 ms y p95 de las últimas 120 mediciones. Se separan `render2d`, `render3d`, `atlas2d`, `atlas3d` y peticiones locales. Ahora la métrica de actualización incluye el atlas, que antes retornaba antes de medirse. Son tiempos CPU de actualizaciones iniciadas por la aplicación, no todos los cuadros de la GPU ni FPS; los movimientos internos de cámara tienen su propio ciclo y no todos pasan por esta medición.
5. **Recomendaciones más precisas.** Con al menos 30 mediciones, se advierte coste repetido si la media supera 20 ms o al menos el 10 % supera 50 ms. Un máximo aislado mayor de 100 ms pide revisar media/p95 antes de concluir lentitud sostenida. El resumen muestra las últimas estadísticas recibidas por vista; no suma instantáneas acumuladas como si fueran muestras nuevas. La media de una vista corresponde a su sesión del navegador, no necesariamente a toda la sesión del conector.

No se cambian permisos, autenticación, consentimiento, cuotas de subida, clima ni conducción. Estas decisiones no requieren nuevas tablas ni funciones de Supabase.

## Validación y siguiente prueba

92 pruebas Python y 51 JavaScript, incluida reproducción de resumen antiguo seguido de nueva telemetría, cambios de contadores durante la compresión, un pico aislado frente a carga repetida, p95 acotado y reutilización de la ventana 3D. Se verifica también atlas, globo, textura, objetivos, rutas, clima y HUD en Chromium.

Actualizar el repositorio, reiniciar el conector y abrir localhost con Firefox. Comparar en la misma escena y vista unos minutos en modo normal y luego ligero, con cámara/ventana iguales. Revisar medias y p95 por vista en las siguientes subidas; repetir la comparación en sesiones del navegador separadas para no mezclar ambas configuraciones en una media acumulada. Confirmar que `session.json.telemetrySamples`, `analysis.json.telemetrySamples` y el índice coincidan en la nueva instantánea.

Las sesiones históricas usaron versiones anteriores. Aún falta medir v1.7.7 en el PC real; no se promete un porcentaje de mejora. Un cierre forzado o fallo de disco/red conserva las limitaciones descritas en [seguridad y recuperación](SEGURIDAD_KSP.md). Registrar los resultados del juego en [la bitácora](KSP_COLABORADORES.md).
