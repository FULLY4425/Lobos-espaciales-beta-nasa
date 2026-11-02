import json
import tempfile
import time
import unittest
from pathlib import Path
from integrations.ksp_cloud import SupabaseClient,CloudError,atomic_json

UID='12345678-1234-1234-1234-123456789abc'

class CloudDoctorTests(unittest.TestCase):
    def client(self,root,send):
        path=Path(root)/'config.json'
        atomic_json(path,dict(url='https://example.supabase.co',publishable_key='sb_publishable_test'))
        atomic_json(path.parent/'auth.json',dict(url='https://example.supabase.co',user_id=UID,access_token='private-token',expires_at=time.time()+3600))
        return SupabaseClient(path,send=send)

    def test_ready_checks_do_not_upload_or_read_evidence_contents(self):
        calls=[]
        def send(method,url,headers,body):
            calls.append((method,url,body))
            return b'true' if url.endswith('ksp_is_tester') else b'[]'
        with tempfile.TemporaryDirectory() as root:
            report=self.client(root,send).doctor()
        self.assertTrue(report['ready'])
        self.assertEqual(len(calls),3)
        self.assertTrue(all('/rpc/ksp_is_tester' in u or '/ksp_sessions?select=id' in u or '/object/list/' in u for _,u,_ in calls))
        self.assertNotIn('private-token',json.dumps(report))
        self.assertNotIn('sb_publishable_test',json.dumps(report))

    def test_missing_authorization_and_missing_schema_are_distinct(self):
        def send(method,url,headers,body):
            if url.endswith('ksp_is_tester'):return b'false'
            if '/ksp_sessions?' in url:raise CloudError('Supabase respondió HTTP 404.')
            return b'[]'
        with tempfile.TemporaryDirectory() as root:report=self.client(root,send).doctor()
        self.assertFalse(report['ready'])
        failed=[x['name'] for x in report['checks'] if not x['ok']]
        self.assertEqual(failed,['tester','sessions'])

    def test_no_auth_does_not_attempt_remote_requests(self):
        with tempfile.TemporaryDirectory() as root:
            def send(*args):self.fail('Remote calls without authentication')
            client=self.client(root,send);client.auth_path.unlink();report=client.doctor()
        self.assertFalse(report['ready'])
        self.assertEqual([x['name'] for x in report['checks']],['authentication'])

    def test_storage_failure_is_reported_without_losing_other_results(self):
        def send(method,url,headers,body):
            if '/object/list/' in url:raise CloudError('Supabase respondió HTTP 403.')
            return b'true' if url.endswith('ksp_is_tester') else b'[]'
        with tempfile.TemporaryDirectory() as root:report=self.client(root,send).doctor()
        self.assertFalse(report['ready'])
        self.assertEqual([x['name'] for x in report['checks'] if not x['ok']],['storage'])

class ProjectPresetTests(unittest.TestCase):
    def test_preset_configures_public_project_without_creating_auth(self):
        import contextlib
        import io
        from unittest.mock import patch
        from integrations.ksp_cloud import main
        with tempfile.TemporaryDirectory() as root:
            config=Path(root)/'config.json'
            with patch('sys.argv',['ksp_cloud.py','--config',str(config),'configure-project']), contextlib.redirect_stdout(io.StringIO()):
                self.assertIsNone(main())
            data=json.loads(config.read_text())
            self.assertEqual(data['url'],'https://crwzshdtvsqukheckxai.supabase.co')
            self.assertTrue(data['publishable_key'].startswith('sb_publishable_'))
            self.assertTrue(data['enabled'])
            self.assertFalse((config.parent/'auth.json').exists())

    def test_invalid_preset_does_not_write_configuration(self):
        import contextlib
        import io
        from unittest.mock import patch
        from integrations.ksp_cloud import main
        with tempfile.TemporaryDirectory() as root:
            config=Path(root)/'config.json';profile=Path(root)/'bad.json'
            profile.write_text('{"schema":"wrong"}')
            with patch('integrations.ksp_cloud.PROJECT_PROFILE',profile), patch('sys.argv',['ksp_cloud.py','--config',str(config),'configure-project']), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):main()
            self.assertFalse(config.exists())
