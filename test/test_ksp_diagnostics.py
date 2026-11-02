import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch
from integrations.ksp_diagnostics import ComputerMonitor,read_flight
from integrations.ksp_session import SessionRecorder
from test_ksp_cloud import FakeClient
from integrations.ksp_cloud import CloudUploader

class DiagnosticsTests(unittest.TestCase):
    def test_flight_is_optional_finite_and_read_only(self):
        class Vessel:
            orbit=NS(apoapsis_altitude=1000,periapsis_altitude=500,inclination=.1,eccentricity=.2,time_to_apoapsis=20,time_to_periapsis=30)
            mass=1200;situation=NS(name='orbiting')
            @property
            def control(self):raise AssertionError('No controls allowed')
            def flight(self,*args):return NS(mean_altitude=800,vertical_speed=float('nan'),horizontal_speed=30,g_force=.1,pitch=10,roll=0)
        data=read_flight(Vessel(),NS(reference_frame='body'))
        self.assertEqual(data['situation'],'orbiting');self.assertIsNone(data['verticalSpeed']);self.assertEqual(data['massKg'],1200)
        self.assertTrue(data['readOnly']);json.dumps(data,allow_nan=False)

    def test_computer_allowlist_excludes_other_programs_and_identifiers(self):
        class Process:
            def __init__(self,pid,name):self.pid=pid;self.info={'pid':pid,'name':name,'username':'private-user','cmdline':['secret']}
            def cpu_percent(self,**kw):return 12
            def memory_info(self):return NS(rss=4096)
        processes=[Process(11,'KSP_x64.exe'),Process(12,'personal-browser')]
        provider=NS(cpu_percent=lambda **kw:20,virtual_memory=lambda:NS(percent=40,used=400,total=1000),Process=lambda pid:Process(pid,'connector'),process_iter=lambda attrs:processes)
        with tempfile.TemporaryDirectory() as root:
            m=ComputerMonitor(storage_path=root,provider=provider);first=m.collect();data=m.collect()
        self.assertIsNone(first['cpuPercent']);self.assertEqual(data['cpuPercent'],20);self.assertEqual(len(data['kspProcesses']),1)
        self.assertNotIn('private-user',json.dumps(data));self.assertNotIn('personal-browser',json.dumps(data));self.assertNotIn('secret',json.dumps(data));self.assertIsNone(data['fps'])

    def test_diagnostics_failure_does_not_fabricate_cpu_ram(self):
        with tempfile.TemporaryDirectory() as root:
            m=ComputerMonitor(storage_path=root);m.provider=None;data=m.collect()
        self.assertEqual(data['status'],'partial');self.assertIsNone(data['cpuPercent']);self.assertIsNone(data['kspDetected'])

    def test_summary_and_zip_include_computer_flight_without_private_files(self):
        with tempfile.TemporaryDirectory() as root:
            r=SessionRecorder(root);r.diagnostic('computer',dict(cpuPercent=95,ramPercent=91));r.diagnostic('flight',dict(meanAltitude=1000,verticalSpeed=20));r.event('krpc-unavailable',{});r.event('browser-performance-snapshot',dict(text=json.dumps(dict(renderCpu=dict(maxMs=150)))))
            (r.path/'passwords.txt').write_text('not evidence');r.event('stop',dict(reason='test'))
            summary=r.analysis();self.assertEqual(summary['diagnosticSamples'],dict(computer=1,flight=1));self.assertGreaterEqual(len(summary['recommendations']),3)
            z=zipfile.ZipFile(io.BytesIO(r.export()));self.assertTrue({'analysis.json','flight.jsonl','computer.jsonl'}<=set(z.namelist()));self.assertNotIn('passwords.txt',z.namelist());self.assertIsNotNone(json.loads(z.read('session.json'))['stoppedAt'])

    def test_final_sync_includes_stop_event_and_diagnostics_when_worker_stopped(self):
        with tempfile.TemporaryDirectory() as root:
            config=Path(root)/'.config/config.json';config.parent.mkdir();r=SessionRecorder(Path(root)/'sessions');client=FakeClient(config);u=CloudUploader(r,client=client)
            r.diagnostic('computer',dict(cpuPercent=20));r.event('stop',dict(reason='test'));u.stop_event.set();u.sync_once(final=True)
            content=next(iter(client.objects.values()));z=zipfile.ZipFile(io.BytesIO(content));self.assertIn('computer.jsonl',z.namelist());self.assertIsNotNone(json.loads(z.read('session.json'))['stoppedAt'])
            self.assertEqual(len(client.rows),1);row=next(iter(client.rows.values()));self.assertIsNotNone(row['stopped_at']);self.assertEqual(row['diagnostic_summary']['diagnosticSamples']['computer'],1)

    def test_pause_prevents_final_upload_and_retains_local_diagnostics(self):
        with tempfile.TemporaryDirectory() as root:
            config=Path(root)/'.config/config.json';config.parent.mkdir();r=SessionRecorder(Path(root)/'sessions');client=FakeClient(config);u=CloudUploader(r,client=client);u.paused=True;r.diagnostic('flight',dict(meanAltitude=10));u.sync_once(final=True)
            self.assertFalse(client.uploads);self.assertTrue((r.path/'flight.jsonl').exists())

    def test_close_running_worker_sends_final_stopped_snapshot(self):
        import threading
        with tempfile.TemporaryDirectory() as root:
            config=Path(root)/'.config/config.json';config.parent.mkdir();r=SessionRecorder(Path(root)/'sessions');client=FakeClient(config);sent=threading.Event();original=client.index
            def index(data,auth):original(data,auth);sent.set()
            client.index=index;u=CloudUploader(r,client=client);u.start();self.assertTrue(sent.wait(2));r.diagnostic('flight',dict(meanAltitude=12));r.event('stop',dict(reason='test'));u.close()
            self.assertFalse(u.thread.is_alive());z=zipfile.ZipFile(io.BytesIO(next(iter(client.objects.values()))));self.assertIn('flight.jsonl',z.namelist());self.assertIsNotNone(json.loads(z.read('session.json'))['stoppedAt'])

    def test_network_failure_keeps_final_zip_for_next_start(self):
        import threading
        with tempfile.TemporaryDirectory() as root:
            config=Path(root)/'.config/config.json';config.parent.mkdir();r=SessionRecorder(Path(root)/'sessions');client=FakeClient(config);failed=threading.Event()
            def upload(*args):failed.set();raise __import__('integrations.ksp_cloud',fromlist=['CloudError']).CloudError('offline')
            client.upload=upload;u=CloudUploader(r,client=client);u.start();self.assertTrue(failed.wait(2));r.event('stop',dict(reason='test'));u.close()
            self.assertFalse(u.thread.is_alive());self.assertTrue((r.path/'.cloud-pending.zip').exists());self.assertTrue(u.status()['finalUploadPending']);self.assertTrue((r.path/'events.jsonl').exists())
