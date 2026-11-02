"""Local read-only evidence. Cloud upload is optional and runs outside this recorder."""
import io
import json
import os
import re
import threading
import time
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

VERSION='1.6.0'
MAX_EXTERNAL_LOG=16*1024*1024
GENERATED=re.compile(r'^(session\.json|KSP\.log|Player\.log|events\.jsonl|telemetry\.jsonl|connector\.log(?:\.[12])?|(?:terrain|mission)-[a-f0-9]{32}\.json)$')


def evidence_files(path):
    return [p for p in sorted(Path(path).iterdir()) if GENERATED.fullmatch(p.name) and p.is_file() and not p.is_symlink()]


def make_archive(files,manifest):
    output=io.BytesIO()
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('session.json',json.dumps(manifest,ensure_ascii=False,allow_nan=False))
        for name,content in files:
            if name!='session.json':z.writestr(name,content)
    return output.getvalue()


def archive_folder(path):
    files=[]
    for p in evidence_files(path):
        try:files.append((p.name,p.read_bytes()))
        except OSError:continue
    manifest=dict(schema='ksp-connector-session-v1',id=Path(path).name,appVersion='unknown',readOnly=True)
    for name,content in files:
        if name=='session.json':manifest=json.loads(content)
    return make_archive(files,manifest)


class SessionRecorder:
    def __init__(self, root, max_bytes=32*1024*1024, external_logs=None):
        self.id=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H-%M-%SZ')+'-'+uuid.uuid4().hex[:12]
        self.path=Path(root)/self.id
        self.started_at=datetime.now(timezone.utc).isoformat();self.stopped_at=None;self.samples=0;self.external_summary={}
        self.external_logs={k:Path(v) for k,v in (external_logs or {}).items() if k in ('KSP.log','Player.log') and v}
        self.limit=max_bytes;self.bytes=0;self.dropped=0;self.error=None;self.last_sample=0;self.lock=threading.Lock()
        try:self.path.mkdir(parents=True,exist_ok=False)
        except OSError as error:self.error=str(error)
        self.event('start',dict(appVersion=VERSION,readOnly=True))

    def status(self):
        with self.lock:return dict(id=self.id,bytes=self.bytes,limitBytes=self.limit,dropped=self.dropped,error=self.error,appVersion=VERSION,telemetrySamples=self.samples)

    def _manifest(self):
        return dict(schema='ksp-connector-session-v1',id=self.id,appVersion=VERSION,readOnly=True,startedAt=self.started_at,stoppedAt=self.stopped_at,bytes=self.bytes,dropped=self.dropped,error=self.error,telemetrySamples=self.samples,externalLogs=self.external_summary,notice='Evidencias de una sesión local. La presencia de telemetría no certifica todas las pruebas. Los logs externos solo se incluyen si se configuran sus rutas.')

    def _save_metadata(self):
        try:
            temporary=self.path/'.session-meta.tmp';temporary.write_text(json.dumps(self._manifest(),ensure_ascii=False),encoding='utf-8');os.replace(temporary,self.path/'session.json')
        except OSError:pass  # Recording errors must never interrupt game telemetry.

    def _write(self, name, data, append=False):
        with self.lock:
            if self.error or self.bytes+len(data)>self.limit:
                self.dropped+=1;self._save_metadata();return False
            try:
                if append:
                    with (self.path/name).open('ab') as file:file.write(data)
                else:
                    temporary=self.path/('.'+name+'.tmp');temporary.write_bytes(data);os.replace(temporary,self.path/name)
                self.bytes+=len(data)
                if name=='telemetry.jsonl':self.samples+=1
                self._save_metadata();return True
            except OSError as error:self.error=str(error);self._save_metadata();return False

    def event(self, kind, data):
        if kind=='stop':
            self.capture_external();self.stopped_at=datetime.now(timezone.utc).isoformat()
        item=dict(at=datetime.now(timezone.utc).isoformat(),type=kind,data=data)
        return self._write('events.jsonl',(json.dumps(item,ensure_ascii=False,allow_nan=False)+'\n').encode(),True)

    def sample(self, data):
        if time.monotonic()-self.last_sample<1:return
        self.last_sample=time.monotonic()
        self._write('telemetry.jsonl',(json.dumps(data,ensure_ascii=False,allow_nan=False)+'\n').encode(),True)

    def artifact(self, kind, data):
        if kind not in ('terrain','mission'):raise ValueError('Tipo de evidencia no válido.')
        name=kind+'-'+uuid.uuid4().hex+'.json'
        self._write(name,json.dumps(data,ensure_ascii=False,allow_nan=False).encode())
        self.event(kind,dict(file=name))

    def capture_external(self):
        external={}
        for name,path in self.external_logs.items():
            try:
                with path.open('rb') as f:
                    size=os.fstat(f.fileno()).st_size
                    f.seek(max(0,size-MAX_EXTERNAL_LOG));content=f.read(MAX_EXTERNAL_LOG)
                destination=self.path/name
                if not destination.exists() or destination.read_bytes()!=content:
                    temporary=self.path/('.'+name+'.tmp');temporary.write_bytes(content);os.replace(temporary,destination)
                external[name]=dict(available=True,size=size,includedBytes=len(content),truncated=size>MAX_EXTERNAL_LOG)
            except OSError:external[name]=dict(self.external_summary.get(name,{}),available=False,reason='unreadable',cached=(self.path/name).is_file())
        with self.lock:
            if external!=self.external_summary:
                self.external_summary=external;self._save_metadata()

    def export(self):
        self.capture_external()
        # Copy under the short recorder lock; compression and network never hold it.
        with self.lock:
            files=[];manifest=self._manifest()
            if self.path.exists():
                for p in evidence_files(self.path):
                    try:files.append((p.name,p.read_bytes()))
                    except OSError:continue
        return make_archive(files,manifest)
