import io
import json
import unittest
from integrations.ksp_navigation import demo_terrain, grid_to_geo, plan_ksp_mission
from integrations.ksp_maps import archive, read_archive, scansat_region, plan_archive


class PortableKspMapsTests(unittest.TestCase):
    def terrain(self):
        t=demo_terrain();t['body']='Duna';t['sourceType']='KSP1-kRPC-bedrock';t['elevations']=[100.]*1089
        return t

    def test_archive_identity_survives_json_integer_float_and_rejects_fake_id(self):
        data=archive(self.terrain());converted=json.loads(json.dumps(data).replace('320000.0','320000'))
        converted['terrain']['id']='fake'
        self.assertEqual(read_archive(converted)['id'],data['terrain']['id'])
        self.assertEqual(read_archive(converted)['vesselId'],'archive')

    def test_malformed_unbounded_or_nonfinite_archives_rejected(self):
        for change in [dict(width=10000),dict(width=True),dict(cellMeters=0),dict(bodyRadius=float('nan')),dict(bodyRadius=10**1000),dict(body=''),dict(sourceType='NASA'),dict(projection='unknown'),dict(water=[1]*1089),dict(elevations=[float('inf')]*1089),dict(elevations=[None]*1089)]:
            with self.subTest(change=list(change)):
                t=self.terrain();t.update(change)
                with self.assertRaises(ValueError):archive(t)
        with self.assertRaises(ValueError):read_archive(dict(schema='mars'))

    def csv(self,t,skip=None):
        rows=['Row,Column,Lat,Long,Height']
        for y in range(33):
            for x in range(33):
                if skip and skip(x,y):continue
                p=grid_to_geo(t,x,y);z=-5 if y==0 else 100
                rows.append(f"{y},{x},{p['lat']},{p['lon']},{z}")
        # The far hemisphere is valid global data, just outside this local map.
        rows.append('0,0,0,170,4')
        return io.StringIO('\n'.join(rows))

    def test_scansat_streaming_coordinates_heights_and_ocean(self):
        t=self.terrain();data=scansat_region(self.csv(t),body='Duna',radius=t['bodyRadius'],latitude=0,longitude=0,cell=25,ocean=True)
        terrain=read_archive(data)
        self.assertEqual(data['conversion']['cellsWithData'],1089)
        self.assertEqual(terrain['sourceType'],'SCANsat-CSV')
        self.assertEqual(terrain['elevations'][16*33+16],100)
        self.assertTrue(terrain['water'][0])
        self.assertFalse(terrain['water'][33])

    def test_missing_scans_remain_holes_and_block_routes(self):
        t=self.terrain();data=scansat_region(self.csv(t,lambda x,y:x==16),body='Duna',radius=t['bodyRadius'],latitude=0,longitude=0,cell=25)
        terrain=read_archive(data)
        self.assertIsNone(terrain['elevations'][16*33+16])
        payload=dict(terrainId=terrain['id'],body='Duna',stops=[dict(name=n,**grid_to_geo(terrain,x,16)) for n,x in [('A',4),('B',28)]])
        with self.assertRaises(ValueError):plan_ksp_mission(terrain,payload)

    def test_csv_header_nonfinite_and_ambiguous_decimal_rejected(self):
        for text in ['Lat,Long,Height\n0,0,1','Row,Column,Lat,Long,Height\n0,0,0,0,nan','Row,Column,Lat,Long,Height\n0,0,0,0,1,5']:
            with self.assertRaises(ValueError):scansat_region(io.StringIO(text),body='Duna',radius=320000,latitude=0,longitude=0)

    def test_imported_plan_has_native_body_provenance_and_ignores_embedded_paths(self):
        data=archive(self.terrain());t=data['terrain']
        payload=dict(terrainId=t['id'],body=t['body'],stops=[dict(name=n,**grid_to_geo(t,x,16)) for n,x in [('A',4),('B',28)]])
        result=plan_archive(dict(map=data,mission=payload,gridPath=[[99,99]]))
        self.assertEqual(result['sourceType'],'KSP1-kRPC-bedrock')
        self.assertEqual(result['planningContext']['mapMode'],'imported-height-map')
        self.assertEqual(result['gridPath'][0],(4,16))
        payload['body']='Kerbin'
        with self.assertRaises(ValueError):plan_archive(dict(map=data,mission=payload))

    def test_telemetry_heading_uses_local_surface_frame(self):
        from types import SimpleNamespace
        from integrations.ksp_server import read_vessel_sample
        body=SimpleNamespace(reference_frame=object(),equatorial_radius=600000,name='Kerbin')
        fixed=SimpleNamespace(latitude=0,longitude=0,heading=171.8,surface_altitude=1,speed=2)
        surface=SimpleNamespace(heading=151)
        orbit_ref=SimpleNamespace(body=body)
        class Vessel:
            orbit=orbit_ref
            name='Rover'
            def flight(self,*args):return fixed if args else surface
        actual_body,sample=read_vessel_sample(Vessel(),'test')
        self.assertIs(actual_body,body)
        self.assertEqual(sample['heading'],151)
        self.assertEqual(sample['speed'],2)

    def test_archived_real_scansat_csv_reproduces_region_and_route(self):
        import zipfile
        from pathlib import Path
        root=Path(__file__).resolve().parents[1]/'docs/ksp-logs/2026-11-01-FULLY4425-scansat'
        with zipfile.ZipFile(root/'scansat-duna-csv.zip') as z:
            text=z.read(z.namelist()[0]).decode('utf-8-sig')
        result=scansat_region(io.StringIO(text),body='Duna',radius=320000,latitude=-13.268,longitude=-133.961,size=17,cell=2000)
        archived=json.loads((root/'duna-region-scansat.json').read_text())
        self.assertEqual(result['terrain']['elevations'],archived['terrain']['elevations'])
        self.assertEqual(result['conversion']['cellsWithData'],280)
        mission=json.loads((root/'mision-ruta-scansat.json').read_text())
        request=dict(mission['request'],terrainId=result['terrain']['id'])
        route=plan_archive(dict(map=result,mission=request))
        self.assertAlmostEqual(route['metrics']['distance'],mission['response']['metrics']['distance'])
        self.assertEqual(route['gridPath'],[tuple(p) for p in mission['response']['gridPath']])
