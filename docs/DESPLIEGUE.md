# Compartir el proyecto con un enlace público

GitHub guarda el código. Para ejecutar la página y su API Python, conecta el
repositorio a un servicio web de Render. GitHub Pages no ejecuta Python.

## Desplegar en Render

1. Sube a GitHub los cambios que incluyen `render.yaml`.
2. Entra en https://dashboard.render.com/ y accede con tu cuenta.
3. Selecciona **New → Blueprint**, conecta GitHub y elige
   `FULLY4425/Lobos-espaciales-beta-nasa` y la rama que contiene estos cambios.
4. Revisa la configuración y crea el servicio. El archivo `render.yaml`
   configura Python, el inicio y la comprobación de salud.
5. Cuando termine el despliegue, abre la URL HTTPS que Render asigne al servicio
   y compártela con tus compañeros. No necesitan instalar Python.

El servidor lee el puerto de `PORT` y escucha en `0.0.0.0`, como requiere Render.
No se necesitan paquetes externos ni claves de API. Los cambios posteriores
en la rama conectada se despliegan automáticamente.

El plan gratuito puede suspender el servicio cuando no se usa; el primer acceso
puede tardar en responder. Revisa las condiciones y límites vigentes de Render.
Esta configuración sirve para compartir el prototipo educativo; el servidor
Python incluido es de desarrollo.

## Comprobar el despliegue

- Abre `/api/health` en la URL pública: debe devolver `"status": "ok"`.
- Abre la página, agrega dos objetivos y calcula una ruta para verificar la API.
- Comparte la URL pública HTTPS, no `localhost` ni la dirección del repositorio.
