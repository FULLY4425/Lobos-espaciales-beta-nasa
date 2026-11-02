import copy
import hashlib
import io
import json
from pathlib import Path
import unittest
from integrations.ksp_navigation import demo_terrain,grid_to_geo,plan_ksp_mission
from integrations.ksp_environment import training_environment
from scripts.build_duna_atlas import build_atlas
ROOT=Path(__file__).resolve().parents[1]

class DunaAtlasTests(unittest.TestCase):
    def setUp(self):
        self.terrain=demo_terrain()
        self.terrain['elevations']=[10.]*1089
        self.payload=dict(terrainId=self.terrain['id'],body=self.terrain['body'],maxSlopeDegrees=15,speedMS=2,avoidWater=True,
                          stops=[dict(name=name,**grid_to_geo(self.terrain,x,16)) for name,x in [('Inicio',5),('Destino',28)]])

    def test_storm_routes_around_restricted_cells_and_marks_simulated_provenance(self):
        clear=plan_ksp_mission(self.terrain,self.payload)
        storm=plan_ksp_mission(self.terrain,dict(self.payload,weather='storm',replanReason='weather'))
        environment,blocked=training_environment(self.terrain,'storm')
        self.assertTrue(blocked)
        self.assertFalse(any(tuple(p) in blocked for p in storm['gridPath']))
        self.assertGreater(storm['metrics']['distance'],clear['metrics']['distance'])
        self.assertGreater(storm['metrics']['durationMinutes'],clear['metrics']['durationMinutes'])
        self.assertEqual(storm['environment']['sourceType'],'synthetic-training')
        self.assertEqual(storm['planningContext']['reason'],'weather')
        self.assertEqual(storm['speedMS'],2)

    def test_goal_in_training_storm_is_rejected_without_mutating_terrain(self):
        before=copy.deepcopy(self.terrain)
        payload=copy.deepcopy(self.payload)
        payload['stops'][1].update(grid_to_geo(self.terrain,21,15))
        payload['weather']='storm'
        with self.assertRaises(ValueError):plan_ksp_mission(self.terrain,payload)
        self.assertEqual(self.terrain,before)

    def test_unknown_and_non_string_weather_are_rejected(self):
        for value in ['observed',{},None,False]:
            with self.subTest(value=value),self.assertRaises(ValueError):
                plan_ksp_mission(self.terrain,dict(self.payload,weather=value))

    def test_global_export_and_original_image_remain_complete(self):
        data=json.loads((ROOT/'public/data/duna-global.json').read_text())
        self.assertEqual(len(data['heights']),1126*563)
        self.assertEqual(sum(v is not None for v in data['heights']),529220)
        image=(ROOT/'public/imagery/duna-global.png').read_bytes()
        original=(ROOT/'docs/ksp-logs/2026-11-01-FULLY4425-travesia/scansat-duna-1919-altimetria.png').read_bytes()
        self.assertEqual(hashlib.sha256(image).digest(),hashlib.sha256(original).digest())

    def test_atlas_builder_flips_rows_and_preserves_zero_negative_and_missing_heights(self):
        data=build_atlas(io.StringIO('Row,Column,Height\n0,0,-1.2\n562,1125,0\n'))
        self.assertEqual(data['heights'][562*1126],-12)
        self.assertEqual(data['heights'][1125],0)
        self.assertIsNone(data['heights'][0])
        self.assertEqual(data['validSamples'],2)
