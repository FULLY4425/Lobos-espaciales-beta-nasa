import tempfile
import unittest
from pathlib import Path
from integrations.ksp_consent import UploadConsent
from integrations.ksp_cloud import CloudUploader,CloudError,atomic_json,read_json
from integrations.ksp_session import SessionRecorder
from test_ksp_cloud import FakeClient,UID

class ConsentTests(unittest.TestCase):
    def make(self,root,consent=None):
        config=Path(root)/'.config/config.json';config.parent.mkdir(exist_ok=True)
        r=SessionRecorder(Path(root)/'sessions');client=FakeClient(config)
        return r,client,CloudUploader(r,client=client,consent=consent)

    def allowed(self,project='https://example.supabase.co',history=False):
        c=UploadConsent(project,include_history=history);c.decide(True);return c

    def test_closed_failed_and_negative_dialogs_deny(self):
        for answer in [False,None,'yes',1]:
            c=UploadConsent('https://example.supabase.co');self.assertFalse(c.request(lambda text:answer));self.assertFalse(c.allowed)
        def unavailable(text):raise RuntimeError('no desktop')
        c=UploadConsent('https://example.supabase.co');self.assertFalse(c.request(unavailable));self.assertEqual(c.reason,'dialog-unavailable')

    def test_permission_is_session_only_and_bound_to_destination(self):
        c=UploadConsent('https://example.supabase.co');text=[]
        self.assertTrue(c.request(lambda message:text.append(message) or True))
        self.assertIn('únicamente en tu PC',text[0]);self.assertIn(c.project,text[0]);self.assertIn('usuario autorizado',text[0])
        self.assertTrue(c.permits(c.project));self.assertFalse(c.permits('https://other.supabase.co'))
        self.assertFalse(UploadConsent(c.project).allowed)

    def test_no_permission_blocks_auth_network_and_automatic_queue(self):
        with tempfile.TemporaryDirectory() as root:
            r,client,u=self.make(root)
            def never():self.fail('Authentication must not run before consent')
            client.auth=never;u.sync_once();u.sync_once(final=True);u.close()
            self.assertFalse(client.uploads);self.assertFalse((r.path/'.cloud-upload.json').exists())
            with self.assertRaises(CloudError):u.control('resume')
            with self.assertRaises(CloudError):u.control('retry')
            with self.assertRaises(CloudError):u.sync_folder(r.path,dict(user_id=UID))

    def test_other_destination_permission_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as root:
            _,client,u=self.make(root,self.allowed('https://other.supabase.co'));u.sync_once();self.assertFalse(client.uploads)

    def test_revocation_blocks_index_after_an_inflight_upload_and_final_sync(self):
        with tempfile.TemporaryDirectory() as root:
            r,client,u=self.make(root,self.allowed());original=client.upload
            def upload(*args):original(*args);u.revoke()
            client.upload=upload
            with self.assertRaises(CloudError):u.sync_once()
            self.assertTrue((r.path/'.cloud-revoked').exists());self.assertFalse(client.rows)
            count=len(client.uploads);u.sync_once(final=True);self.assertEqual(len(client.uploads),count)
            with self.assertRaises(CloudError):u.control('resume')

    def test_revoked_session_is_not_retried_with_a_new_permission(self):
        with tempfile.TemporaryDirectory() as root:
            r,client,u=self.make(root,self.allowed());u.sync_once();u.revoke();r.event('after-revoke',{})
            count=len(client.uploads);other=CloudUploader(r,client=client,consent=self.allowed());other.sync_once()
            self.assertEqual(len(client.uploads),count)

    def test_legacy_queue_requires_explicit_history_scope(self):
        with tempfile.TemporaryDirectory() as root:
            r,client,u=self.make(root,self.allowed());u.sync_once()
            marker=r.path/'.cloud-upload.json';state=read_json(marker);state.pop('consentVersion');atomic_json(marker,state);r.event('new-data',{})
            new=SessionRecorder(r.path.parent);fresh=CloudUploader(new,client=client,consent=self.allowed())
            count=len(client.uploads);self.assertFalse(fresh.sync_folder(r.path,dict(user_id=UID)));self.assertEqual(len(client.uploads),count)

    def test_history_flag_cannot_expand_the_scope_without_dialog_consent(self):
        with tempfile.TemporaryDirectory() as root:
            r,client,_=self.make(root);u=CloudUploader(r,client=client,include_history=True,consent=self.allowed())
            self.assertFalse(u.include_history)
