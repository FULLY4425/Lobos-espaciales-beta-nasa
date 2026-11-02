"""Local read-only test evidence, unique directories, bounded disk use, no uploads."""
import io
import json
import threading
import time
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

VERSION='1.4.0'


class SessionRecorder:
    def __init__(self, root, max_bytes=32*1024*1024):
        self.id=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H-%M-%SZ')+'-'+uuid.uuid4().hex[:12]
        self.path=Path(root)/self.id
        self.limit=max_bytes;self.bytes=0;self.dropped=0;self.error=None;self.last_sample=0;self.lock=threading.Lock()
        try:self.path.mkdir(parents=True,exist_ok=False)
        except OSError as error:self.error=str(error)
        self.event('start',dict(appVersion=VERSION,readOnly=True))

    def status(self):
        with self.lock:return dict(id=self.id,bytes=self.bytes,limitBytes=self.limit,dropped=self.dropped,error=self.error,appVersion=VERSION)

    def _write(self, name, data, append=False):
        with self.lock:
            if self.error or self.bytes+len(data)>self.limit:self.dropped+=1;return False
            try:
                with (self.path/name).open('ab' if append else 'xb') as file:file.write(data)
                self.bytes+=len(data);return True
            except OSError as error:self.error=str(error);return False

    def event(self, kind, data):
        item=dict(at=datetime.now(timezone.utc).isoformat(),type=kind,data=data)
        return self._write('events.jsonl',(json.dumps(item,ensure_ascii=False,allow_nan=False)+'\n').encode(),True)

    def sample(self, data):
        if time.monotonic()-self.last_sample<1:return
        self.last_sample=time.monotonic()
        self._write('telemetry.jsonl',(json.dumps(data,ensure_ascii=False,allow_nan=False)+'\n').encode(),True)

    def artifact(self, kind, data):
        name=kind+'-'+uuid.uuid4().hex+'.json'
        self._write(name,json.dumps(data,ensure_ascii=False,allow_nan=False).encode())
        self.event(kind,dict(file=name))

    def export(self):
        with self.lock:
            output=io.BytesIO()
            with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
                z.writestr('session.json',json.dumps(dict(schema='ksp-connector-session-v1',id=self.id,appVersion=VERSION,readOnly=True,bytes=self.bytes,dropped=self.dropped,error=self.error,notice='Estado de KSP y evidencias locales. No incluye KSP.log ni Player.log; adjúntalos por separado.'),ensure_ascii=False))
                if self.path.exists():
                    for p in sorted(self.path.iterdir()):
                        if p.is_file() and not p.is_symlink():
                            try:z.write(p,p.name)
                            except OSError:pass
            return output.getvalue()
