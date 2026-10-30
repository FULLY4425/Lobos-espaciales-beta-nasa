"""Download documented NASA/PDS products, extract a small Gale DTM window.
No third-party dependencies. TLS verification remains enabled.
"""
import urllib.request,csv,io,struct,json,math,pathlib,hashlib,datetime
OUT=pathlib.Path(__file__).resolve().parents[1]/'public/data';OUT.mkdir(parents=True,exist_ok=True)
BASE='https://pds-geosciences.wustl.edu/msl/urn-nasa-pds-msl_gt_diagenesis_supplement/'
DTM='https://www.uahirise.org/PDS/DTM/PSP/ORB_009100_009199/PSP_009149_1750_PSP_009294_1750/DTEEC_009149_1750_009294_1750_U01.IMG'
def get(u):
 with urllib.request.urlopen(u,timeout=90) as r:return r.read()
raw=get(BASE+'data/target_classification.csv');(OUT/'target_classification.csv').write_bytes(raw)
for name in ['readme.txt','data/target_classification.xml']:(OUT/pathlib.Path(name).name).write_bytes(get(BASE+name))
rows=list(csv.DictReader(io.StringIO('\n'.join(raw.decode('utf-8-sig').splitlines()[1:]))))
points=[]
for r in rows:
 points.append(dict(name=r['Target'],sol=int(r['Sol']),lat=float(r['Latitude (dd)']),lon=float(r['Longitude (dd)']),elevation=float(r['Elevation (m)']),formation=r['Formation'],member=r['Stratigraphic Member'],veins=r['RMI has veins']=='1',nodules=r['RMI has nodules']=='1',sequence=r['SeqID']))
# Native PDS image: 26996-byte attached label record, little endian float32.
# 12-pixel sampling, no interpolation; preserve nulls instead of inventing terrain.
l0,l1,c0,c1=2800,3652,1400,2852;step=12;rb=26996
start=l0*rb;end=(l1+1)*rb-1
with urllib.request.urlopen(urllib.request.Request(DTM,headers={'Range':f'bytes={start}-{end}'}),timeout=90) as r:
 if r.status!=206:raise RuntimeError('Server must honor byte ranges')
 data=r.read()
w=len(range(c0,c1+1,step));h=len(range(l0,l1+1,step));values=[]
for l in range(l0,l1+1,step):
 for c in range(c0,c1+1,step):
  v=struct.unpack_from('<f',data,(l-l0)*rb+(c-1)*4)[0];values.append(round(v,2) if -4406.78<=v<=-2268.75 else None)
res=58586.494013
terrain=dict(width=w,height=h,cellMeters=step*1.0117467945795,west=137.41+(c0-1-3319.5)/res,north=(-273961.5-l0+1)/res,degreeStep=step/res,elevations=values,source=DTM,nativeCellMeters=1.0117467945795)
valid=0
for p in points:
 l=round(-273961.5-p['lat']*res+1);c=round(3319.5+(p['lon']-137.41)*res+1)
 v=struct.unpack_from('<f',data,(l-l0)*rb+(c-1)*4)[0];valid+=-4406.78<=v<=-2268.75
(OUT/'targets.json').write_text(json.dumps(points,ensure_ascii=False))
(OUT/'terrain.json').write_text(json.dumps(terrain))
(OUT/'provenance.json').write_text(json.dumps(dict(retrievedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),targetCount=len(points),validNativePixels=valid,csvSha256=hashlib.sha256(raw).hexdigest(),terrainWindowSha256=hashlib.sha256(data).hexdigest(),terrainByteRange=[start,end],sources=[BASE,DTM],warning='Downsampled terrain is educational; not certified for astronaut navigation.'),indent=2))
print(f'{len(points)} targets; {valid} valid native pixels; terrain {w} x {h}')

# Supporting research material; APXS is reference only, not plotted in the app.
apxs='https://pds-geosciences.wustl.edu/msl/urn-nasa-pds-msl_apxs_supplement_sols_3054_3712/'
(OUT/'apxs-reference').mkdir(exist_ok=True)
for name in ['readme.txt','data/ds01_2024.csv','data/ds01_2024.xml']:
 (OUT/'apxs-reference'/pathlib.Path(name).name).write_bytes(get(apxs+name))
with urllib.request.urlopen(urllib.request.Request(DTM,headers={'Range':'bytes=0-26995'}),timeout=90) as response:
 if response.status!=206:raise RuntimeError('Server must honor byte ranges')
 (OUT/'hirise-attached-label.txt').write_bytes(response.read(26996).rstrip(b'\x00 '))
