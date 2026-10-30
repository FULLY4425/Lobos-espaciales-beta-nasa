# Lobos Espaciales · Mars Field Guide

Aplicación educativa en español para explorar **Glen Torridon, cráter Gale, Marte**, y planear una caminata científica con datos reales de NASA/PDS.

## Ejecutar

Requiere Node.js 22 o posterior. No usa dependencias de ejecución ni claves de API.

```sh
npm ci
npm run dev
```

Abre el puerto 5173 en tu entorno de desarrollo. `PORT` permite cambiarlo. Para generar archivos estáticos: `npm run build`. Publica el contenido de `dist` desde la raíz de un dominio. `npm test` verifica navegación, obstáculos y datos reales.

## Uso

1. Activa las capas de relieve, pendientes y objetivos científicos.
2. Selecciona un punto del mapa o usa el selector accesible de objetivos.
3. Agrega dos o más objetivos al recorrido, en orden. El primero es la salida.
4. Ajusta el límite de pendiente simulado y calcula la ruta.
5. Exporta coordenadas, fuentes, parámetros y métricas en JSON.

Las rutas siguen una cuadrícula de elevación real muestreada a unos 12.1 m. Se evitan celdas sin datos, pendientes superiores al límite y cruces diagonales por esquinas bloqueadas. La función de costo penaliza desniveles. No se afirma que sea una ruta certificada ni óptima para humanos.

## Datos e investigación

- [Investigación y fuentes](docs/INVESTIGACION.md)
- [Verificación de cobertura](docs/COBERTURA.md)
- [Procedencia y hashes](public/data/provenance.json)
- [Tabla científica original](public/data/target_classification.csv)
- [Reproducir la recopilación](scripts/collect-data.py): `python3 scripts/collect-data.py` (solo biblioteca estándar).

Los datos pequeños están incluidos; la app no necesita consultar NASA durante el uso. Las tipografías remotas son opcionales y tienen fuentes de respaldo. El mapa muestra **relieve calculado, no una fotografía**. Las imágenes se consultan en el archivo original mediante el enlace de contexto; todavía no se vinculan automáticamente por objetivo.

## Capturas

![Vista de escritorio](docs/captura-escritorio.png)

[Validación realizada](docs/VALIDACION.md).

## Alcance

Implementado: elevación, pendientes calculadas, observaciones químico-geológicas de ChemCam, filtros de vetas y nódulos, ficha científica, recorridos y exportación. Dos misiones: MRO y MSL/Curiosity.

No integrado: capa mineralógica CRISM, clima, radiación, fotografía orbital de fondo, navegación 3D/HUD, posiciones APXS transformadas o autonomía de trajes. Se investigaron como extensiones, pero requieren comprobar cobertura y calibración. Los tiempos usan **2 km/h y 10 min por parada posterior a la salida**; no incluyen regreso. No se estima oxígeno. Las alturas publicadas de objetivos y del DTM no se comparan como si compartieran una alineación vertical ya validada.

Proyecto independiente inspirado en NASA Space Apps. No implica afiliación ni aprobación de NASA. Conservar créditos de NASA/JPL-Caltech/University of Arizona y Gasda et al. al reutilizar los datos. Consultar las condiciones de cada fuente; no se asigna una licencia propia a los datos de terceros.
