# Desarrollo, arquitectura y API

## Requisitos por tarea

| Tarea | Requisitos |
| --- | --- |
| Mapa, API y distribución | Python 3.10+, biblioteca estándar; navegador moderno. |
| Terreno/globo 3D | WebGL; Three.js incluido en `src/vendor`. |
| Indicaciones habladas | SpeechSynthesis y voces disponibles en el dispositivo. |
| Prueba KSP con juego | PC con KSP 1, mod kRPC compatible y cliente Python de `integrations/requirements-ksp.txt`. |
| Pruebas JavaScript | Node.js moderno; se han usado las API actuales de `node:test`. |
| Cámara / WebXR | Contexto seguro, permisos y soporte del dispositivo. |

## Responsabilidades

```text
Navegador: mapa 2D/3D, objetivos, cámaras y formularios
      │ POST /api/plan o /api/export
      ▼
server.py → mars/planner.py → terreno y objetivos del servidor
      │
      └─ misión JSON: gridPath, route, stops, metrics, assumptions, sources
             ├─ astronautas y navegación hablada
             ├─ ksp.html: laboratorio de HUD
             └─ ar.html: cámara HUD / maqueta WebXR

PC de KSP: integrations/ksp_server.py → kRPC 127.0.0.1:50000/50001
      │ GET /api/ksp (mismo origen que su aplicación local)
      ▼
HUD: calibración local → proyección sobre la ruta → aviso y voz
```

El cálculo A* y las métricas de misión pertenecen al servidor. JavaScript representa la ruta y calcula indicaciones/progreso visual; no sustituye el planificador. El puente de KSP solo lee propiedades: no accede a control ni piloto automático.

| Archivo | Responsabilidad |
| --- | --- |
| `server.py` | HTTP, recursos públicos y API JSON. |
| `mars/planner.py` | Validación, A*, pendientes y métricas educativas. |
| `src/app.js`, `src/route.js` | Interfaz, almacenamiento de objetivos propios, mapa y consultas asíncronas. |
| `src/terrain3d.js` | Terreno, globo, cámaras, personajes y reproducción. |
| `src/directions.js`, `src/navigation.js` | Maniobras, avisos, estado y voz nativa. |
| `ksp.html`, `ar.html`, `src/ar.js` | Laboratorio KSP y pantalla AR; la página KSP omite cámara y WebXR. |
| `src/ar-xr.js`, `src/ar-tracking.js` | Maqueta WebXR y proyección relativa de telemetría KSP. |
| `integrations/ksp_server.py` | Servidor local y muestreo de telemetría, con caducidad y reconexión. |
| `src/connection.js`, `sw.js` | Estado de conexión y retirada de la caché heredada; no se instala una aplicación independiente. |
| `scripts/build.py` | Copia una distribución ejecutable en `dist/`. |
| `scripts/collect-data.py` | Recopilación de tabla y terreno con trazabilidad. |

## API principal

El cuerpo de los POST debe ser un objeto JSON y tener como máximo 16384 bytes. La respuesta es JSON; los errores de validación devuelven `400` y un campo `error`.

### `GET /api/health`

Devuelve `status: "ok"`, `engine: "python"` y el número de objetivos científicos. No incluye los puntos guardados en los navegadores.

### `POST /api/plan` y `POST /api/export`

Aceptan 2–20 paradas y una pendiente entre 5° y 40°. Una parada científica se identifica por su nombre exacto. Un punto propio se identifica explícitamente como `type: "custom"`:

```json
{
  "stops": [
    "Stornoway",
    {
      "type": "custom",
      "name": "Mi punto",
      "lat": -4.73324341,
      "lon": 137.3998236
    }
  ],
  "maxSlopeDegrees": 20
}
```

Se rechazan coordenadas no finitas, nombres vacíos/de más de 60 caracteres, nombres repetidos, puntos fuera de cobertura o sin elevación válida. El servidor obtiene la altura de sus propios datos e ignora alturas y clasificaciones añadidas por el cliente. Un objetivo propio no puede suplantar el nombre de uno científico.

Campos de respuesta:

| Campo | Significado |
| --- | --- |
| `stops` | Paradas verificadas. Los puntos propios tienen `scientificObservation: false`. |
| `gridPath` | Celdas de la cuadrícula que componen la ruta. |
| `route` | Coordenadas longitud/latitud de esas celdas. |
| `metrics` | Distancia horizontal, ascenso y duración educativa. |
| `assumptions` | Velocidad, tiempo por parada y tamaño de celda. |
| `maxSlopeDegrees`, `returnIncluded` | Límite empleado y ausencia de regreso. |
| `educationalSimulation`, `createdAt`, `sources` | Carácter educativo, fecha de generación y procedencia. |

`/api/export` añade una cabecera de descarga JSON. No recupera una ruta guardada en una cuenta: vuelve a calcular con las paradas solicitadas.

### `GET /api/ksp`

- Con `server.py` o Render: `503`, con explicación de que hace falta el conector local.
- Con `integrations/ksp_server.py`: `200` y `status: "connected"` solo con datos recientes; `503` cuando no hay juego/conexión o los datos han caducado.
- El bloque `telemetry` contiene latitud, longitud, rumbo, altitud, velocidad, radio/nombre del cuerpo, nombre/identificador de vehículo, `receivedAt`, origen y `readOnly: true`.

La identificación de sesión/vehículo obliga a recalibrar tras reconexiones o cambios. El HUD comprueba frescura y solicita un recálculo si el desvío supera 30 m; conserva el origen de calibración y pausa si el cálculo falla. El protocolo no envía mandos al juego. Ver [calibración y red](AR_KSP.md).

## Almacenamiento y privacidad funcional

- Objetivos propios y preferencias de voz: `localStorage` de ese navegador.
- Misión transferida al menú KSP/AR: `sessionStorage` de la pestaña y origen.
- Importación JSON: validación en el navegador, máximo 2 MB; no se envía el archivo a Render.
- No hay cuentas ni sincronización colaborativa. Exportar JSON conserva las paradas de esa misión; no crea un respaldo de toda la lista de puntos propios.
- El puente se limita a loopback y no permite introducir un host RPC remoto desde la web.

## Ejecutar y verificar

```bash
python3 server.py
python3 -m unittest discover -s test -v
node test/directions.test.js
node test/ar-tracking.test.js
node test/replanning.test.js
node test/ksp-geo.test.js
node test/ksp-guidance.test.js
python3 scripts/build.py
```

Los comandos de Node.js son opcionales y solo para pruebas de desarrollo. `dist/` no se versiona; inicia `python3 server.py` dentro de esa carpeta para probar el paquete. El servidor sigue usando Python al desplegar: GitHub Pages no ejecuta esta API.

La [validación registrada](KSP_COLABORADORES.md#validaciones-registradas-y-pruebas-pendientes) separa pruebas unitarias, comprobaciones en navegador y ensayos pendientes con dispositivos reales. Las comprobaciones anteriores de Playwright se hicieron con herramientas temporales, no con una suite de navegador incluida en el repositorio.

## Contribuir o extender

1. Describe el comportamiento que quieres cambiar y comprueba el estado actual en las guías.
2. Conserva la procedencia y las unidades de los datos; no añadas capas científicas sin validar su cobertura.
3. Si cambias el planificador, valida obstáculos, límites, entradas y métricas. Si cambias indicaciones o telemetría, ejecuta las pruebas JavaScript correspondientes.
4. Comprueba que la distribución contiene los recursos web actuales. `sw.js` se conserva solo para retirar cachés heredadas; no añadas un flujo de instalación.
5. Actualiza guías y [validación](KSP_COLABORADORES.md#validaciones-registradas-y-pruebas-pendientes) sin presentar telemetría simulada como prueba en KSP ni emulación de pantalla como dispositivo físico.

El servidor HTTP incluido es de desarrollo. El despliegue público actual es un prototipo detrás de Render, no una infraestructura certificada de navegación o de casco.

## Escenarios y replanificación

Los POST aceptan `weather` (`clear`, `dust`, `storm`) y `replanReason`
(`initial`, `deviation`, `weather`, `manual`). El servidor carga los parámetros
de `public/data/weather-scenarios.json`, construye celdas bloqueadas e incluye
`environment`, `planningContext` y `stopPathIndices` en la misión. Los índices
permiten mantener las paradas pendientes al replanificar.

`src/replanning.js` construye la nueva salida personalizada desde la posición
actual, conserva el orden de destinos restantes y cancela peticiones obsoletas.
No modifica los datos científicos. El umbral de 30 m y las velocidades de clima
son parámetros del prototipo; ver [CLIMA_RECALCULO.md](CLIMA_RECALCULO.md).

## Navegación KSP nativa

`integrations/ksp_navigation.py` implementa proyección geográfica local,
validación y planificación con alturas leídas de kRPC. `Telemetry` en el
conector administra trabajos de muestreo y solo publica mallas completas.
`src/ksp-map.js`, `src/ksp-geo.js` y `src/ksp-view3d.js` proporcionan el mapa
nativo y su relieve, separados del terreno marciano.

Las capacidades actuales se anuncian como `ksp-surface-v1`. Una petición
`/api/ksp/plan` necesita una región muestreada del cuerpo activo y telemetría
reciente. Las API `/api/ksp/demo/*` solo usan el escenario sintético del
servidor y están disponibles en el despliegue web. Los detalles están en
[KSP_MAPA.md](KSP_MAPA.md).

## Mapas portátiles KSP

`integrations/ksp_maps.py` valida `ksp-terrain-v1`, deriva una identidad del contenido y planifica con alturas importadas. `scripts/import-scansat.py` convierte el CSV de SCANsat línea a línea, sin interpolar huecos. Las rutas `/api/ksp/maps/validate` y `/api/ksp/maps/plan` aceptan hasta 512 KB y no persisten archivos. El mapa web distingue salida manual y vehículo real. Instrucciones y límites en [KSP_MAPAS_DATOS.md](KSP_MAPAS_DATOS.md).

## Bitácora de pruebas KSP

Las experiencias de los colaboradores se registran en [KSP_COLABORADORES.md](KSP_COLABORADORES.md), mediante commits o pull requests. El documento incluye una plantilla y una tabla para enlazar sesiones y logs.

## Conducción y sesiones KSP (v1.4.0)

`src/ksp-guidance.js` implementa conectividad y estado físico de llegada; `src/speech-queue.js` ordena anuncios. `src/ksp-session.js` conserva sesiones del navegador y métricas de CPU/HTTP. `integrations/ksp_session.py` escribe evidencias locales acotadas en carpetas únicas; el conector expone diagnóstico, eventos y exportación ZIP en loopback. El servidor público no persiste evidencias de juego. [Formato, límites y pruebas pendientes](KSP_TRAVESIA.md).

## Evidencias privadas (v1.5.0)

`integrations/ksp_cloud.py` usa las APIs de Supabase Auth/Storage/PostgREST con una cuenta individual y clave pública. La cola se guarda con el ZIP exacto hasta confirmar Storage e índice; las credenciales se guardan solo en `.ksp-cloud/` local. `supabase/ksp_evidence.sql` define RLS y bucket privado. Las pruebas usan transportes simulados; configuración real y verificación de políticas siguen pendientes. [Guía](KSP_NUBE.md).

## Atlas de relieve (v1.6.0)

`src/terrain-style.js` comparte paleta y curvas entre Marte y KSP. `src/ksp-imagery.js` valida y reproyecta la textura en la malla local; la imagen no modifica elevaciones ni planificación. `public/data/ksp-map-catalog.json` referencia regiones y metadatos, sin duplicar los archivos de evidencias. Las máscaras se regeneran con `scripts/ksp_texture_coverage.py` a partir de los CSV ZIP de las sesiones. El mapa 3D KSP reutiliza marcadores y repinta a demanda; el espacio integrado pausa consultas y guía cuando queda oculto.

Comprobaciones adicionales: `node test/terrain-style.test.js`; las dos pruebas del generador de cobertura están incluidas en `python3 -m unittest discover -s test -v`. [Uso y contrato de textura](KSP_MAPAS_3D.md).

## Duna Explorador (v1.7.0)

`python3 scripts/build_duna_atlas.py` publica el PNG completo sin cambios y genera la cuadrícula global con alturas en decímetros enteros y huecos `null`. El globo reduce solo su geometría de visualización (paso de cuatro píxeles), sin modificar el archivo. Las regiones locales consultan el píxel más próximo y siguen pasando por la validación nativa y A*. `ksp_environment.py` y `ksp-environment.js` comparten parámetros explícitos de entrenamiento; el servidor aplica las restricciones y conserva su procedencia sintética en la misión. La maqueta WebXR acepta una textura explícita para que Duna nunca use el fondo de Marte. Pruebas adicionales: `test/test_duna_atlas.py` y `node test/ksp-global.test.js`.
