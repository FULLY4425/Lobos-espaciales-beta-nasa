import math,unittest
from integrations.ksp_environment import training_environment
from integrations.ksp_navigation import demo_terrain,plan_ksp_mission,grid_to_geo

class WeatherTests(unittest.TestCase):
    def test_training_presets_and_direction(self):
        t=demo_terrain()
        for scenario,speed,gust,visibility in [('clear',0,0,20000),('wind',12,20,5000),('dust',8,14,1500),('storm',25,40,200)]:
            state,blocked=training_environment(t,scenario,270)
            self.assertEqual(state['wind'],dict(speedMS=speed,gustMS=gust,fromDegrees=270))
            self.assertEqual(state['visibilityMeters'],visibility)
            self.assertEqual(bool(blocked),scenario=='storm')
        for invalid in [True,-1,360,math.nan,math.inf,'90']:
            with self.assertRaises(ValueError):training_environment(t,'wind',invalid)

    def test_wind_changes_estimate_not_heights_and_is_exported(self):
        t=demo_terrain();t['elevations']=[0.]*1089;before=list(t['elevations'])
        payload=dict(terrainId=t['id'],body=t['body'],speedMS=2,stops=[dict(name='A',**grid_to_geo(t,3,16)),dict(name='B',**grid_to_geo(t,28,16))])
        clear=plan_ksp_mission(t,payload);wind=plan_ksp_mission(t,dict(payload,weather='wind',windDirection=180))
        self.assertEqual(clear['gridPath'],wind['gridPath']);self.assertEqual(t['elevations'],before)
        self.assertGreater(wind['metrics']['durationMinutes'],clear['metrics']['durationMinutes'])
        self.assertEqual(wind['environment']['wind']['fromDegrees'],180)
