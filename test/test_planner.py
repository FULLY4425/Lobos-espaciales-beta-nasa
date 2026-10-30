import json
import math
from pathlib import Path
import unittest
from mars.planner import find_path, grid_point, route_metrics, plan_mission
ROOT=Path(__file__).resolve().parents[1]
class PlannerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.terrain=json.loads((ROOT/'public/data/terrain.json').read_text())
        cls.targets=json.loads((ROOT/'public/data/targets.json').read_text())
    def flat(self):
        return dict(width=5,height=5,cellMeters=10,elevations=[0]*25)
    def test_diagonal_distance(self):
        t=self.flat();p=find_path(t,(0,0),(4,4))
        self.assertEqual(len(p),5)
        self.assertAlmostEqual(route_metrics(t,p)['distance'],40*math.sqrt(2))
    def test_missing_barrier(self):
        t=self.flat()
        for y in range(5):t['elevations'][y*5+2]=None
        self.assertIsNone(find_path(t,(0,2),(4,2)))
    def test_no_corner_cutting(self):
        t=dict(width=2,height=2,cellMeters=10,elevations=[0,None,None,0])
        self.assertIsNone(find_path(t,(0,0),(1,1)))
    def test_steep_or_outside(self):
        t=self.flat();t['elevations'][12]=100
        self.assertIsNone(find_path(t,(0,0),(2,2)))
        self.assertIsNone(find_path(t,(-1,0),(2,2)))
    def test_all_targets(self):
        self.assertEqual(len(self.targets),718)
        for p in self.targets:
            x,y=grid_point(self.terrain,p)
            self.assertTrue(0<=x<self.terrain['width'] and 0<=y<self.terrain['height'])
            self.assertIsNotNone(self.terrain['elevations'][y*self.terrain['width']+x])
    def test_real_mission(self):
        m=plan_mission(self.terrain,self.targets,dict(stops=[self.targets[0]['name'],self.targets[-1]['name']]))
        self.assertGreater(m['metrics']['distance'],1000)
        self.assertEqual(len(m['route']),len(m['gridPath']))
        self.assertTrue(m['educationalSimulation']);self.assertFalse(m['returnIncluded'])
    def test_bad_inputs(self):
        for p in [{},{'stops':['unknown','other']},{'stops':['Stornoway']},{'stops':['Stornoway','Stornoway']},{'stops':['Stornoway','Whaligoe'],'maxSlopeDegrees':float('nan')},{'stops':['Stornoway','Whaligoe'],'maxSlopeDegrees':True}]:
            with self.assertRaises(ValueError):plan_mission(self.terrain,self.targets,p)
