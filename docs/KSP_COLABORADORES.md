# Bitácora de colaboradores · Pruebas de integración KSP

Este documento reúne las experiencias de quienes prueban la integración con una partida real de **Kerbal Space Program 1**: mapa nativo, conector kRPC, HUD conectado al juego y mapas importados utilizados junto a KSP.

Cada colaborador añade aquí sus resultados, logs, errores, mejoras y sugerencias. También se pueden documentar intentos reales bloqueados por problemas de conexión, indicando qué se intentó. Las pruebas exclusivas de la demo, del explorador de Marte o de AR sin KSP quedan fuera del alcance de esta bitácora.

[Configuración del conector](AR_KSP.md) · [Mapa nativo KSP](KSP_MAPA.md) · [Mapas SCANsat](KSP_MAPAS_DATOS.md) · [Validación del proyecto](VALIDACION.md)

## Cómo añadir tu experiencia

1. Copia la plantilla de este documento y añádela al final, después del registro de sesiones.
2. Identifica la versión o commit realmente probado, aunque sea anterior al actual.
3. Completa los datos del entorno, pasos, resultados y sugerencias. Marca como **No probado** lo que no hayas comprobado.
4. Añade los logs y evidencias con nombres que permitan relacionarlos con la sesión. Puedes usar `docs/ksp-logs/AAAA-MM-DD-usuario/` para archivos de texto revisados, misiones JSON y capturas. Crea la carpeta cuando tengas archivos que aportar.
5. Enlaza los archivos desde tu entrada y relaciona los errores con la hora o línea del log. Si falta algún log, explica por qué y qué evidencia sí obtuviste.
6. Guarda los cambios con un commit o abre un pull request para que el equipo revise e incorpore la experiencia.

Desde GitHub puedes editar este documento con el botón del lápiz y subir los archivos con **Add file → Upload files** en la carpeta correspondiente. Para un cambio que incluya varios archivos, conviene trabajar en una rama y agruparlo en un pull request. Si no tienes permiso de escritura, utiliza un fork y propone el pull request.

Este repositorio es público: revisa los logs antes de añadirlos, especialmente claves, correos, nombres de usuario y rutas personales. Usa archivos de texto o ZIP revisados para logs extensos y respeta los límites de archivos de GitHub. No añadas el juego, ejecutables, credenciales ni tu instalación completa de KSP.

## Qué evidencias recopilar

- **`KSP.log`** de la carpeta de instalación, correspondiente a la sesión del problema. Si aportas `Player.log`, identifica instalación y sesión.
- **Salida del conector Python**, con mensajes de inicio, conexión y errores. Por ejemplo:

  ```bash
  # macOS/Linux, desde la raíz del repositorio:
  .venv/bin/python -u integrations/ksp_server.py > ksp-connector.log 2>&1
  ```

  ```powershell
  # Windows, desde la raíz del repositorio:
  .venv\Scripts\python.exe -u integrations/ksp_server.py *> ksp-connector.log
  ```

  Mantén el proceso abierto durante la prueba y detén con Ctrl+C al terminar. La salida se escribe en el archivo en estos ejemplos.
- **Errores de la consola del navegador**, con mensaje completo y hora.
- **Misión y mapa exportados**, cuando el fallo dependa de destinos, alturas, pendiente o cobertura.
- **Capturas o video** del juego y la guía; para errores de rumbo, compara con la navball.
- **Estado del conector**, si es relevante: guarda la respuesta de `http://localhost:7173/api/ksp` y de `http://localhost:7173/api/ksp/terrain`. Son instantáneas, no logs de toda la sesión.

## Plantilla para copiar

Copia el bloque siguiente, rellénalo y añade la sesión al registro. No marques la plantilla vacía como una prueba realizada.

```markdown
## AAAA-MM-DD · Usuario · Título de la prueba

### Sesión y entorno

- Colaborador / usuario de GitHub:
- Fecha, hora y zona horaria:
- Aplicación: versión y commit probado:
- KSP: versión y distribución:
- kRPC: versión del mod y del cliente Python:
- Python / sistema operativo / navegador:
- Equipo: CPU, RAM y GPU:
- Mods relevantes y versiones (o stock):
- Área probada: mapa nativo / HUD con KSP / mapas importados / conector:
- Cuerpo, ubicación y vehículo o astronauta:
- Duración aproximada de la sesión:
- Resultado general: funcionó / parcial / bloqueado:
- Confirmación: esta experiencia corresponde a una prueba con KSP real:

### Configuración y preparación

Indica cómo ejecutaste el conector, puertos, mapa/misión utilizada,
resolución, pendiente, destinos y cualquier ajuste necesario para repetirla.

### Pasos de la prueba

1.
2.
3.

### Resultado esperado

### Resultado observado y experiencia de uso

Incluye respuesta de la guía, fluidez, indicaciones y diferencias con el juego.

### Comprobaciones

Usa Correcto / Falló / No probado / No aplica, con observaciones.

| Comprobación | Resultado | Observaciones / evidencia |
| --- | --- | --- |
| Conexión y reconexión kRPC | No probado | |
| Posición y cuerpo correctos | No probado | |
| Rumbo frente a la navball | No probado | |
| Muestreo de alturas | No probado | |
| Destinos y cálculo de ruta | No probado | |
| Recálculo al desviarse | No probado | |
| Pausa por desconexión / salida de región | No probado | |
| Indicaciones y voz | No probado | |
| Importación / exportación de mapas | No probado | |
| Fluidez y consumo de recursos | No probado | |

### Logs y evidencias

Enlaza cada archivo y explica qué demuestra. Indica sesión, hora o líneas
relevantes. Añade extractos si ayudan, conservando también los logs completos.

- Log KSP:
- Log del conector:
- Errores de navegador:
- Misión / mapa:
- Capturas / video:
- Evidencias que faltan y motivo:

### Errores encontrados

Para cada error: pasos, hora, mensaje exacto, frecuencia e impacto.

### Mejoras y sugerencias

Para cada propuesta: problema, cambio sugerido, utilidad y prioridad.
Si no tienes propuestas, indícalo.

### Seguimiento

- Pendientes:
- Respuesta o revisión de otro colaborador:
- Nueva versión probada y resultado:
- Estado: pendiente / en revisión / resuelto:
```

## Registro de sesiones

Añade las experiencias debajo de esta tabla y enlaza aquí su encabezado. Conserva las observaciones originales cuando añadas una repetición o corrección.

| Fecha | Colaborador | Versión / commit | Prueba | Resultado | Enlace a la sesión |
| --- | --- | --- | --- | --- | --- |

La prueba parcial del HUD con KSP 1.12.5 ya registrada se conserva en [VALIDACION.md](VALIDACION.md#conexión-con-una-partida-real-de-ksp-1-parcial). Ese registro corresponde al HUD anterior y no valida por sí solo el mapa nativo ni versiones posteriores.
