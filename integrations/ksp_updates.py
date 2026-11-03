"""Official GitHub update checks. Installation is an explicit, stopped-connector CLI action."""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPOSITORY='https://github.com/FULLY4425/Lobos-espaciales-beta-nasa'
GUIDE=REPOSITORY+'/blob/main/docs/KSP_ACTUALIZAR.md'
STATE=ROOT/'.ksp-updates'

class UpdateError(Exception):pass

def version_tuple(value):
    if not isinstance(value,str) or not re.fullmatch(r'\d{1,4}\.\d{1,4}\.\d{1,4}',value):raise UpdateError('Version no valida.')
    return tuple(map(int,value.split('.')))

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None

def read_remote(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Lobos-KSP-Update-Check','Accept':'application/json'})
    try:
        with urllib.request.build_opener(NoRedirect()).open(req,timeout=8) as response:
            data=response.read(65537)
            if len(data)>65536:raise UpdateError('Respuesta de actualizacion demasiado grande.')
        return json.loads(data)
    except (OSError,ValueError):raise UpdateError('No se pudo comprobar GitHub. Tu version sigue funcionando.') from None

def latest_release(fetch=read_remote):
    commit=fetch('https://api.github.com/repos/FULLY4425/Lobos-espaciales-beta-nasa/git/ref/heads/main')
    obj=commit.get('object') if isinstance(commit,dict) else None
    sha=obj.get('sha') if isinstance(obj,dict) else None
    if not isinstance(sha,str) or not re.fullmatch('[a-f0-9]{40}',sha):raise UpdateError('GitHub no devolvio una revision valida.')
    package=fetch('https://raw.githubusercontent.com/FULLY4425/Lobos-espaciales-beta-nasa/'+sha+'/package.json')
    version=package.get('version') if isinstance(package,dict) else None
    version_tuple(version)
    return dict(version=version,commit=sha,guide=GUIDE)

class InstallLock:
    def __init__(self,root=ROOT):
        path=Path(root)/'.ksp-updates';path.mkdir(exist_ok=True)
        self.file=(path/'runtime.lock').open('a+b');self.file.seek(0);self.file.write(b'0');self.file.flush();self.file.seek(0)
        try:
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(self.file.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(self.file.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError:self.file.close();raise UpdateError('Cierra el conector y otros actualizadores de esta carpeta antes de continuar.') from None
    def close(self):self.file.close()

class UpdateChecker:
    def __init__(self,current,fetch=read_remote):
        self.current=current;self.fetch=fetch;self.lock=threading.Lock();self.stop=threading.Event();self.thread=None
        self.value=dict(current=current,status='pending',available=False,guide=GUIDE)
    def status(self):
        with self.lock:return dict(self.value)
    def check(self):
        try:
            latest=latest_release(self.fetch)
            result=dict(current=self.current,latest=latest['version'],commit=latest['commit'],available=version_tuple(latest['version'])>version_tuple(self.current),status='checked',checkedAt=time.time(),guide=GUIDE)
        except UpdateError as error:
            result=self.status();result.update(status='offline',error=str(error))
        with self.lock:self.value=result
        return result
    def start(self,notify=False):
        def run():
            first=True
            while not self.stop.is_set():
                state=self.check()
                if first and notify and state.get('available') and os.name=='nt':
                    # Native informational prompt only. Never installs or runs downloaded code.
                    import ctypes,webbrowser
                    text='Hay una nueva version: '+state['latest']+' (actual '+self.current+').\n\nPuedes seguir usando esta version. Para actualizar, cierra el conector y ejecuta actualizar-ksp.cmd.\n\n¿Abrir las instrucciones?'
                    if ctypes.windll.user32.MessageBoxW(None,text,'Lobos Espaciales · Actualizacion disponible',0x24)==6:webbrowser.open(GUIDE)
                first=False
                self.stop.wait(3600)
        self.thread=threading.Thread(target=run,name='ksp-update-check',daemon=True);self.thread.start()
    def close(self):self.stop.set()


def apply_update(root=ROOT,release=None,run=None):
    """Never resets/cleans/stashes, installs dependencies, or runs repository hooks."""
    root=Path(root);guard=InstallLock(root)
    try:
        with tempfile.TemporaryDirectory(prefix='lobos-git-hooks-') as hooks:
            def git(*args):
                if run:return run(*args)
                try:
                    result=subprocess.run(['git','-c','core.hooksPath='+hooks,'-c','core.fsmonitor=false','-c','submodule.recurse=false','-c','credential.helper=',*args],cwd=root,text=True,capture_output=True,timeout=120,env=dict(os.environ,GIT_TERMINAL_PROMPT='0'))
                except (OSError,subprocess.TimeoutExpired):raise UpdateError('Git no esta disponible o se agoto el tiempo. No se fuerza la actualizacion.') from None
                if result.returncode:raise UpdateError('Git no pudo continuar. No se borran cambios; revisa conexion, rama o conflictos desde tu terminal.')
                return result.stdout.strip()
            if Path(git('rev-parse','--show-toplevel')).resolve()!=root.resolve():raise UpdateError('Usa la carpeta raiz del repositorio clonado con Git.')
            remote=git('remote','get-url','origin').rstrip('/')
            if remote not in (REPOSITORY,REPOSITORY+'.git'):raise UpdateError('El remoto origin no es el repositorio oficial HTTPS. Actualiza tu copia manualmente.')
            if git('status','--porcelain','--untracked-files=normal'):raise UpdateError('Hay cambios locales o archivos sin registrar. Guardalos en Git o copia tus cambios antes de actualizar.')
            if not git('symbolic-ref','--quiet','--short','HEAD'):raise UpdateError('HEAD separado: elige tu rama antes de actualizar.')
            latest=release or latest_release();sha=latest.get('commit','');wanted=latest.get('version');version_tuple(wanted)
            if not re.fullmatch('[a-f0-9]{40}',sha):raise UpdateError('Revision no valida.')
            current=json.loads((root/'package.json').read_text())['version']
            if version_tuple(wanted)<=version_tuple(current):return dict(updated=False,version=current)
            git('fetch','--no-tags','--no-recurse-submodules',REPOSITORY+'.git',sha)
            fetched=json.loads(git('show',sha+':package.json'))
            if fetched.get('version')!=wanted:raise UpdateError('La version obtenida no coincide con el aviso; no se aplica.')
            git('merge-base','--is-ancestor','HEAD',sha)
            git('merge','--ff-only','--no-edit',sha)
            return dict(updated=True,version=wanted)
    finally:guard.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['check','update'],nargs='?',default='check');args=parser.parse_args()
    try:
        if args.action=='check':print(json.dumps(UpdateChecker(json.loads((ROOT/'package.json').read_text())['version']).check(),ensure_ascii=False,indent=2))
        else:
            answer=input('Cierra el conector. ¿Actualizar desde GitHub sin borrar cambios locales? Escribe ACTUALIZAR: ')
            if answer.strip()!='ACTUALIZAR':sys.exit('Actualizacion cancelada.')
            print(json.dumps(apply_update(),ensure_ascii=False));print('Reinicia el conector. Si cambiaron las dependencias, revisa requirements-ksp.txt. El mod DLL se recompila por separado.')
    except (UpdateError,ValueError,KeyError) as error:sys.exit(str(error))
