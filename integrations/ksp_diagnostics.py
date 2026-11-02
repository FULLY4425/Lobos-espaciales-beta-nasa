"""Allowlisted, low-frequency host/flight diagnostics; no control or personal files."""
import math
import os
import platform
import shutil
import threading
import time
from datetime import datetime,timezone

FLIGHT_FIELDS={
 'meanAltitude':('flight','mean_altitude'),'verticalSpeed':('flight','vertical_speed'),
 'horizontalSpeed':('flight','horizontal_speed'),'gForce':('flight','g_force'),
 'pitch':('surface','pitch'),'roll':('surface','roll'),'massKg':('vessel','mass'),'thrustNewtons':('vessel','thrust'),
 'apoapsisAltitude':('orbit','apoapsis_altitude'),'periapsisAltitude':('orbit','periapsis_altitude'),
 'orbitalPeriodSeconds':('orbit','period'),'inclinationRad':('orbit','inclination'),'eccentricity':('orbit','eccentricity'),
 'timeToApoapsis':('orbit','time_to_apoapsis'),'timeToPeriapsis':('orbit','time_to_periapsis')}

def finite(value):
    return value if isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) else None


def read_flight(vessel,body,sources=None):
    result=dict(at=time.time(),source='KSP1-kRPC',readOnly=True)
    sources=dict(sources or {},vessel=vessel)
    for name,read in [('orbit',lambda:vessel.orbit),('flight',lambda:vessel.flight(body.reference_frame)),('surface',lambda:vessel.flight())]:
        try:
            if name not in sources:sources[name]=read()
        except Exception:pass
    for key,(source,attribute) in FLIGHT_FIELDS.items():
        try:result[key]=finite(getattr(sources[source],attribute))
        except Exception:result[key]=None
    try:
        state=vessel.situation
        name=getattr(state,'name',str(state).split('.')[-1])
        result['situation']=name if name in ('landed','splashed','pre_launch','flying','sub_orbital','orbiting','escaping','docked') else 'unknown'
    except Exception:result['situation']='unknown'
    for key,resource in [('liquidFuel','LiquidFuel'),('oxidizer','Oxidizer'),('electricCharge','ElectricCharge')]:
        try:result[key]=finite(vessel.resources.amount(resource))
        except Exception:result[key]=None
    result['availableFields']=sum(result[k] is not None for k in FLIGHT_FIELDS)
    return result


class ComputerMonitor:
    def __init__(self,recorder=None,storage_path='.',provider=None,enabled=True,interval=5):
        self.recorder=recorder;self.storage_path=storage_path;self.interval=max(5,interval);self.enabled=enabled
        self.stop_event=threading.Event();self.thread=None;self.lock=threading.Lock();self.last=None;self.primed=False;self.processes={}
        if provider is None:
            try:import psutil;provider=psutil
            except ImportError:pass
        self.provider=provider

    def collect(self):
        result=dict(at=time.time(),os=platform.system(),cpuCount=os.cpu_count(),status='ok' if self.provider else 'partial',cpuPercent=None,ramPercent=None,ramUsedBytes=None,ramTotalBytes=None,kspProcesses=[],kspDetected=None)
        try:
            disk=shutil.disk_usage(self.storage_path);result.update(diskFreeBytes=disk.free,diskTotalBytes=disk.total)
        except OSError:result.update(diskFreeBytes=None,diskTotalBytes=None)
        p=self.provider
        if p:
            try:
                cpu=p.cpu_percent(interval=None);memory=p.virtual_memory()
                result.update(cpuPercent=finite(cpu) if self.primed else None,ramPercent=finite(memory.percent),ramUsedBytes=memory.used,ramTotalBytes=memory.total)
                self.primed=True
                result['connectorRssBytes']=p.Process(os.getpid()).memory_info().rss
            except Exception:result['status']='partial'
            found={}
            try:
                for process in p.process_iter(['pid','name']):
                    try:
                        if (process.info.get('name') or '').lower() not in ('ksp_x64.exe','ksp.exe','ksp.x86_64','ksp.x86','ksp'):continue
                        previous=self.processes.get(process.pid);tracked=previous or process;cpu=tracked.cpu_percent(interval=None)
                        result['kspProcesses'].append(dict(cpuPercent=finite(cpu) if previous else None,rssBytes=tracked.memory_info().rss))
                        found[process.pid]=tracked
                        if len(found)>=4:break
                    except Exception:continue
                result['kspDetected']=bool(found);self.processes=found
            except Exception:result['status']='partial'
        else:result['notice']='Instala integrations/requirements-ksp.txt para medir CPU/RAM; no se inventan valores.'
        result['fps']=None  # kRPC does not provide reliable game FPS.
        with self.lock:self.last=result
        if self.recorder:self.recorder.diagnostic('computer',result)
        return result

    def status(self):
        with self.lock:return dict(enabled=self.enabled,intervalSeconds=self.interval,sample=self.last)

    def run(self):
        while not self.stop_event.is_set():
            try:self.collect()
            except Exception:pass  # Diagnostics must not stop telemetry.
            self.stop_event.wait(self.interval)

    def start(self):
        if self.enabled:self.thread=threading.Thread(target=self.run,name='ksp-computer-diagnostics',daemon=True);self.thread.start()

    def close(self):
        self.stop_event.set()
        if self.thread:self.thread.join(timeout=2)
