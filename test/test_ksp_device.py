import json
import tempfile
import time
import unittest
from pathlib import Path
from integrations.ksp_cloud import SupabaseClient,CloudError,atomic_json
from integrations.ksp_consent import UploadConsent
UID='12345678-1234-1234-1234-123456789abc'
class DeviceClientTests(unittest.TestCase):
    def make(self,root,send):
        path=Path(root)/'config.json';atomic_json(path,dict(url='https://example.supabase.co',publishable_key='sb_publishable_test',device_registration=True))
        return SupabaseClient(path,send=send)
    def consent(self):
        c=UploadConsent('https://example.supabase.co',automatic_registration=True);c.decide(True);return c
    def response(self):return dict(user=dict(id=UID,app_metadata=dict(ksp_device=True)),access_token='device-token',refresh_token='device-refresh',expires_in=3600)
    def test_no_consent_does_not_create_device_or_call_network(self):
        with tempfile.TemporaryDirectory() as root:
            def never(*args):self.fail('Network without permission')
            c=self.make(root,never)
            with self.assertRaises(CloudError):c.ensure_device_auth(None)
            self.assertFalse((Path(root)/'device.json').exists())
    def test_new_installation_enrolls_without_email_password_and_reuses_tokens(self):
        calls=[]
        def send(method,url,headers,body):calls.append((url,json.loads(body)));return json.dumps(self.response()).encode()
        with tempfile.TemporaryDirectory() as root:
            c=self.make(root,send);c.ensure_device_auth(self.consent());c.ensure_device_auth(self.consent());a=c.auth()
            self.assertEqual(a['mode'],'device');self.assertEqual(len(calls),1)
            self.assertNotIn('email',calls[0][1]);self.assertNotIn('password',calls[0][1]);self.assertEqual(len(calls[0][1]['device_secret']),64)
            self.assertTrue((Path(root)/'device.json').exists())
            if __import__('os').name!='nt':self.assertEqual((Path(root)/'device.json').stat().st_mode&0o777,0o600)
    def test_revocation_during_enrollment_does_not_save_tokens(self):
        consent=self.consent()
        def send(*args):consent.decide(False,'revoked');return json.dumps(self.response()).encode()
        with tempfile.TemporaryDirectory() as root:
            c=self.make(root,send)
            with self.assertRaises(CloudError):c.ensure_device_auth(consent)
            self.assertFalse(c.auth_path.exists())
    def test_device_uses_gateway_instead_of_direct_storage_or_index(self):
        calls=[]
        def send(method,url,headers,body):calls.append(url);return b'{}'
        with tempfile.TemporaryDirectory() as root:
            c=self.make(root,send);a=dict(mode='device',access_token='device-token');c.upload('own/path.zip',b'ZIP',a);c.index({},a);c.delete(['own/path.zip'],a)
        self.assertTrue(all('/functions/v1/ksp-device/' in url for url in calls));self.assertEqual(len(calls),3)
    def test_existing_manual_account_is_preserved(self):
        def never(*args):self.fail('Existing account must not be replaced')
        with tempfile.TemporaryDirectory() as root:
            c=self.make(root,never);atomic_json(c.auth_path,dict(url=c.config['url'],user_id=UID,access_token='manual-token',expires_at=time.time()+3600));c.ensure_device_auth(self.consent());self.assertEqual(c.auth()['access_token'],'manual-token')
    def test_device_role_requires_server_app_metadata(self):
        value=self.response();value['user']=dict(id=UID,user_metadata=dict(ksp_device=True))
        with tempfile.TemporaryDirectory() as root:
            c=self.make(root,lambda *args:json.dumps(value).encode())
            with self.assertRaises(CloudError):c.ensure_device_auth(self.consent())
            self.assertFalse(c.auth_path.exists())
    def test_logout_pause_blocks_automatic_registration(self):
        def never(*args):self.fail('Logout cannot silently re-register')
        with tempfile.TemporaryDirectory() as root:
            c=self.make(root,never);atomic_json(c.automatic_pause_path,dict(paused=True))
            with self.assertRaises(CloudError):c.ensure_device_auth(self.consent())
