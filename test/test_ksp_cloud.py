from integrations.ksp_consent import UploadConsent
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from integrations.ksp_cloud import SupabaseClient, CloudUploader, CloudError, validate_config, atomic_json, WorkerLock
from integrations.ksp_session import SessionRecorder, MAX_EXTERNAL_LOG

UID='12345678-1234-1234-1234-123456789abc'


def approved_consent(client):
    consent=UploadConsent(client.config['url']);consent.decide(True,'test-fixture');return consent


class FakeClient:
    def __init__(self,path):
        self.path=Path(path);self.config=validate_config(dict(url='https://example.supabase.co',publishable_key='sb_publishable_test'))
        self.objects={};self.rows={};self.uploads=[];self.fail_upload=False;self.fail_index=False
    def auth(self):return dict(user_id=UID,access_token='private-user-token')
    def upload(self,path,data,auth):
        self.uploads.append((path,data))
        if self.fail_upload:raise CloudError('offline')
        self.objects[path]=data
    def index(self,data,auth):
        if self.fail_index:raise CloudError('index offline')
        self.rows[data['id']]=data
    def delete(self,paths,auth):
        for path in paths:self.objects.pop(path,None)


class CloudEvidenceTests(unittest.TestCase):
    def make(self,root):
        config=Path(root)/'.config/config.json';config.parent.mkdir()
        recorder=SessionRecorder(Path(root)/'sessions')
        client=FakeClient(config);uploader=CloudUploader(recorder,client=client,consent=approved_consent(client))
        return recorder,client,uploader

    def test_configuration_rejects_insecure_urls_and_privileged_keys(self):
        for url in ['http://x.supabase.co','https://user:pass@x.supabase.co','https://x.supabase.co/path','https://x.supabase.co?secret=yes']:
            with self.assertRaises(CloudError):validate_config(dict(url=url,publishable_key='sb_publishable_test'))
        with self.assertRaises(CloudError):validate_config(dict(url='https://x.supabase.co',publishable_key='sb_secret_admin'))
        with self.assertRaises(CloudError):validate_config(dict(url='https://x.supabase.co',publishable_key='sb_publishable_test',interval_seconds=0))

    def test_retry_after_network_failure_uses_same_durable_zip_and_retains_local_files(self):
        with tempfile.TemporaryDirectory() as root:
            recorder,client,uploader=self.make(root);recorder.sample(dict(body='Duna',speed=2))
            client.fail_upload=True
            with self.assertRaises(CloudError):uploader.sync_once()
            state=json.loads((recorder.path/'.cloud-upload.json').read_text());pending=state['pending']
            self.assertTrue((recorder.path/'.cloud-pending.zip').exists())
            recorder.event('new-data',dict(text='After failed upload'))
            client.fail_upload=False
            restarted=CloudUploader(recorder,client=client,consent=approved_consent(client));restarted.sync_once()
            self.assertEqual(client.uploads[0],client.uploads[1])
            self.assertEqual(client.rows[recorder.id]['archive_path'],pending['object_path'])
            restarted.sync_once()
            self.assertEqual(len(client.rows),1);self.assertEqual(len(client.objects),1)
            self.assertTrue((recorder.path/'events.jsonl').exists())

    def test_index_failure_preserves_pending_archive_until_acknowledged(self):
        with tempfile.TemporaryDirectory() as root:
            recorder,client,uploader=self.make(root);client.fail_index=True
            with self.assertRaises(CloudError):uploader.sync_once()
            self.assertEqual(len(client.rows),0)
            self.assertIsNotNone(json.loads((recorder.path/'.cloud-upload.json').read_text())['pending'])
            client.fail_index=False;uploader.sync_once()
            self.assertIsNone(json.loads((recorder.path/'.cloud-upload.json').read_text())['pending'])
            self.assertEqual(len(client.rows),1)

    def test_pause_persists_and_same_snapshot_does_not_upload_twice(self):
        with tempfile.TemporaryDirectory() as root:
            recorder,client,uploader=self.make(root);uploader.control('pause');uploader.sync_once();self.assertFalse(client.uploads)
            restarted=CloudUploader(recorder,client=client,consent=approved_consent(client));self.assertTrue(restarted.paused)
            restarted.control('resume');restarted.sync_once();count=len(client.uploads)
            restarted.sync_once();self.assertEqual(len(client.uploads),count)

    def test_queue_survives_connector_restart_and_ignores_unrequested_history(self):
        with tempfile.TemporaryDirectory() as root:
            recorder,client,uploader=self.make(root);client.fail_upload=True
            with self.assertRaises(CloudError):uploader.sync_once()
            other=SessionRecorder(recorder.path.parent);self.assertNotEqual(other.id,recorder.id)
            unrelated=SessionRecorder(recorder.path.parent)
            client.fail_upload=False;CloudUploader(other,client=client,consent=approved_consent(client)).sync_once()
            self.assertIn(recorder.id,client.rows);self.assertIn(other.id,client.rows);self.assertNotIn(unrelated.id,client.rows)

    def test_private_files_and_symlinks_are_not_added_to_evidence_zip(self):
        with tempfile.TemporaryDirectory() as root:
            recorder,_,_=self.make(root)
            (recorder.path/'auth.json').write_text('DO NOT UPLOAD')
            (recorder.path/'.cloud-upload.json').write_text('DO NOT UPLOAD')
            secret=Path(root)/'secret';secret.write_text('DO NOT UPLOAD')
            try:(recorder.path/'connector.log').symlink_to(secret)
            except (OSError,NotImplementedError):pass
            z=zipfile.ZipFile(io.BytesIO(recorder.export()))
            self.assertNotIn('auth.json',z.namelist());self.assertNotIn('.cloud-upload.json',z.namelist());self.assertNotIn('connector.log',z.namelist())

    def test_other_account_cannot_claim_previously_queued_session(self):
        with tempfile.TemporaryDirectory() as root:
            recorder,client,uploader=self.make(root);uploader.sync_once();before=len(client.uploads)
            recorder.event('later',{})
            uploader.sync_folder(recorder.path,dict(user_id='aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'))
            self.assertEqual(before,len(client.uploads))

    def test_auth_uses_user_login_refresh_and_never_a_service_key(self):
        with tempfile.TemporaryDirectory() as root:
            config=Path(root)/'config.json';atomic_json(config,dict(url='https://example.supabase.co',publishable_key='sb_publishable_test'))
            calls=[]
            def send(method,url,headers,body):
                calls.append((method,url,headers,json.loads(body)))
                return json.dumps(dict(user=dict(id=UID),access_token='user-access-token',refresh_token='refresh-only-local',expires_in=3600)).encode()
            client=SupabaseClient(config,send=send);client.login('tester@example.org','PASSWORD')
            auth=json.loads(client.auth_path.read_text());auth['expires_at']=0;atomic_json(client.auth_path,auth)
            client.auth();self.assertIn('refresh_token',calls[1][3]);self.assertNotIn('PASSWORD',client.path.read_text());self.assertEqual(calls[0][2]['apikey'],'sb_publishable_test')
            if __import__('os').name!='nt':self.assertEqual(client.auth_path.stat().st_mode&0o777,0o600)

    def test_external_logs_are_explicit_and_truncation_is_reported_without_source_path(self):
        with tempfile.TemporaryDirectory() as root:
            source=Path(root)/'private-installation/KSP.log';source.parent.mkdir();source.write_bytes(b'a'*(MAX_EXTERNAL_LOG+10))
            recorder=SessionRecorder(Path(root)/'sessions',external_logs={'KSP.log':source})
            z=zipfile.ZipFile(io.BytesIO(recorder.export()));manifest=json.loads(z.read('session.json'))
            self.assertEqual(len(z.read('KSP.log')),MAX_EXTERNAL_LOG);self.assertTrue(manifest['externalLogs']['KSP.log']['truncated']);self.assertNotIn('private-installation',z.read('session.json').decode())
            source.unlink();cached=zipfile.ZipFile(io.BytesIO(recorder.export()));meta=json.loads(cached.read('session.json'))
            self.assertTrue(meta['externalLogs']['KSP.log']['cached']);self.assertFalse(meta['externalLogs']['KSP.log']['available']);self.assertEqual(len(cached.read('KSP.log')),MAX_EXTERNAL_LOG)

    def test_single_worker_lock_prevents_overlapping_uploaders(self):
        with tempfile.TemporaryDirectory() as root:
            a=WorkerLock(Path(root)/'lock')
            try:
                with self.assertRaises(CloudError):WorkerLock(Path(root)/'lock')
            finally:a.close()
            WorkerLock(Path(root)/'lock').close()
