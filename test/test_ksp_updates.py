import json,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock
from integrations.ksp_updates import UpdateChecker,UpdateError,latest_release,version_tuple,apply_update,InstallLock,REPOSITORY

SHA='a'*40

def release_fetch(url):return dict(object=dict(sha=SHA)) if '/git/ref/' in url else dict(version='1.7.9')

class UpdateTests(unittest.TestCase):
    def test_version_comparison_is_numeric_and_pins_commit(self):
        self.assertGreater(version_tuple('1.7.10'),version_tuple('1.7.9'))
        fetch=Mock(side_effect=release_fetch);latest=latest_release(fetch)
        self.assertEqual(latest['commit'],SHA);self.assertIn('/'+SHA+'/package.json',fetch.call_args.args[0])
        self.assertTrue(UpdateChecker('1.7.8',fetch).check()['available'])
        self.assertFalse(UpdateChecker('1.7.9',fetch).check()['available'])
        for value in ['latest','1.2','1.2.3;cmd',None]:
            with self.assertRaises(UpdateError):version_tuple(value)

    def test_offline_is_nonfatal_and_forged_revision_rejected(self):
        checker=UpdateChecker('1.7.8',Mock(side_effect=UpdateError('offline')))
        self.assertEqual(checker.check()['status'],'offline')
        with self.assertRaises(UpdateError):latest_release(lambda url:dict(object=dict(sha='--unsafe')))

    def make(self,root,dirty='',remote=REPOSITORY+'.git'):
        (Path(root)/'package.json').write_text(json.dumps(dict(version='1.7.8')))
        calls=[]
        def git(*args):
            calls.append(args)
            if args[:2]==('rev-parse','--show-toplevel'):return str(Path(root).resolve())
            if args[:2]==('remote','get-url'):return remote
            if args[0]=='status':return dirty
            if args[0]=='symbolic-ref':return 'main'
            if args[0]=='show':return json.dumps(dict(version='1.7.9'))
            return ''
        return git,calls

    def test_dirty_or_foreign_repository_never_fetches_or_merges(self):
        for dirty,remote in [(' M file',REPOSITORY),('', 'https://attacker.example/repo')]:
            with tempfile.TemporaryDirectory() as root:
                git,calls=self.make(root,dirty,remote)
                with self.assertRaises(UpdateError):apply_update(root,dict(commit=SHA,version='1.7.9'),git)
                self.assertFalse(any(c[0] in ('fetch','merge') for c in calls))

    def test_update_is_explicit_fast_forward_of_verified_version(self):
        with tempfile.TemporaryDirectory() as root:
            git,calls=self.make(root)
            result=apply_update(root,dict(commit=SHA,version='1.7.9'),git)
            self.assertTrue(result['updated'])
            self.assertIn(('merge-base','--is-ancestor','HEAD',SHA),calls)
            self.assertIn(('merge','--ff-only','--no-edit',SHA),calls)
            self.assertFalse(any(c[0] in ('reset','clean','stash') for c in calls))

    def test_connector_lock_prevents_update(self):
        with tempfile.TemporaryDirectory() as root:
            guard=InstallLock(root)
            try:
                with self.assertRaises(UpdateError):InstallLock(root)
            finally:guard.close()
            InstallLock(root).close()

    def test_mismatched_package_version_never_merges(self):
        with tempfile.TemporaryDirectory() as root:
            git,calls=self.make(root)
            def wrong(*args):
                result=git(*args)
                return json.dumps(dict(version='9.9.9')) if args[0]=='show' else result
            with self.assertRaises(UpdateError):apply_update(root,dict(commit=SHA,version='1.7.9'),wrong)
            self.assertFalse(any(c[0]=='merge' for c in calls))
