import math
import sys
import time
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from integrations.ksp_server import Telemetry, validate_sample


class KspBridgeTests(unittest.TestCase):
    def sample(self):
        return dict(latitude=0., longitude=10., heading=90., surfaceAltitude=2., speed=3.,
                    bodyRadius=320000., body='Duna', vessel='Rover', vesselId='id')

    def test_valid_sample_is_finite_and_has_freshness_metadata(self):
        data = validate_sample(self.sample())
        self.assertTrue(data['readOnly'])
        self.assertEqual(data['source'], 'KSP1-kRPC')
        self.assertAlmostEqual(data['receivedAt'], time.time(), delta=1)
        for change in (dict(latitude=True), dict(speed=math.nan), dict(bodyRadius=0), dict(latitude=91)):
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_sample(self.sample() | change)

    def test_stale_or_absent_data_never_reports_connected(self):
        telemetry = Telemetry()
        self.assertEqual(telemetry.snapshot()[0], 503)
        telemetry.sample = validate_sample(self.sample())
        self.assertEqual(telemetry.snapshot()[0], 200)
        telemetry.sample['receivedAt'] -= 4
        self.assertEqual(telemetry.snapshot()[0], 503)

    def test_scene_transition_keeps_rpc_connection_and_waits(self):
        telemetry=Telemetry()
        class SpaceCenter:
            reads=0
            @property
            def active_vessel(self):
                self.reads+=1
                if self.reads==2:telemetry.stopped.set()
                return None
        connection=SimpleNamespace(space_center=SpaceCenter(),close=Mock())
        client=SimpleNamespace(connect=Mock(return_value=connection))
        with patch.dict(sys.modules,{'krpc':client}),patch.object(telemetry.stopped,'wait') as wait:
            telemetry.run()
        client.connect.assert_called_once()
        self.assertEqual(connection.space_center.reads,2)
        self.assertEqual(wait.call_args.args,(1,))
        self.assertEqual(telemetry.snapshot()[0],503)
        connection.close.assert_called_once()

    def test_sampler_only_reads_flight_data_and_closes_connection(self):
        telemetry = Telemetry()
        body = SimpleNamespace(name='Duna', equatorial_radius=320000., reference_frame=object())

        class Flight:
            latitude, longitude, heading, surface_altitude = 0., 10., 90., 2.
            @property
            def speed(self):
                telemetry.stopped.set()
                return 3.

        class Vessel:
            name, orbit = 'Rover', SimpleNamespace(body=body)
            frames = []
            def flight(self, reference_frame=None):
                self.frames.append(reference_frame)
                return Flight()
            @property
            def control(self):
                raise AssertionError('Must not access vehicle controls')

        vessel = Vessel()
        connection = SimpleNamespace(space_center=SimpleNamespace(active_vessel=vessel), close=Mock())
        client = SimpleNamespace(connect=Mock(return_value=connection))
        with patch.dict(sys.modules, {'krpc': client}):
            telemetry.run()
        self.assertEqual(telemetry.snapshot()[0], 200)
        self.assertEqual(vessel.frames, [body.reference_frame, None])
        self.assertEqual(client.connect.call_args.kwargs['address'], '127.0.0.1')
        self.assertEqual(client.connect.call_args.kwargs['timeout'], 2)
        connection.close.assert_called_once()
