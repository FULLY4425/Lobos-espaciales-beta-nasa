"""Local KSP 1/kRPC telemetry server. Never sends vehicle-control commands."""
import argparse
import math
import sys
import threading
import time
import uuid
import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from http.server import ThreadingHTTPServer
from server import Handler
from integrations.ksp_navigation import terrain_request, grid_to_geo, plan_ksp_mission
from integrations.ksp_session import SessionRecorder, VERSION


def validate_sample(sample):
    """Keep a small, finite, read-only telemetry contract."""
    keys = ('latitude', 'longitude', 'heading', 'surfaceAltitude', 'speed', 'bodyRadius')
    if any(isinstance(sample.get(k), bool) or not isinstance(sample.get(k), (int, float))
           or not math.isfinite(sample[k]) for k in keys):
        raise ValueError('Telemetría no válida.')
    if not -90 <= sample['latitude'] <= 90 or sample['bodyRadius'] <= 0:
        raise ValueError('Coordenadas o radio no válidos.')
    return {k: sample[k] for k in keys} | {
        'body': str(sample['body'])[:80], 'vessel': str(sample['vessel'])[:120],
        'vesselId': str(sample['vesselId'])[:120], 'receivedAt': time.time(),
        'source': 'KSP1-kRPC', 'readOnly': True,
    }


def read_vessel_sample(vessel, session_id):
    body = vessel.orbit.body
    flight = vessel.flight(body.reference_frame)
    # Heading is defined relative to local north, unlike body-fixed Cartesian axes.
    surface = vessel.flight()
    return body, validate_sample(dict(
        latitude=flight.latitude, longitude=flight.longitude, heading=surface.heading,
        surfaceAltitude=flight.surface_altitude, speed=flight.speed,
        bodyRadius=body.equatorial_radius, body=body.name,
        vessel=vessel.name, vesselId=f"{session_id}:{hash(vessel)}"))


class Telemetry:
    def __init__(self, rpc_port=50000, stream_port=50001, recorder=None):
        self.rpc_port, self.stream_port = rpc_port, stream_port
        self.recorder=recorder
        self.instance_id=uuid.uuid4().hex
        self.started_at=datetime.now(timezone.utc).isoformat()
        self.lock = threading.Lock()
        self.sample = None
        self.stopped = threading.Event()
        self.message = 'Conectando a kRPC en este equipo…'
        self.job = None
        self.work = None
        self.terrain = None

    def info(self):
        return dict(version=VERSION,instanceId=self.instance_id,startedAt=self.started_at,rpcPort=self.rpc_port,streamPort=self.stream_port,readOnly=True,recording=self.recorder.status() if self.recorder else None)

    def record(self, kind, data):
        if self.recorder:self.recorder.event(kind,data)

    def snapshot(self):
        with self.lock:
            if self.sample and time.time()-self.sample['receivedAt'] <= 3:
                return 200, dict(status='connected', telemetry=self.sample, protocol='ksp-surface-v1', connector=self.info(), capabilities=['telemetry','terrain-sampling','surface-planning'],readOnly=True)
            return 503, dict(status='unavailable', error=self.message, connector=self.info(), readOnly=True)

    def request_terrain(self, payload):
        status, data = self.snapshot()
        if status != 200:
            raise RuntimeError(data['error'])
        with self.lock:
            if self.work:
                raise RuntimeError('Hay un muestreo en curso. Espera o cancélalo.')
            terrain = terrain_request(data['telemetry'], payload, uuid.uuid4().hex)
            self.work = dict(terrain=terrain,index=0,checked=False,hasOcean=False)
            self.terrain = None
            self.job = dict(status='queued',id=terrain['id'],completed=0,total=terrain['width']*terrain['height'])
            self.record('sampling-start',dict(id=terrain['id'],body=terrain['body'],size=terrain['width'],cellMeters=terrain['cellMeters']))
            return dict(self.job)

    def terrain_status(self):
        with self.lock:
            if not self.job:
                return dict(status='empty',message='Solicita una región alrededor del vehículo activo.')
            result = dict(self.job)
            if result['status']=='complete':
                result['terrain'] = self.terrain
            return result

    def cancel_terrain(self, job_id=None):
        with self.lock:
            if job_id and (not self.job or self.job['id']!=job_id):
                return dict(status='ignored')
            self.work = None
            if self.job and self.job['status'] in ('queued','sampling'):
                self.job['status']='cancelled'
            return dict(status='cancelled')

    def _sample_batch(self, body, sample):
        with self.lock:
            work = self.work
        if not work:
            return
        terrain = work['terrain']
        try:
            if sample['vesselId']!=terrain['vesselId'] or sample['body']!=terrain['body']:
                raise ValueError('Cambió el vehículo o el cuerpo durante el muestreo. Carga otra región.')
            if not work['checked']:
                if not body.has_solid_surface:
                    raise ValueError('Este cuerpo no tiene una superficie sólida para una ruta de rover.')
                work['hasOcean']=bool(body.has_ocean)
                work['checked']=True
            batch_start=time.monotonic()
            for _ in range(16):
                with self.lock:
                    if self.work is not work:
                        return
                i=work['index'];x=i%terrain['width'];y=i//terrain['width']
                geo=grid_to_geo(terrain,x,y)
                height=body.bedrock_height(geo['lat'],geo['lon'])
                if isinstance(height,(int,float)) and not isinstance(height,bool) and math.isfinite(height):
                    terrain['elevations'][i]=height
                    terrain['water'][i]=work['hasOcean'] and height<0
                work['index']+=1
                with self.lock:
                    if self.work is not work:
                        return
                    self.job.update(status='sampling',completed=work['index'])
                    if work['index']==len(terrain['elevations']):
                        terrain['sampledAt']=datetime.now(timezone.utc).isoformat()
                        self.terrain=terrain
                        self.work=None
                        self.job['status']='complete'
                        if self.recorder:self.recorder.artifact('terrain',terrain)
                        return
                if time.monotonic()-batch_start>.08:
                    return
        except Exception as error:
            with self.lock:
                if self.work is work:
                    self.work=None
                    self.job.update(status='failed',error=f'No se pudo muestrear el terreno: {error}')
                    self.record('sampling-failed',dict(error=str(error)))

    def plan_surface(self, payload):
        status,data=self.snapshot()
        if status!=200:
            raise RuntimeError(data['error'])
        with self.lock:
            terrain=self.terrain
        if not terrain:
            raise ValueError('Carga primero un terreno KSP completo.')
        sample=data['telemetry']
        if terrain['vesselId'].split(':')[0]!=sample['vesselId'].split(':')[0]:
            raise ValueError('La conexión kRPC cambió. Vuelve a muestrear el terreno.')
        if terrain['body']!=sample['body'] or terrain['bodyRadius']!=sample['bodyRadius']:
            raise ValueError('El cuerpo activo cambió. Vuelve a cargar el terreno.')
        try:
            mission=plan_ksp_mission(terrain,payload)
            if self.recorder:self.recorder.artifact('mission',mission)
            return mission
        except ValueError as error:
            self.record('planning-failed',dict(error=str(error)))
            raise

    def run(self):
        try:
            import krpc
        except ImportError:
            self.message = 'Instala las dependencias de integrations/requirements-ksp.txt.'
            logging.error(self.message)
            return
        while not self.stopped.is_set():
            connection = None
            try:
                connection = krpc.connect(name='Ojo de Marte · solo lectura', address='127.0.0.1',
                                          rpc_port=self.rpc_port, stream_port=self.stream_port, timeout=2)
                session_id = uuid.uuid4().hex
                logging.info('Conexión kRPC establecida · solo lectura')
                self.record('krpc-connected',dict(session=session_id))
                while not self.stopped.is_set():
                    vessel = connection.space_center.active_vessel
                    # All RPC calls here are reads. No control/autopilot access.
                    body, sample = read_vessel_sample(vessel, session_id)
                    with self.lock:
                        self.sample = sample
                    if self.recorder:self.recorder.sample(sample)
                    self._sample_batch(body,sample)
                    self.stopped.wait(.2)  # Five samples per second, no busy loop.
            except Exception as error:
                logging.warning('kRPC no disponible: %s',error)
                self.record('krpc-unavailable',dict(error=str(error)))
                with self.lock:
                    self.sample = None
                    if self.work:
                        self.work=None
                        self.job.update(status='failed',error='Se perdió la conexión durante el muestreo.')
                    self.message = 'Sin telemetría. Abre KSP 1, activa kRPC y selecciona un vehículo.'
                self.stopped.wait(2)
            finally:
                if connection:
                    try:
                        connection.close()
                    except Exception:
                        pass


def create_handler(telemetry):
    class LocalHandler(Handler):
        def record_ksp_artifact(self, kind, data):
            if telemetry.recorder:telemetry.recorder.artifact(kind,data)

        def log_message(self, format, *args):
            logging.debug(format,*args)

        def do_GET(self):
            path=urlsplit(self.path).path
            if path=='/api/ksp/info':return self.reply(200,telemetry.info())
            if path=='/api/ksp/session':return self.reply(200,telemetry.recorder.status() if telemetry.recorder else dict(enabled=False))
            if path=='/api/ksp/session/export':
                if not telemetry.recorder:return self.reply(503,dict(error='Registro de disco desactivado. Usa la descarga del navegador.'))
                content=telemetry.recorder.export()
                self.send_response(200)
                self.send_header('Content-Type','application/zip')
                self.send_header('Content-Length',str(len(content)))
                self.send_header('Content-Disposition',f'attachment; filename="ksp-session-{telemetry.recorder.id}.zip"')
                self.send_header('Cache-Control','no-store')
                self.end_headers();self.wfile.write(content);return
            if urlsplit(self.path).path == '/api/ksp':
                status, data = telemetry.snapshot()
                return self.reply(status, data)
            if urlsplit(self.path).path == '/api/ksp/terrain':
                return self.reply(200,telemetry.terrain_status())
            super().do_GET()

        def do_POST(self):
            path=urlsplit(self.path).path
            origin=self.headers.get('Origin')
            if path.startswith('/api/ksp/') and origin and urlsplit(origin).netloc!=self.headers.get('Host'):
                return self.reply(403,dict(error='Origen no permitido.'))
            if path not in ('/api/ksp/terrain','/api/ksp/terrain/cancel','/api/ksp/plan','/api/ksp/session/events'):
                return super().do_POST()
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=16384:
                    return self.reply(413,dict(error='Solicitud demasiado grande o vacía.'))
                payload=json.loads(self.rfile.read(length))
                if not isinstance(payload,dict):
                    raise ValueError('Se requiere un objeto JSON.')
                if path=='/api/ksp/session/events':
                    events=payload.get('events')
                    if not isinstance(events,list) or len(events)>20:raise ValueError('Lote de eventos no válido.')
                    for event in events:
                        if not isinstance(event,dict) or not isinstance(event.get('type'),str) or len(event['type'])>60 or not isinstance(event.get('text'),str) or len(event['text'])>2000:raise ValueError('Evento no válido.')
                    for event in events:telemetry.record('browser-'+event['type'],dict(text=event['text']))
                    return self.reply(200,dict(recorded=bool(telemetry.recorder)))
                if path=='/api/ksp/terrain':
                    return self.reply(202,telemetry.request_terrain(payload))
                if path=='/api/ksp/terrain/cancel':
                    if not isinstance(payload.get('jobId'),str) or not payload['jobId']:
                        raise ValueError('Se requiere el identificador del muestreo a cancelar.')
                    return self.reply(200,telemetry.cancel_terrain(payload['jobId']))
                return self.reply(200,telemetry.plan_surface(payload))
            except (ValueError,TypeError) as error:
                return self.reply(400,dict(error=str(error)))
            except RuntimeError as error:
                return self.reply(503,dict(error=str(error)))

    return LocalHandler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=7173)
    parser.add_argument('--rpc-port', type=int, default=50000)
    parser.add_argument('--stream-port', type=int, default=50001)
    parser.add_argument('--session-dir',default='ksp-sessions',help='Carpeta local de evidencias, una sesión única por arranque')
    parser.add_argument('--no-session-log',action='store_true',help='Desactiva el registro de disco')
    args = parser.parse_args()
    telemetry = Telemetry(args.rpc_port, args.stream_port)
    try:httpd = ThreadingHTTPServer(('127.0.0.1', args.port), create_handler(telemetry))
    except OSError as error:
        parser.exit(1,f'No se pudo abrir el puerto {args.port}: {error}. Comprueba http://localhost:{args.port}/api/ksp/info y detén el conector anterior antes de reiniciar.\n')
    recorder=None if args.no_session_log else SessionRecorder(args.session_dir)
    telemetry.recorder=recorder
    handlers=[logging.StreamHandler()]
    if recorder and not recorder.error:
        try:handlers.append(RotatingFileHandler(recorder.path/'connector.log',maxBytes=1024*1024,backupCount=2,encoding='utf-8'))
        except OSError as error:recorder.error=str(error)
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s',handlers=handlers)
    worker = threading.Thread(target=telemetry.run, daemon=True)
    worker.start()
    logging.info('Ojo de Marte KSP v%s · instancia %s · http://localhost:%s/ksp-map.html · solo lectura',VERSION,telemetry.instance_id,args.port)
    if recorder:logging.info('Evidencias locales: %s',recorder.path.resolve())
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        telemetry.stopped.set()
        worker.join(timeout=3)
        if recorder:recorder.event('stop',dict(reason='server-stop'))
        httpd.server_close()


if __name__ == '__main__':
    main()
