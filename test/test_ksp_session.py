import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from integrations.ksp_session import SessionRecorder
from integrations.ksp_server import Telemetry


class KspSessionTests(unittest.TestCase):
    def test_unique_sessions_keep_artifacts_and_telemetry_without_overwrite(self):
        with tempfile.TemporaryDirectory() as root:
            a,b=SessionRecorder(root),SessionRecorder(root)
            self.assertNotEqual(a.path,b.path)
            a.sample(dict(body='Duna',speed=15));a.sample(dict(body='Duna',speed=16))
            a.artifact('terrain',dict(id='one',elevations=[10,20]))
            a.artifact('mission',dict(gridPath=[[0,0],[1,0]]))
            z=zipfile.ZipFile(io.BytesIO(a.export()));names=z.namelist()
            self.assertIn('session.json',names)
            self.assertEqual(len(z.read('telemetry.jsonl').splitlines()),1)
            self.assertTrue(any(x.startswith('terrain-') for x in names))
            self.assertTrue(any(x.startswith('mission-') for x in names))
            self.assertEqual(json.loads(z.read('session.json'))['schema'],'ksp-connector-session-v1')
            self.assertTrue(b.path.exists())

    def test_disk_limit_is_reported_and_never_silently_overwrites(self):
        with tempfile.TemporaryDirectory() as root:
            a=SessionRecorder(root,max_bytes=500)
            a.event('large',dict(text='x'*1000))
            self.assertGreater(a.status()['dropped'],0)
            self.assertLessEqual(a.status()['bytes'],500)
            self.assertEqual(json.loads(zipfile.ZipFile(io.BytesIO(a.export())).read('session.json'))['dropped'],a.status()['dropped'])

    def test_filesystem_failure_does_not_break_telemetry(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/'file';p.write_text('occupied')
            a=SessionRecorder(p)
            self.assertTrue(a.status()['error'])
            telemetry=Telemetry(recorder=a)
            self.assertEqual(telemetry.snapshot()[0],503)
            self.assertEqual(telemetry.info()['version'],'1.4.0')
            self.assertTrue(telemetry.info()['recording']['error'])
