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

    def custom_terrain(self):
        return dict(self.flat(),west=137,north=-4,degreeStep=.001,source='test')
    def test_custom_and_mixed_stops(self):
        t=self.custom_terrain()
        custom=dict(type='custom',name='Mi punto',lat=-4.004,lon=137.004,elevation=99999,sol=999)
        mission=plan_mission(t,[dict(name='NASA',lat=-4,lon=137)],dict(stops=['NASA',custom]))
        self.assertEqual(mission['gridPath'][-1],(4,4))
        self.assertEqual(mission['stops'][1]['elevation'],0)
        self.assertFalse(mission['stops'][1]['scientificObservation'])
        self.assertNotIn('sol',mission['stops'][1])
        self.assertGreater(mission['metrics']['distance'],0)
    def test_invalid_custom_stops(self):
        t=self.custom_terrain()
        base=dict(type='custom',name='Punto',lat=-4.002,lon=137.002)
        known=dict(name='NASA',lat=-4,lon=137)
        for change in [dict(lat=True),dict(lon=float('nan')),dict(lat=-3.99999),dict(lon=137.005),dict(name=''),dict(name='x'*61),dict(name='NASA'),dict(type='other')]:
            with self.subTest(change=change),self.assertRaises(ValueError):
                plan_mission(t,[known],dict(stops=['NASA',dict(base,**change)]))
        with self.assertRaises(ValueError):
            plan_mission(t,[],dict(stops=[base,base]))
        t['elevations'][12]=None
        with self.assertRaises(ValueError):
            plan_mission(t,[known],dict(stops=['NASA',base]))
    def test_custom_stops_obey_slope_and_obstacles(self):
        t=self.custom_terrain()
        a=dict(type='custom',name='A',lat=-4,lon=137)
        b=dict(type='custom',name='B',lat=-4.004,lon=137.004)
        for y in range(5):t['elevations'][y*5+2]=None
        with self.assertRaises(ValueError):
            plan_mission(t,[],dict(stops=[a,b]))
        t=self.custom_terrain();t['elevations'][24]=100
        with self.assertRaises(ValueError):
            plan_mission(t,[],dict(stops=[a,b],maxSlopeDegrees=5))
    def test_weather_blocks_area_and_routes_around_it(self):
        from mars.planner import environment_for, blocked_cells
        t=dict(width=50,height=50,cellMeters=10,elevations=[0]*2500,west=137,north=-4,degreeStep=.001,source='test')
        stops=[dict(type='custom',name='A',lat=-4.024,lon=137),dict(type='custom',name='B',lat=-4.024,lon=137.049)]
        clear=plan_mission(t,[],dict(stops=stops,weather='clear'))
        storm=plan_mission(t,[],dict(stops=stops,weather='storm'))
        blocked=blocked_cells(t,environment_for(t,'storm'))
        self.assertTrue(any(tuple(p) in blocked for p in clear['gridPath']))
        self.assertFalse(any(tuple(p) in blocked for p in storm['gridPath']))
        self.assertGreater(storm['metrics']['distance'],clear['metrics']['distance'])
        self.assertGreater(storm['metrics']['durationMinutes'],clear['metrics']['durationMinutes'])
        self.assertEqual(storm['environment']['sourceType'],'synthetic')
    def test_weather_invalid_and_no_safe_escape(self):
        t=self.custom_terrain();stops=[dict(type='custom',name='A',lat=-4,lon=137),dict(type='custom',name='B',lat=-4.004,lon=137.004)]
        for weather in [False,{},'live-nasa']:
            with self.assertRaises(ValueError):plan_mission(t,[],dict(stops=stops,weather=weather))
        with self.assertRaises(ValueError):plan_mission(t,[],dict(stops=stops,weather='storm'))
    def test_replan_from_position_keeps_destination(self):
        t=self.custom_terrain();stops=[dict(type='custom',name='Actual',lat=-4.001,lon=137.002),dict(type='custom',name='Destino',lat=-4.004,lon=137.004)]
        mission=plan_mission(t,[],dict(stops=stops,replanReason='deviation',weather='dust'))
        self.assertEqual(mission['gridPath'][0],(2,1));self.assertEqual(mission['gridPath'][-1],(4,4))
        self.assertEqual(mission['planningContext']['reason'],'deviation')
        self.assertEqual(mission['stopPathIndices'],[0,len(mission['gridPath'])-1])
