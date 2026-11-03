# v1.7.9 · Avisos y actualización del conector

## Cómo funciona

Desde v1.7.9 el conector comprueba la versión oficial al arrancar y cada hora en un hilo independiente. Consulta el último commit de `main` en GitHub y el `package.json` de ese commit concreto. Compara versiones numéricas: 1.7.10 es posterior a 1.7.9.

Si hay una nueva versión, KSP Map muestra un aviso junto al título. En Windows, si ya existe una actualización al arrancar el conector, aparece también una ventana que permite abrir estas instrucciones. Rechazarla conserva la versión actual. No hay ventanas periódicas mientras se conduce: las novedades detectadas posteriormente se muestran en el mapa.

**Comprobar no instala nada ni ejecuta código remoto.** Tampoco cierra KSP, modifica partidas o recompila el mod. Puedes terminar tu prueba antes de actualizar. La web de Render se publica por separado y basta recargarla; este sistema actualiza la copia local del proyecto.

Si falla Internet o GitHub limita peticiones, el conector continúa funcionando. El aviso conserva la última información conocida, si existe. Para no contactar con GitHub, arrancar con `--no-update-check`. Esta comprobación es independiente del consentimiento para evidencias: no envía sesiones ni datos de PC a GitHub, aunque GitHub recibe los metadatos normales de una conexión HTTPS.

## Actualizar una copia clonada con Git

1. Termina la prueba y cierra el conector con Ctrl+C para guardar e intentar el último envío. No es necesario cerrar KSP para actualizar solo Python/web.
2. Ejecuta **`actualizar-ksp.cmd`** en la carpeta raíz. Usa `.venv` si existe; en caso contrario, el lanzador `py -3` de Windows.
3. Escribe **ACTUALIZAR** cuando lo pida. Puede cancelarse sin modificar la copia.
4. El programa verifica Git, el origen oficial HTTPS, la rama y que no haya cambios locales ni archivos nuevos sin registrar. Obtiene y verifica la revisión anunciada y aplica únicamente un avance rápido.
5. Reinicia el conector y recarga el mapa. Si cambian las dependencias, revisa `integrations/requirements-ksp.txt` y actualiza tu entorno de Python según la guía de instalación. No se ejecuta pip automáticamente.

Alternativa en otras plataformas:

```bash
python3 integrations/ksp_updates.py check
python3 integrations/ksp_updates.py update
```

Desde v1.7.9, el conector y el instalador comparten un bloqueo de esta carpeta: no se actualiza mientras el conector está abierto. La primera migración desde una versión anterior a v1.7.9 debe hacerse manualmente, con todos los conectores antiguos cerrados, porque todavía no incorporan ese bloqueo.

No se usan `reset --hard`, `clean`, stash automático ni fusión de conflictos. Si tienes cambios, guárdalos en un commit o respáldalos y resuelve la actualización tú mismo. Si la rama diverge, el actualizador se detiene. Los repositorios con origen SSH o un fork requieren actualización manual; el programa no cambia su remoto por ti. Se desactivan hooks de Git y fsmonitor durante las operaciones del actualizador. No se ponen contraseñas o tokens en comandos.

Las carpetas ignoradas `.ksp-cloud`, `.ksp-updates`, `ksp-sessions` y `.venv` se conservan. No publiques esas carpetas para pedir ayuda. La actualización obtiene código del repositorio oficial: no es una firma independiente ni protege frente a una cuenta de GitHub comprometida. El proceso depende de Git y de la disponibilidad del servidor; no promete recuperación automática de un corte de energía durante el cambio de archivos.

## Si descargaste un ZIP

Los avisos funcionan, pero el actualizador Git no transforma una carpeta ZIP en un repositorio. Descarga la versión desde [GitHub](https://github.com/FULLY4425/Lobos-espaciales-beta-nasa), extráela en otra carpeta y sigue la instalación local. Conserva la carpeta anterior y traslada tus evidencias/configuración privada solo dentro de tu PC cuando corresponda. No sobrescribas a ciegas tu único respaldo.

## Mod meteorológico de KSP

Actualizar el proyecto cambia su **código fuente**, no la DLL instalada dentro del juego. Si la revisión cambia el mod, cierra KSP y vuelve a ejecutar `integrations/ksp-weather-mod/install-weather.cmd` siguiendo [la guía de clima](KSP_CLIMA.md). El mod sigue siendo experimental y requiere compilación y validación con las bibliotecas reales del juego.

## Validación

Pruebas de comparación numérica, GitHub sin conexión, revisión inválida, cambios locales, origen ajeno, bloqueo entre procesos, versión descargada incorrecta y uso exclusivo de avance rápido. Se comprobó también la consulta real al repositorio oficial. Además de las pruebas con Git simulado, se actualizó un clon temporal real de v1.7.7 a v1.7.8 mediante el repositorio oficial y se verificó que conservara su configuración local ignorada. La copia de trabajo no se modificó durante ese ensayo. No sustituye una prueba de instalación en Windows ni un reinicio real de KSP. El aviso nativo de Windows queda pendiente de comprobación visual en ese sistema.
