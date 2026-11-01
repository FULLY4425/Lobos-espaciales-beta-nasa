# Comprobación de coordenadas y cobertura

Verificación realizada el 30 de octubre de 2026 mediante productos públicos descargados por HTTPS con validación TLS.

## Terreno

Producto: `DTEEC_009149_1750_009294_1750_U01`, MRO/HiRISE.

Fuente: https://www.uahirise.org/dtm/dtm.php?ID=PSP_009294_1750

La etiqueta PDS3 está adjunta al archivo IMG (no hay archivo LBL separado para este DTM).

| Propiedad | Valor |
|---|---|
| Latitud mínima / máxima | −4.9231148946946 / −4.676204001717° |
| Longitud oeste / este | 137.35334875 / 137.46855246° E |
| Dimensiones | 6749 columnas × 14466 filas |
| Escala | 1.0117467945795 m/píxel |
| Resolución angular | 58586.494013 píxeles/grado |
| Proyección | Equirectangular |
| Latitud | Planetocéntrica |
| Longitud | Positiva al este |
| Centro de proyección | 0° latitud; 137.41° longitud |
| Radio esférico | 3396190 m |
| Referencia vertical | Superficie equipotencial Mars 2000 Datum |

Lectura: registro de etiqueta de 26996 bytes, imagen float32 little-endian, un registro por fila. Coordenadas de píxel PDS de base uno:

```
line = -273961.5 - latitude * 58586.494013 + 1
sample = 3319.5 + (longitude - 137.41) * 58586.494013 + 1
```

## Objetivos ChemCam

718 registros, 718 nombres distintos, soles 2300–3007.

- Latitud: −4.73677143 a −4.72568617°.
- Longitud: 137.3793272 a 137.3998264° E.
- Extensión aproximada: 1215 m este-oeste × 657 m norte-sur.
- Todos están dentro de los límites del DTM.
- Se consultaron los píxeles nativos más cercanos: **718/718 elevaciones válidas**.
- Esto no demuestra ausencia de huecos entre objetivos ni transitabilidad humana.

Se detectó una inconsistencia en la etiqueta XML: los campos 10 y 11 se llaman Northing/Easting en orden opuesto al encabezado CSV. Se usa el encabezado CSV. Sus valores concuerdan con `E = R × lon_rad`, `N = R × lat_rad`, R = 3396190 m: máximos residuos de 0.00868 m y 0.00530 m. Esto es coherencia numérica interna, no exactitud geográfica ni confirmación independiente del datum.

## Recorte incluido

Filas PDS 2800–3652 y columnas 1400–2852, muestreadas cada 12 píxeles: 122 × 72 celdas. Tamaño de celda ~12.14 m. Se preservan datos ausentes como null. Las rutas se ajustan al centro de celda más cercano: desplazamiento máximo aproximado de 8.6 m. Pendientes por diferencias finitas sobre el recorte; detalles subcuadrícula y obstáculos pequeños no están representados.

Se incorporó la ortofotografía `PSP_009149_1750_RED_C_01_ORTHO`, con la misma proyección, escala y offsets PDS del DTM. Se recortan los píxeles de base cero [1399, 2799, 2863, 3663), a 1464 × 864 píxeles. La esquina superior izquierda corresponde al origen de la cuadrícula; cada celda equivale a 12 píxeles de la imagen. Se conserva la banda RED en escala de grises, sin inventar colores naturales. Créditos: NASA/JPL/University of Arizona. Véase `/public/imagery/metadata.json`.

Queda pendiente la verificación independiente de la precisión absoluta horizontal y la referencia vertical de las alturas científicas. APXS y CRISM no forman parte de esta cobertura validada.
