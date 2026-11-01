# Alojamiento y despliegue

## Servicio público actual

La aplicación está disponible en **https://lobos-espaciales-python.onrender.com/**.
Es un **servicio web Python** de Render conectado a la rama `main` del repositorio
`FULLY4425/Lobos-espaciales-beta-nasa` y con despliegue automático habilitado.

Rutas públicas principales:

| Ruta | Función |
| --- | --- |
| `/` | Mapa, planificación, astronautas e indicaciones. |
| `/ksp-map.html` | Mapa nativo KSP: demo pública; el juego real requiere el conector local. |
| `/ksp.html` | Laboratorio del HUD para KSP; el juego real requiere el conector local. |
| `/ar.html` | Pantalla AR experimental. |
| `/api/health` | Estado del motor Python y número de objetivos. |

GitHub conserva el código; Render ejecuta el servidor. GitHub Pages no ejecuta
las API de cálculo y exportación. El sitio estático creado en una etapa anterior
no sustituye al servicio Python.

## Actualizar el servicio existente

1. Verifica los cambios y súbelos a `main`.
2. Render inicia un despliegue al detectar el commit; no hace falta disparar otro.
3. Comprueba que ese despliegue llegue al estado `live`.
4. Abre `/api/health` y calcula una ruta en la URL pública.
5. Comprueba las pantallas del explorador, KSP y AR en el navegador. Las cachés heredadas se retiran automáticamente al abrir la versión actual.

El nombre del servicio web actual es `lobos-espaciales-python`. El `render.yaml`
del repositorio es una plantilla para crear infraestructura; el servicio actual
se creó directamente y no se debe asumir que editar ese archivo cambia su
configuración en Render. Aplicar un Blueprint nuevo puede crear otro servicio.

## Crear un despliegue nuevo

Puedes usar **New → Web Service** con estos valores:

| Campo | Valor |
| --- | --- |
| Repositorio | `https://github.com/FULLY4425/Lobos-espaciales-beta-nasa` |
| Rama | La rama que quieras publicar, normalmente `main`. |
| Runtime | Python. |
| Build command | `python --version` |
| Start command | `python server.py` |
| Comprobación HTTP opcional | `/api/health` |

También puedes elegir **New → Blueprint** después de subir `render.yaml` a la
rama elegida, revisando nombre, recursos y plan antes de aplicarlo. Consulta las
condiciones vigentes de Render para planes, límites y facturación.

El servidor lee `PORT` y escucha en `0.0.0.0`, como requiere el alojamiento. La
aplicación principal no necesita paquetes externos ni claves. **No instales
kRPC en Render para intentar acceder al juego del usuario**: la telemetría se
obtiene ejecutando el conector en el PC de KSP, según [AR_KSP.md](AR_KSP.md).

El plan gratuito puede suspender el servicio por inactividad y tardar en el
primer acceso. El servidor incluido sigue siendo de desarrollo; el despliegue
actual se utiliza para compartir y probar el prototipo.

La sección `/ksp-tests.html` utiliza GitHub para reportes y adjuntos persistentes. No requiere variables de entorno ni base de datos nuevas. Su formulario nativo se despliega con el repositorio (`.github/ISSUE_TEMPLATE/ksp-integration.yml`).
