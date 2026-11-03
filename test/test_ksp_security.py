"""HTTP boundary regression checks; run with network/loopback permission."""
import http.client
import json
import uuid
from unittest.mock import Mock
import tempfile
import threading
import unittest
from pathlib import Path
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from integrations.ksp_server import Telemetry, create_handler


class LocalBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.telemetry=Telemetry()
        try:self.server=ThreadingHTTPServer(('127.0.0.1',0),create_handler(self.telemetry))
        except PermissionError:self.skipTest('Loopback sockets unavailable in sandbox')
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.port=self.server.server_port

    def tearDown(self):
        if hasattr(self,'server'):self.server.shutdown();self.server.server_close();self.thread.join()

    def request(self,path,method='GET',headers=None,body=None):
        c=http.client.HTTPConnection('127.0.0.1',self.port,timeout=3)
        c.request(method,path,body=body,headers=headers or {})
        r=c.getresponse();result=r.status,dict(r.getheaders()),r.read();c.close();return result

    def test_external_host_and_foreign_or_null_origin_cannot_read_private_endpoints(self):
        for path in ['/api/ksp/info','/api/ksp/session/export','/api/ksp/cloud','/ksp-map.html']:
            for headers in [{'Host':'attacker.example'}, {'Origin':'https://attacker.example'}, {'Origin':'null'}, {'Sec-Fetch-Site':'cross-site'}]:
                with self.subTest(path=path,headers=headers):self.assertEqual(self.request(path,headers=headers)[0],403)
        self.assertEqual(self.request('/api/ksp/info',headers={'Origin':f'http://localhost:{self.port}'})[0],200)

    def test_get_and_head_deny_private_paths_and_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp,patch('server.ROOT',Path(tmp)):
            root=Path(tmp);(root/'.ksp-cloud').mkdir();(root/'.ksp-cloud/auth.json').write_text('SECRET')
            (root/'docs').mkdir();(root/'docs/private.json').symlink_to(root/'.ksp-cloud/auth.json')
            (root/'docs/guide.md').write_text('Public guide')
            for method in ['GET','HEAD']:
                for path in ['/.ksp-cloud/auth.json','/%2eksp-cloud/auth.json','/docs/private.json','/integrations/ksp_server.py']:
                    with self.subTest(method=method,path=path):
                        status,_,body=self.request(path,method);self.assertEqual(status,404);self.assertNotIn(b'SECRET',body)
                self.assertEqual(self.request('/docs/guide.md',method)[0],200)

    def test_cross_site_post_cannot_revoke_or_record_events(self):
        for path in ['/api/ksp/cloud/control','/api/ksp/session/events','/api/ksp/maps/plan']:
            self.assertEqual(self.request(path,'POST',{'Origin':'https://attacker.example'})[0],403)

    def test_event_batch_retry_is_deduplicated_and_wrong_instance_rejected(self):
        self.telemetry.recorder=Mock()
        body=dict(batchId=str(uuid.uuid4()),instanceId=self.telemetry.instance_id,events=[dict(type='arrival-confirmed',text='test')])
        for _ in range(2):self.assertEqual(self.request('/api/ksp/session/events','POST',{'Content-Type':'application/json'},json.dumps(body))[0],200)
        self.telemetry.recorder.event.assert_called_once()
        body['instanceId']='other'
        self.assertEqual(self.request('/api/ksp/session/events','POST',{'Content-Type':'application/json'},json.dumps(body))[0],409)
