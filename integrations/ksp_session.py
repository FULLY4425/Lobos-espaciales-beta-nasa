"""Local read-only evidence. Cloud upload is optional and runs outside this recorder."""
import io
import math
import json
import os
import re
import threading
import time
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

VERSION='1.7.9'
MAX_EXTERNAL_LOG=16*1024*1024
GENERATED=re.compile(r'^(session\.json|KSP\.log|Player\.log|events\.jsonl|telemetry\.jsonl|computer\.jsonl|flight\.jsonl|analysis\.json|connector\.log(?:\.[12])?|(?:terrain|mission)-[a-f0-9]{32}\.json)$')


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
        self.browser_performance={};self.computer_info=None;self.situations={};self.diagnostic_counts={'computer':0,'flight':0};self.peaks={};self.event_counts={};self.last_analysis=0
        self.limit=max_bytes;self.bytes=0;self.dropped=0;self.error=None;self.last_sample=0;self.lock=threading.RLock()
        try:self.path.mkdir(parents=True,exist_ok=False)
        except OSError as error:self.error=str(error)
        self.event('start',dict(appVersion=VERSION,readOnly=True))

    def status(self):
        with self.lock:return dict(id=self.id,bytes=self.bytes,limitBytes=self.limit,dropped=self.dropped,error=self.error,appVersion=VERSION,telemetrySamples=self.samples)

    def _manifest(self):
        return dict(schema='ksp-connector-session-v1',id=self.id,appVersion=VERSION,readOnly=True,startedAt=self.started_at,stoppedAt=self.stopped_at,bytes=self.bytes,dropped=self.dropped,error=self.error,telemetrySamples=self.samples,externalLogs=self.external_summary,diagnosticSamples=dict(self.diagnostic_counts),notice='Evidencias de una sesión local. La presencia de telemetría no certifica todas las pruebas. Los logs externos solo se incluyen si se configuran sus rutas.')

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
        with self.lock:
            key=kind if kind in self.event_counts or len(self.event_counts)<64 else 'other'
            self.event_counts[key]=self.event_counts.get(key,0)+1
            if kind=='browser-performance-snapshot':
                try:
                    stats=json.loads(data.get('text','{}'))
                    for key in ('renderCpu','render2d','render3d','atlas2d','atlas3d','httpRequest'):
                        item=stats.get(key)
                        if not isinstance(item,dict):continue
                        count,total,maximum=item.get('count'),item.get('totalMs'),item.get('maxMs')
                        if not all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) and 0<=v<=1e12 for v in (count,total,maximum)) or not 0<count<=1e9:continue
                        value=dict(count=count,totalMs=total,maxMs=maximum,meanMs=round(total/count,2))
                        for field in ('p95RecentMs','over50Ms'):
                            v=item.get(field)
                            if isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) and 0<=v<=(count if field=='over50Ms' else maximum):value[field]=v
                        self.browser_performance[key]=value
                    for source,target in [('renderCpu','browserRenderMaxMs'),('httpRequest','httpRequestMaxMs')]:
                        value=stats.get(source,{}).get('maxMs')
                        if isinstance(value,(int,float)) and not isinstance(value,bool) and 0<=value<=1e9:self.peaks[target]=max(self.peaks.get(target,0),value)
                except (ValueError,TypeError,AttributeError):pass
        if kind=='stop':
            self.capture_external();self.stopped_at=datetime.now(timezone.utc).isoformat();self.write_analysis()
        item=dict(at=datetime.now(timezone.utc).isoformat(),type=kind,data=data)
        return self._write('events.jsonl',(json.dumps(item,ensure_ascii=False,allow_nan=False)+'\n').encode(),True)

    def sample(self, data):
        if time.monotonic()-self.last_sample<1:return
        self.last_sample=time.monotonic()
        with self.lock:
            value=data.get('rpcReadMs')
            if isinstance(value,(int,float)) and 0<=value<=1e9:self.peaks['rpcReadMaxMs']=max(self.peaks.get('rpcReadMaxMs',0),value)
        with self.lock:
            for key in ('speed','surfaceAltitude'):
                value=data.get(key)
                if isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value):self.peaks[key]=max(self.peaks.get(key,value),value)
        self._write('telemetry.jsonl',(json.dumps(data,ensure_ascii=False,allow_nan=False)+'\n').encode(),True)

    def diagnostic(self,kind,data):
        if kind not in ('computer','flight'):raise ValueError('Diagnóstico no válido.')
        if self._write(kind+'.jsonl',(json.dumps(data,ensure_ascii=False,allow_nan=False)+'\n').encode(),True):
            with self.lock:
                self.diagnostic_counts[kind]+=1
                if kind=='computer':self.computer_info={k:data.get(k) for k in ('os','cpuCount','ramTotalBytes','diskTotalBytes','kspDetected')}
                if kind=='flight':
                    state=data.get('situation','unknown')
                    if state in ('landed','splashed','pre_launch','flying','sub_orbital','orbiting','escaping','docked','unknown'):self.situations[state]=self.situations.get(state,0)+1
                for key in ('cpuPercent','ramPercent','surfaceAltitude','meanAltitude','verticalSpeed','gForce'):
                    value=data.get(key)
                    if isinstance(value,(int,float)) and not isinstance(value,bool):self.peaks[key]=max(self.peaks.get(key,value),value)
            if time.monotonic()-self.last_analysis>=60:self.write_analysis()

    def analysis(self):
        with self.lock:
            recommendations=[]
            if self.peaks.get('cpuPercent',0)>=90:recommendations.append('CPU elevada: comparar sesiones con malla o detalle 3D menores; no atribuye causalidad a KSP.')
            if self.peaks.get('ramPercent',0)>=90:recommendations.append('RAM elevada: revisar consumo de KSP y otros programas; no se registra su listado.')
            losses=self.event_counts.get('krpc-unavailable',0)
            if losses:recommendations.append('Revisar desconexiones kRPC y cambios de escena con sus marcas de tiempo.')
            render=self.browser_performance.get('renderCpu',{})
            if render.get('count',0)>=30 and (render.get('meanMs',0)>20 or render.get('over50Ms',0)/render['count']>=.1):recommendations.append('Repintado costoso repetido: prueba Modo ligero y compara 2D/3D en la misma escena; no mide FPS de KSP.')
            elif self.peaks.get('browserRenderMaxMs',0)>100:recommendations.append('Pico aislado de repintado: revisar media y p95 antes de concluir lentitud sostenida; no mide FPS de KSP.' if render.get('count',0)>=30 else 'Pico de repintado: faltan suficientes mediciones de media y p95 para evaluar si es sostenido; no mide FPS de KSP.')
            if self.peaks.get('rpcReadMaxMs',0)>500:recommendations.append('Lectura kRPC lenta: comparar RPC, cambios de escena y diagnóstico adicional antes de atribuir fallos al mapa.')
            if self.peaks.get('httpRequestMaxMs',0)>2000:recommendations.append('Peticiones locales lentas: comparar carga del conector, muestreo y registro.')
            if not self.samples:recommendations.append('No hay telemetría de juego: comprobar kRPC antes de evaluar rutas.')
            return dict(schema='ksp-session-analysis-v1',generatedAt=datetime.now(timezone.utc).isoformat(),telemetrySamples=self.samples,diagnosticSamples=dict(self.diagnostic_counts),peaks=dict(self.peaks),browserPerformance={k:dict(v) for k,v in self.browser_performance.items()},computer=self.computer_info,situations=dict(self.situations),events=dict(self.event_counts),recommendations=recommendations,notice='Resumen automático por reglas; no modifica el código ni demuestra causas. FPS no disponible por kRPC.')

    def write_analysis(self):
        self.last_analysis=time.monotonic()
        self._write('analysis.json',json.dumps(self.analysis(),ensure_ascii=False,allow_nan=False).encode())

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
            # Summary and manifest must describe the exact same locked snapshot.
            files=[(name,data) for name,data in files if name!='analysis.json']
            files.append(('analysis.json',json.dumps(self.analysis(),ensure_ascii=False,allow_nan=False).encode()))
        return make_archive(files,manifest)
