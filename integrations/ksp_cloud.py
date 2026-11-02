"""Private Supabase evidence uploads. No service-role keys; no game control RPCs."""
import argparse
import base64
import getpass
import hashlib
import json
import os
import re
import threading
import time
import uuid
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_CONFIG=Path('.ksp-cloud/config.json')
MAX_ARCHIVE=50*1024*1024
SESSION_ID=re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z-[a-f0-9]{12}$')


class CloudError(Exception):
    pass


def atomic_json(path, data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name(path.name+'.tmp-'+uuid.uuid4().hex)
    fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
    with os.fdopen(fd,'w',encoding='utf-8') as file:
        json.dump(data,file,ensure_ascii=False,allow_nan=False);file.flush();os.fsync(file.fileno())
    os.replace(temporary,path)
    if os.name!='nt':os.chmod(path,0o600)


def read_json(path):
    try:
        value=json.loads(Path(path).read_text(encoding='utf-8'))
        if not isinstance(value,dict):raise ValueError()
        return value
    except (OSError,ValueError):raise CloudError('No se pudo leer un archivo de configuración/estado local.') from None


def validate_config(data):
    if not isinstance(data,dict):raise CloudError('Configuración no válida.')
    url=str(data.get('url','')).strip().rstrip('/');p=urllib.parse.urlsplit(url)
    if p.scheme!='https' or not p.hostname or p.username or p.password or p.path or p.query or p.fragment:
        raise CloudError('Configura la URL HTTPS base de tu proyecto Supabase, sin rutas ni credenciales.')
    key=data.get('publishable_key','')
    if not isinstance(key,str) or not key or any(c.isspace() for c in key):raise CloudError('Falta la clave pública publishable/anon.')
    if key.startswith('sb_secret_'):raise CloudError('No uses claves secretas ni service_role en el conector.')
    if not key.startswith('sb_publishable_'):
        try:
            claims=json.loads(base64.urlsafe_b64decode(key.split('.')[1]+'==='))
            if claims.get('role')!='anon':raise ValueError()
        except (ValueError,IndexError,TypeError):raise CloudError('Usa una clave publishable o la clave anon pública; nunca service_role.') from None
    interval=data.get('interval_seconds',300)
    if isinstance(interval,bool) or not isinstance(interval,(int,float)) or not 30<=interval<=3600:raise CloudError('El intervalo debe ser de 30 a 3600 segundos.')
    return dict(url=url,publishable_key=key,interval_seconds=interval,enabled=data.get('enabled',True) is True)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None


def transport(method,url,headers,body):
    request=urllib.request.Request(url,data=body,headers=headers,method=method)
    try:
        with urllib.request.build_opener(NoRedirect()).open(request,timeout=10) as response:return response.read()
    except urllib.error.HTTPError as error:
        # Response bodies may contain account information. Never log them or tokens.
        raise CloudError(f'Supabase respondió HTTP {error.code}. Revisa conexión, sesión y permisos del proyecto.') from None
    except (urllib.error.URLError,TimeoutError,OSError):raise CloudError('No se pudo contactar con Supabase. Se conserva la copia local para reintentar.') from None


class SupabaseClient:
    def __init__(self, config_path=DEFAULT_CONFIG, send=transport):
        self.path=Path(config_path);self.config=validate_config(read_json(self.path));self.auth_path=self.path.parent/'auth.json';self.send=send

    def _call(self,method,path,data=None,token=None,content_type='application/json',extra=None):
        headers={'apikey':self.config['publishable_key'],'Content-Type':content_type}
        if token:headers['Authorization']='Bearer '+token
        headers.update(extra or {})
        body=data if isinstance(data,bytes) else json.dumps(data).encode() if data is not None else None
        return self.send(method,self.config['url']+path,headers,body)

    def save_auth(self,response):
        if not isinstance(response,dict) or not isinstance(response.get('user'),dict):raise CloudError('Respuesta de autenticación no válida.')
        user_id=response.get('user',{}).get('id','')
        if not re.fullmatch(r'[0-9a-fA-F-]{36}',user_id) or not response.get('access_token') or not response.get('refresh_token'):raise CloudError('Respuesta de autenticación no válida.')
        auth=dict(url=self.config['url'],user_id=user_id,access_token=response['access_token'],refresh_token=response['refresh_token'],expires_at=time.time()+response.get('expires_in',3600))
        atomic_json(self.auth_path,auth)
        return auth

    def login(self,email,password):
        raw=self._call('POST','/auth/v1/token?grant_type=password',dict(email=email,password=password))
        try:return self.save_auth(json.loads(raw))
        except (ValueError,TypeError,KeyError):raise CloudError('No se pudo interpretar la respuesta de autenticación.') from None

    def auth(self):
        if not self.auth_path.exists():raise CloudError('Inicia sesión con: python integrations/ksp_cloud.py login')
        auth=read_json(self.auth_path)
        if auth.get('url')!=self.config['url']:raise CloudError('La sesión pertenece a otro proyecto. Vuelve a iniciar sesión.')
        if not re.fullmatch(r'[0-9a-fA-F-]{36}',str(auth.get('user_id',''))):raise CloudError('Identidad local no válida. Vuelve a iniciar sesión.')
        if auth.get('expires_at',0)<time.time()+60:
            raw=self._call('POST','/auth/v1/token?grant_type=refresh_token',dict(refresh_token=auth.get('refresh_token')))
            try:auth=self.save_auth(json.loads(raw))
            except (ValueError,TypeError,KeyError):raise CloudError('No se pudo renovar la sesión. Vuelve a iniciar sesión.') from None
        return auth

    def doctor(self):
        """Check current user's setup without uploading or reading evidence bodies."""
        report=dict(project=self.config['url'],ready=False,checks=[])
        try:
            auth=self.auth()
            report['checks'].append(dict(name='authentication',ok=True))
        except CloudError as error:
            report['checks'].append(dict(name='authentication',ok=False,message=str(error)))
            return report
        checks=[
            ('tester', 'POST', '/rest/v1/rpc/ksp_is_tester', {}, 'Autoriza este usuario en public.ksp_testers antes de enviar evidencias.'),
            ('sessions', 'GET', '/rest/v1/ksp_sessions?select=id,user_id,app_version,archive_path,sha256,archive_bytes,captured_at,started_at,telemetry_samples&limit=0&user_id=eq.'+auth['user_id'], None, 'Aplica supabase/ksp_evidence.sql y revisa los permisos de ksp_sessions.'),
            ('storage', 'POST', '/storage/v1/object/list/ksp-evidence', dict(prefix=auth['user_id']+'/',limit=1,offset=0), 'Crea el bucket privado ksp-evidence y aplica sus políticas de acceso.'),
        ]
        for name,method,path,payload,hint in checks:
            try:
                value=json.loads(self._call(method,path,payload,auth['access_token']))
                if (name=='tester' and value is not True) or (name!='tester' and not isinstance(value,list)):
                    raise CloudError(hint)
                report['checks'].append(dict(name=name,ok=True))
            except (CloudError,ValueError,TypeError) as error:
                message=str(error) if isinstance(error,CloudError) else 'Respuesta de diagnóstico no válida.'
                report['checks'].append(dict(name=name,ok=False,message=message,hint=hint))
        report['ready']=all(check['ok'] for check in report['checks'])
        report['notice']='Lectura verificada; no se subieron archivos. Las políticas de escritura, privacidad y aislamiento requieren una prueba real independiente.'
        return report

    def upload(self,path,content,auth):
        self._call('POST','/storage/v1/object/ksp-evidence/'+path,content,auth['access_token'],'application/zip',{'x-upsert':'true'})

    def index(self,data,auth):
        self._call('POST','/rest/v1/ksp_sessions?on_conflict=id',data,auth['access_token'],extra={'Prefer':'resolution=merge-duplicates,return=minimal'})

    def delete(self,paths,auth):
        if paths:self._call('DELETE','/storage/v1/object/ksp-evidence',dict(prefixes=paths),auth['access_token'])


class WorkerLock:
    """One uploader per configuration; prevents refresh-token and queue races."""
    def __init__(self,path):
        self.file=open(path,'a+b');self.file.seek(0);self.file.write(b'0');self.file.flush();self.file.seek(0)
        try:
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(self.file.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(self.file.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError:self.file.close();raise CloudError('Otra instancia ya está enviando evidencias con esta configuración.') from None

    def close(self):self.file.close()


def utc_now():return datetime.now(timezone.utc).isoformat()


class CloudUploader:
    def __init__(self,recorder,config_path=DEFAULT_CONFIG,client=None,include_history=False):
        self.recorder=recorder;self.client=client or SupabaseClient(config_path);self.root=recorder.path.parent;self.include_history=include_history
        self.control_path=self.client.path.parent/'upload-control.json'
        self.paused=read_json(self.control_path).get('paused',False) if self.control_path.exists() else False
        self.state=dict(configured=True,paused=self.paused,status='queued',lastSuccess=None,error=None,nextRetry=None)
        self.lock=threading.Lock();self.stop_event=threading.Event();self.wake=threading.Event();self.thread=None;self.failures=0;self.worker_lock=None
        marker=self.recorder.path/'.cloud-upload.json'
        if self.client.config['enabled'] and not marker.exists():
            owner=None
            try:
                auth=read_json(self.client.path.parent/'auth.json')
                if auth.get('url')==self.client.config['url']:owner=auth.get('user_id')
            except CloudError:pass
            atomic_json(marker,dict(user_id=owner,project=self.client.config['url']))

    def status(self):
        with self.lock:return dict(self.state,paused=self.paused,intervalSeconds=self.client.config['interval_seconds'])

    def set_status(self,**kwargs):
        with self.lock:self.state.update(kwargs)

    def control(self,action):
        if action not in ('pause','resume','retry'):raise ValueError('Acción de subida no válida.')
        if action in ('pause','resume'):
            self.paused=action=='pause';atomic_json(self.control_path,dict(paused=self.paused))
        if action=='retry':self.failures=0
        if action in ('resume','retry') and not self.paused:self.set_status(status='queued')
        self.wake.set();return self.status()

    def _fingerprint(self,path):
        from integrations.ksp_session import evidence_files
        data=[(p.name,p.stat().st_size,p.stat().st_mtime_ns) for p in evidence_files(path)]
        if path==self.recorder.path:
            for name,p in self.recorder.external_logs.items():
                try:data.append((name,p.stat().st_size,p.stat().st_mtime_ns))
                except OSError:data.append((name,'unavailable'))
        return hashlib.sha256(json.dumps(data).encode()).hexdigest()

    def sync_folder(self,path,auth):
        from integrations.ksp_session import archive_folder
        if not SESSION_ID.fullmatch(path.name) or path.is_symlink():raise CloudError('Carpeta de sesión no válida.')
        state_path=path/'.cloud-upload.json';pending_path=path/'.cloud-pending.zip'
        state=read_json(state_path) if state_path.exists() else dict(user_id=auth['user_id'],project=self.client.config['url'])
        if state.get('project')!=self.client.config['url']:return False
        if state.get('user_id') is None:
            state['user_id']=auth['user_id'];atomic_json(state_path,state)
        if state.get('user_id')!=auth['user_id']:return False
        fingerprint=self._fingerprint(path)
        pending=state.get('pending')
        if not pending and state.get('fingerprint')!=fingerprint:
            content=self.recorder.export() if path==self.recorder.path else archive_folder(path)
            if len(content)>MAX_ARCHIVE:raise CloudError('El ZIP supera 50 MB. Conservado localmente; reduce el volumen o adjunta los logs grandes por separado.')
            sha=hashlib.sha256(content).hexdigest();object_path=f"{auth['user_id']}/{path.name}/{sha}.zip"
            # Atomic state + a durable local ZIP lets retries send the exact same snapshot.
            temp=pending_path.with_suffix('.tmp');temp.write_bytes(content);os.replace(temp,pending_path)
            pending=dict(fingerprint=fingerprint,sha256=sha,object_path=object_path,bytes=len(content),captured_at=utc_now())
            state['pending']=pending;atomic_json(state_path,state)
        if pending:
            expected=f"{auth['user_id']}/{path.name}/{pending.get('sha256')}.zip"
            if pending.get('object_path')!=expected or not re.fullmatch(r'[a-f0-9]{64}',str(pending.get('sha256',''))):raise CloudError('Estado de envío no válido; la copia local se conserva.')
            try:content=pending_path.read_bytes()
            except OSError:raise CloudError('Falta el ZIP pendiente; revisa la carpeta de evidencias local.') from None
            if hashlib.sha256(content).hexdigest()!=pending['sha256']:raise CloudError('El ZIP pendiente cambió; no se enviará un archivo distinto al registrado.')
            self.set_status(status='uploading',sessionId=path.name)
            row=dict(id=path.name,user_id=auth['user_id'],archive_path=expected,sha256=pending['sha256'],archive_bytes=len(content),captured_at=pending['captured_at'],app_version='unknown')
            import zipfile,io
            try:manifest=json.loads(zipfile.ZipFile(io.BytesIO(content)).read('session.json'))
            except (ValueError,KeyError,zipfile.BadZipFile):raise CloudError('El ZIP no contiene un manifiesto de sesión válido.') from None
            if not isinstance(manifest,dict) or manifest.get('id')!=path.name or manifest.get('schema')!='ksp-connector-session-v1':raise CloudError('El manifiesto no corresponde a la sesión pendiente.')
            row['app_version']=manifest.get('appVersion','unknown')
            row['telemetry_samples']=manifest.get('telemetrySamples')
            row['started_at']=manifest.get('startedAt')
            self.client.upload(expected,content,auth)
            self.client.index(row,auth)
            previous=state.get('archive_path');cleanup=state.get('cleanup',[])
            if previous and previous!=expected:cleanup.append(previous)
            state.update(fingerprint=pending['fingerprint'],archive_path=expected,last_success=utc_now(),pending=None,cleanup=list(dict.fromkeys(cleanup)))
            atomic_json(state_path,state);pending_path.unlink(missing_ok=True)
            self.set_status(lastSuccess=state['last_success'],status='uploaded',error=None,sessionId=path.name)
        if state.get('cleanup'):
            allowed=[p for p in state['cleanup'] if re.fullmatch(re.escape(auth['user_id']+'/'+path.name+'/')+r'[a-f0-9]{64}\.zip',p)]
            try:
                self.client.delete(allowed,auth);self.set_status(cleanupPending=False);state['cleanup']=[];atomic_json(state_path,state)
            except CloudError:self.set_status(cleanupPending=True)
        return bool(pending)

    def sync_once(self):
        self.recorder.capture_external()
        if self.paused:self.set_status(status='paused');return
        auth=self.client.auth()
        # Only the current session and previously queued sessions are sent automatically.
        queued=[p for p in sorted(self.root.iterdir()) if p.is_dir() and not p.is_symlink() and SESSION_ID.fullmatch(p.name) and ((p/'.cloud-upload.json').exists() or self.include_history) and p!=self.recorder.path]
        for path in [self.recorder.path,*queued]:
            if self.paused or self.stop_event.is_set():break
            self.sync_folder(path,auth)
        self.set_status(error=None,nextRetry=None)

    def run(self):
        try:self.worker_lock=WorkerLock(self.client.path.parent/'uploader.lock')
        except (CloudError,OSError) as error:self.set_status(status='blocked',error=str(error));return
        try:
            while not self.stop_event.is_set():
                try:
                    self.sync_once();self.failures=0;delay=self.client.config['interval_seconds']
                except (CloudError,OSError,ValueError,TypeError,KeyError) as error:
                    self.failures+=1;delay=min(900,30*2**min(self.failures-1,5))
                    # No raw HTTP bodies, URLs with tokens or OS exception text in public status.
                    self.set_status(status='retrying',error=str(error) if isinstance(error,CloudError) else 'Envío pendiente: revisa el estado local. La evidencia se conserva.',nextRetry=time.time()+delay)
                self.wake.wait(delay);self.wake.clear()
        finally:self.worker_lock.close()

    def start(self):
        self.thread=threading.Thread(target=self.run,name='ksp-cloud-upload',daemon=True);self.thread.start()

    def close(self):
        self.stop_event.set();self.wake.set()
        if self.thread:self.thread.join(timeout=2)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=DEFAULT_CONFIG)
    sub=parser.add_subparsers(dest='command',required=True)
    configure=sub.add_parser('configure');configure.add_argument('--url',required=True);configure.add_argument('--key',required=True);configure.add_argument('--interval',type=int,default=300)
    login=sub.add_parser('login');login.add_argument('--email')
    sub.add_parser('logout');sub.add_parser('status');sub.add_parser('doctor')
    args=parser.parse_args()
    try:
        if args.command=='configure':
            data=validate_config(dict(url=args.url,publishable_key=args.key,interval_seconds=args.interval,enabled=True));atomic_json(args.config,data)
            print('Destino configurado. Ejecuta login; el próximo arranque del conector enviará su sesión automáticamente.')
        elif args.command=='logout':
            (args.config.parent/'auth.json').unlink(missing_ok=True);print('Sesión de Supabase eliminada de este equipo. Se conservan las evidencias locales.')
        elif args.command=='login':
            client=SupabaseClient(args.config);auth=client.login(args.email or input('Correo del probador: '),getpass.getpass('Contraseña de Supabase Auth (no la de tu cuenta de administración): '));print('Inicio de sesión correcto. Usuario:',auth['user_id'])
        elif args.command=='doctor':
            result=SupabaseClient(args.config).doctor();print(json.dumps(result,ensure_ascii=False,indent=2))
            if not result['ready']:return 1
        else:
            client=SupabaseClient(args.config);print(json.dumps(dict(project=client.config['url'],intervalSeconds=client.config['interval_seconds'],signedIn=client.auth_path.exists()),ensure_ascii=False))
    except (CloudError,OSError,ValueError):parser.exit(1,'No se pudo completar. Revisa configuración, credenciales de Supabase Auth y permisos. No se modificaron tus evidencias.\n')


if __name__=='__main__':raise SystemExit(main())
