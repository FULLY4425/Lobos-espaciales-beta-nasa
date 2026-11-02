"""Build a SCANsat PNG coverage mask from exported CSV row/column indices.

Usage: python3 scripts/ksp_texture_coverage.py export.zip mask.json --width 1126 --height 563
Rows in the export run south to north; PNG rows run north to south.
No elevation values or image colours are inferred for missing samples.
"""
import argparse
import csv
import io
import json
from pathlib import Path
import zipfile

def build_coverage(source, width, height):
    rows = {}
    for item in csv.DictReader(source):
        x, south_row = int(item['Column']), int(item['Row'])
        if not (0 <= x < width and 0 <= south_row < height):
            raise ValueError('CSV indices exceed image dimensions')
        rows.setdefault(height - 1 - south_row, set()).add(x)
    packed = {}
    for y, values in sorted(rows.items()):
        runs = []
        for x in sorted(values):
            if runs and x == runs[-1][1] + 1:
                runs[-1][1] = x
            else:
                runs.append([x, x])
        packed[str(y)] = runs
    return dict(width=width, height=height, rows=packed)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv_zip', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--width', type=int, required=True)
    parser.add_argument('--height', type=int, required=True)
    args = parser.parse_args()
    with zipfile.ZipFile(args.csv_zip) as package:
        names = [n for n in package.namelist() if n.lower().endswith('.csv')]
        if len(names) != 1:
            parser.error('Expected one CSV in ZIP')
        with package.open(names[0]) as raw:
            mask = build_coverage(io.TextIOWrapper(raw, encoding='utf-8-sig'), args.width, args.height)
    args.output.write_text(json.dumps(mask, separators=(',', ':')) + '\n')
    print('Coverage written; scanned pixels:', sum(b-a+1 for runs in mask['rows'].values() for a,b in runs))
