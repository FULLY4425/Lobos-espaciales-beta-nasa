"""Convert a SCANsat altimetry CSV to a small portable map, without loading it all."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from integrations.ksp_maps import scansat_region


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('csv',type=Path)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--body',required=True,help='Exact KSP body name')
    p.add_argument('--radius',type=float,required=True,help='Actual body radius in meters')
    p.add_argument('--lat',type=float,required=True)
    p.add_argument('--lon',type=float,required=True)
    p.add_argument('--size',type=int,choices=(17,33,41),default=33)
    p.add_argument('--cell',type=float,default=250,help='Meters, choose no finer than the CSV resolution')
    p.add_argument('--ocean',action='store_true',help='Only if this body has an ocean: negative terrain is water')
    args=p.parse_args()
    try:
        with args.csv.open(encoding='utf-8-sig',newline='') as stream:
            data=scansat_region(stream,body=args.body,radius=args.radius,latitude=args.lat,longitude=args.lon,size=args.size,cell=args.cell,ocean=args.ocean)
        args.output.write_text(json.dumps(data,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    except (OSError,ValueError) as error:p.exit(1,f'No se pudo convertir: {error}\n')
    c=data['conversion'];print(f"Mapa guardado: {args.output} · {c['cellsWithData']}/{c['totalCells']} celdas con datos. Los huecos no son transitables.")


if __name__=='__main__':main()
