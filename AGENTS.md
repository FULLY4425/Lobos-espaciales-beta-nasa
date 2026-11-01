# Instrucciones para agentes

Proyecto educativo "Lobos Espaciales / Ojo de Marte": servidor Python (`server.py`),
interfaz web (`index.html`, `ksp.html`, `ksp-map.html`, `ar.html`) y conector KSP 1.

- Responde y documenta en español.
- No presentes datos simulados (demo, escenarios de clima, telemetría sintética)
  como reales.
- La aplicación y `integrations/ksp_server.py` son **solo lectura** con KSP: no
  añadas control del vehículo ni del piloto automático.
- Para probar con el juego real, lee primero [docs/KSP_AGENTES.md](docs/KSP_AGENTES.md):
  preparación, mandos de teclado, trampas de kRPC y errores ya cometidos.
  Las herramientas de lectura están en `tools/ksp/`.
- Pruebas: `python -m unittest discover -s test -v` y `node test/<archivo>.test.js`
  (ver [docs/DESARROLLO.md](docs/DESARROLLO.md)). Registra los resultados reales en
  [docs/VALIDACION.md](docs/VALIDACION.md).
