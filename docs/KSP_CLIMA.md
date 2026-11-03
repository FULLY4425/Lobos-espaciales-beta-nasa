# v1.7.8 · Vientos de Duna

Hay dos componentes: simulación en el mapa conectado a KSP y código de un mod opcional para efectos dentro del juego. El conector continúa leyendo kRPC; no aplica fuerzas ni controla el vehículo. El mod sí puede aplicar fuerzas si el jugador activa expresamente esa opción.

## En el mapa

Actualizar el repositorio, reiniciar el conector y abrir `http://localhost:7173/ksp-map.html`. En «Escenarios de entrenamiento» elegir escenario y dirección **desde donde viene** el viento (0° norte, 90° este). Las flechas apuntan hacia donde sopla. Puede usarse también sin juego con un mapa importado.

| Escenario | Viento / ráfaga | Visibilidad de entrenamiento | Factor de velocidad planificada |
| --- | --- | --- | --- |
| Despejado | 0 / 0 m/s | 20.000 m | 1 |
| Viento | 12 / 20 m/s | 5.000 m | 0,85 |
| Polvo | 8 / 14 m/s | 1.500 m | 0,75 |
| Tormenta | 25 / 40 m/s | 200 m | 0,5 |

Son valores educativos, no una previsión de Duna ni datos meteorológicos de Marte. El factor cambia la ETA; no cambia el mando de aceleración del rover. La dirección se representa en flechas y se comparte con el mod; la penalización de ETA es por escenario, no un cálculo aerodinámico por cada tramo. La visibilidad es un parámetro informativo y visual, no un detector de obstáculos a esa distancia.

La tormenta tiene una zona restringida: la ruta la evita o se pausa si no hay paso. Al cambiar de escenario/dirección se recalcula si hay misión y telemetría válida. El ciclo opcional pasa por despejado → viento → polvo → tormenta cada 20 s; dejarlo desactivado para pruebas estables. Se registran escenario, viento y visibilidad en eventos y exportación de la misión. La voz depende de activarla en el navegador.

Las franjas de ráfagas no capturan clics. En HUD se ocultan y en modo ligero o con movimiento reducido no se animan. Las alturas y objetivos permanecen intactos.

## Mod dentro de KSP: compilar e instalar en Windows

**Estado:** código preparado para KSP 1.12.x; sintaxis C# revisada, pero todavía no compilado contra bibliotecas de KSP ni ensayado en el juego. No hay una DLL precompilada. Esta sesión no tiene una instalación de KSP ni sus bibliotecas: no puede confirmar la compatibilidad binaria ni los efectos físicos reales.

1. Cerrar KSP y conservar una copia de la partida de prueba.
2. En el repositorio actualizado, abrir `integrations/ksp-weather-mod/install-weather.cmd`.
3. Seleccionar la carpeta de KSP que contiene `GameData` y `KSP_x64_Data/Managed`.
4. El script usa el compilador C# de .NET Framework de Windows y las bibliotecas de esa instalación. No descarga DLL de terceros ni copia bibliotecas de KSP al repositorio. Si falla, se detiene sin instalar y muestra la salida del compilador.
5. Si compila, instala únicamente `GameData/LobosWeather/LobosWeather.dll`. Reiniciar KSP.
6. En vuelo, abrir el botón del mod en la barra de aplicaciones o **Alt izquierdo + W**. Marcar **Activar entrenamiento**. Elegir escenario manualmente o seguir el mapa. Las fuerzas requieren una segunda casilla independiente.

Alternativa PowerShell, para compilar sin instalar:

```powershell
powershell.exe -NoProfile -File .\integrations\ksp-weather-mod\Build-Weather.ps1 -KspPath 'C:\ruta\Kerbal Space Program'
```

Para instalar añadir `-Install`. El lanzador `.cmd` omite la política de ejecución solo para ese proceso de PowerShell; no la cambia permanentemente. Revisar el script antes de ejecutarlo. Si Windows no tiene el compilador .NET Framework, hay que instalarlo. Para desinstalar, cerrar KSP y retirar solo la carpeta `GameData/LobosWeather`.

## Usar el mismo escenario en mapa y juego

1. Iniciar el conector en su puerto predeterminado 7173.
2. En el mapa local, elegir el escenario y marcar **Compartir escenario con el mod de KSP local**.
3. En el mod, marcar **Activar entrenamiento** y **Seguir mapa local en puerto 7173**.
4. Para añadir efecto físico al rover, marcar **Aplicar fuerzas al rover**. Para detenerlo, desmarcarla o pulsar **Detener efectos**.

El mod consulta solo `http://127.0.0.1:7173/api/ksp/weather` cada 2 s. No consulta Render/Supabase, no usa credenciales y no hace subidas. Una publicación en el conector no demuestra que el mod esté instalado o haya aplicado fuerzas; su ventana muestra el estado efectivo. El mapa renueva la activación cada 5 s mientras está visible; el conector deja de publicarla activa tras 15 s sin renovación. Si el mod no recibe una respuesta válida durante 5 s, desactiva los efectos mientras sigue el mapa. Ocultar o cerrar la vista también termina desactivando el escenario compartido por caducidad. Si usa controles manuales del mod, no necesita el conector.

La API local admite únicamente los cuatro escenarios, dirección válida y activación booleana. Las fuerzas siguen requiriendo autorización dentro del mod: el mapa no puede activarlas por sí solo. Al cerrar/cambiar la fuente del mapa se intenta dejar de compartir; un cierre forzado puede impedir ese último aviso. Detener el conector invalida la conexión del mod tras 5 s.

## Alcance físico y límites

La primera implementación aplica efectos solo al vehículo activo cargado, cerca de la superficie de **Duna**, sin aceleración temporal y sin pausa. No actúa sobre vehículos descargados, astronautas EVA u órbitas. Polvo visual con hasta 160 partículas; ráfagas sinusoidales entre las velocidades del escenario.

Las fuerzas son un modelo educativo incremental de arrastre: densidad atmosférica de KSP, velocidad relativa, área de arrastre fija equivalente a 10 m² y aceleración limitada a **0,2 m/s²**. Usa `ForceMode.Acceleration` sobre cuerpos rígidos distintos del rover para evitar duplicar el mismo cuerpo. No equivale a una simulación meteorológica validada ni usa la geometría real de cada pieza. No modifica la atmósfera global ni añade un sistema de clima planetario a KSP. Debe validarse en una partida de prueba antes de usarlo en una misión que se quiera conservar.

## Verificación

95 pruebas Python y 52 JavaScript, incluyendo presets, parámetros inválidos, puente protegido y ETA con viento; prueba del mapa/globo/3D en Chromium y análisis de la gramática C#. Esto **no sustituye** compilar el mod con `Assembly-CSharp`/Unity de KSP y probar las llamadas de su API real.

Para la prueba real: empezar con fuerzas desactivadas; comprobar efectos visuales en Duna, activación/detención, seguimiento del mapa, pérdida del conector y pausa/aceleración temporal. Después activar fuerzas a baja velocidad y verificar estabilidad y dirección, registrar KSP.log (de forma opcional) y añadir resultados y errores de compilación a [la bitácora](KSP_COLABORADORES.md). El mod no incluye control de rumbo, piloto automático ni ejecución de órdenes externas.
