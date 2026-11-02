"""Publish the complete archived SCANsat export, preserving unscanned pixels."""
import csv
import io
import json
from pathlib import Path
import shutil
import zipfile
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'docs/ksp-logs/2026-11-01-FULLY4425-travesia'

def build_atlas(source):
    width,height=1126,563
    values=[None]*(width*height)
    for row in csv.DictReader(source):
        x,y=int(row['Column']),height-1-int(row['Row'])
        if not 0<=x<width or not 0<=y<height:raise ValueError('Invalid SCANsat pixel')
        values[y*width+x]=round(float(row['Height'])*10)
    return dict(schema='ksp-global-height-v1',body='Duna',bodyRadius=320000,width=width,height=height,
                heightScale=.1,pixelConvention='scansat',west=-180,east=180,north=90,south=-90,
                validSamples=sum(v is not None for v in values),heights=values,
                source='/docs/ksp-logs/2026-11-01-FULLY4425-travesia/scansat-duna-1919-csv.zip',
                credit='FULLY4425 · SCANsat 21.1 · exportación real de Duna, 19:19; altimetría y Ore')

if __name__=='__main__':
    with zipfile.ZipFile(SOURCE/'scansat-duna-1919-csv.zip') as package:
        with package.open(package.namelist()[0]) as raw:data=build_atlas(io.TextIOWrapper(raw,encoding='utf-8-sig'))
    (ROOT/'public/data/duna-global.json').write_text(json.dumps(data,separators=(',',':'),ensure_ascii=False)+'\n')
    shutil.copyfile(SOURCE/'scansat-duna-1919-altimetria.png',ROOT/'public/imagery/duna-global.png')
    print('Published complete Duna export:',data['validSamples'],'samples; original PNG unchanged')
