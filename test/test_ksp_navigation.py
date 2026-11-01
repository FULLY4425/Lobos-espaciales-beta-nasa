import copy
import math
import unittest
from integrations.ksp_navigation import to_geo,to_local,grid_to_geo,grid_coordinate,terrain_request,plan_ksp_mission,demo_terrain
from integrations.ksp_server import Telemetry,validate_sample


class NativeKspTests(unittest.TestCase):
    def sample(self):
        return dict(latitude=0.,longitude=179.99,heading=0.,surfaceAltitude=1.,speed=0.,bodyRadius=320000.,body='Duna',vessel='Rover',vesselId='test')

    def flat(self):
        terrain=demo_terrain();terrain['elevations']=[0.]*1089
        return terrain

    def stop(self,t,name,x,y):
        return dict(name=name,**grid_to_geo(t,x,y))

    def payload(self,t):
        return dict(terrainId=t['id'],body=t['body'],stops=[self.stop(t,'Salida',3,16),self.stop(t,'Destino',28,16)])

    def test_projection_roundtrip_at_poles_and_longitude_wrap(self):
        for center in [dict(lat=0,lon=179.999),dict(lat=89.9,lon=-179.9),dict(lat=-65,lon=30)]:
            for x,y in [(200.,-75.),(-100.,120.),(0.,0.)]:
                with self.subTest(center=center,x=x,y=y):
                    geo=to_geo(center,x,y,320000.)
                    actual=to_local(center,geo['lat'],geo['lon'],320000.)
                    self.assertAlmostEqual(actual[0],x,delta=.001)
                    self.assertAlmostEqual(actual[1],y,delta=.001)

    def test_grid_roundtrip_and_invalid_sample_request(self):
        t=terrain_request(self.sample(),dict(size=17,cellMeters=25),'id')
        for x,y in [(0,0),(8,8),(16,16)]:
            self.assertEqual(grid_coordinate(t,grid_to_geo(t,x,y)),(x,y))
        for payload in [dict(size=True),dict(size=17.0),dict(size=500),dict(cellMeters=math.nan),dict(cellMeters=1)]:
            with self.assertRaises(ValueError):terrain_request(self.sample(),payload,'bad')
        with self.assertRaises(ValueError):terrain_request(dict(self.sample(),bodyRadius=10),{},'too-big')

    def test_native_route_uses_game_coordinates_and_not_nasa_metadata(self):
        t=self.flat();mission=plan_ksp_mission(t,self.payload(t))
        self.assertEqual(mission['context']['kind'],'ksp-surface')
        self.assertEqual(mission['context']['body'],t['body'])
        self.assertNotIn('sources',mission)
        self.assertEqual(mission['stops'][1]['grid'],[28,16])
        self.assertEqual(mission['gridPath'][0],(3,16))
        self.assertEqual(mission['gridPath'][-1],(28,16))
        self.assertTrue(mission['readOnly'])
        self.assertEqual(mission['metrics']['distance'],625.)

    def test_water_and_steep_terrain_are_respected(self):
        t=self.flat()
        for y in range(33):t['water'][y*33+16]=True
        with self.assertRaises(ValueError):plan_ksp_mission(t,self.payload(t))
        self.assertTrue(plan_ksp_mission(t,dict(self.payload(t),avoidWater=False))['gridPath'])
        t['water']=[False]*1089
        for y in range(33):t['elevations'][y*33+16]=1000
        with self.assertRaises(ValueError):plan_ksp_mission(t,self.payload(t))

    def test_plan_rejects_wrong_context_and_bad_coordinates(self):
        t=self.flat();payload=self.payload(t)
        for change in [dict(body='Mars'),dict(terrainId='old'),dict(speedMS=True),dict(maxSlopeDegrees=math.nan),dict(avoidWater='yes')]:
            with self.assertRaises(ValueError):plan_ksp_mission(t,payload|change)
        bad=copy.deepcopy(payload);bad['stops'][1]['lat']=45.
        with self.assertRaises(ValueError):plan_ksp_mission(t,bad)

    def test_sampling_progress_completion_and_underwater_mask(self):
        tracker=Telemetry();tracker.sample=validate_sample(self.sample());tracker.request_terrain(dict(size=17))
        class Body:
            has_solid_surface=True
            has_ocean=True
            def bedrock_height(self,lat,lon):return -2 if lat<0 else 10
        body=Body()
        for _ in range(300):
            tracker._sample_batch(body,tracker.sample)
            if tracker.terrain_status()['status']=='complete':break
        result=tracker.terrain_status()
        self.assertEqual(result['status'],'complete')
        self.assertEqual(result['completed'],289)
        self.assertEqual(result['terrain']['body'],'Duna')
        self.assertTrue(any(result['terrain']['water']))
        self.assertTrue(all(v is not None for v in result['terrain']['elevations']))

    def test_cancellation_and_non_solid_body_fail_without_publishing(self):
        tracker=Telemetry();tracker.sample=validate_sample(self.sample());tracker.request_terrain(dict(size=17));tracker.cancel_terrain()
        self.assertEqual(tracker.terrain_status()['status'],'cancelled')
        self.assertIsNone(tracker.terrain)
        tracker.request_terrain(dict(size=17))
        class GasBody:
            has_solid_surface=False
            @property
            def bedrock_height(self):raise AssertionError('must not sample gas body')
        tracker._sample_batch(GasBody(),tracker.sample)
        self.assertEqual(tracker.terrain_status()['status'],'failed')
        self.assertIsNone(tracker.terrain)

    def test_native_planning_rejects_stale_data_and_reconnected_session(self):
        tracker=Telemetry();terrain=self.flat();tracker.terrain=terrain
        tracker.sample=validate_sample(dict(self.sample(),body=terrain['body'],bodyRadius=terrain['bodyRadius'],vesselId=terrain['vesselId']))
        self.assertTrue(tracker.plan_surface(self.payload(terrain))['readOnly'])
        tracker.sample['vesselId']='new-session:rover'
        with self.assertRaises(ValueError):tracker.plan_surface(self.payload(terrain))
        tracker.sample['receivedAt']-=10
        with self.assertRaises(RuntimeError):tracker.plan_surface(self.payload(terrain))
