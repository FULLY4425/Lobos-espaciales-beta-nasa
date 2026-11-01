"""Local KSP 1/kRPC telemetry server. Never sends vehicle-control commands."""
import argparse
import math
import sys
import threading
import time
import uuid
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from http.server import ThreadingHTTPServer
from server import Handler


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


class Telemetry:
    def __init__(self, rpc_port=50000, stream_port=50001):
        self.rpc_port, self.stream_port = rpc_port, stream_port
        self.lock = threading.Lock()
        self.sample = None
        self.stopped = threading.Event()
        self.message = 'Conectando a kRPC en este equipo…'

    def snapshot(self):
        with self.lock:
            if self.sample and time.time()-self.sample['receivedAt'] <= 3:
                return 200, dict(status='connected', telemetry=self.sample)
            return 503, dict(status='unavailable', error=self.message, readOnly=True)

    def run(self):
        try:
            import krpc
        except ImportError:
            self.message = 'Instala las dependencias de integrations/requirements-ksp.txt.'
            return
        while not self.stopped.is_set():
            connection = None
            try:
                connection = krpc.connect(name='Ojo de Marte · solo lectura', address='127.0.0.1',
                                          rpc_port=self.rpc_port, stream_port=self.stream_port, timeout=2)
                session_id = uuid.uuid4().hex
                while not self.stopped.is_set():
                    vessel = connection.space_center.active_vessel
                    body = vessel.orbit.body
                    flight = vessel.flight(body.reference_frame)
                    # All RPC calls here are property reads. No control/autopilot access.
                    sample = validate_sample(dict(
                        latitude=flight.latitude, longitude=flight.longitude, heading=flight.heading,
                        surfaceAltitude=flight.surface_altitude, speed=flight.speed,
                        bodyRadius=body.equatorial_radius, body=body.name,
                        vessel=vessel.name, vesselId=f"{session_id}:{hash(vessel)}"))
                    with self.lock:
                        self.sample = sample
                    self.stopped.wait(.2)  # Five samples per second, no busy loop.
            except Exception:
                with self.lock:
                    self.sample = None
                    self.message = 'Sin telemetría. Abre KSP 1, activa kRPC y selecciona un vehículo.'
                self.stopped.wait(2)
            finally:
                if connection:
                    try:
                        connection.close()
                    except Exception:
                        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=7173)
    parser.add_argument('--rpc-port', type=int, default=50000)
    parser.add_argument('--stream-port', type=int, default=50001)
    args = parser.parse_args()
    telemetry = Telemetry(args.rpc_port, args.stream_port)

    class LocalHandler(Handler):
        def do_GET(self):
            if urlsplit(self.path).path == '/api/ksp':
                status, data = telemetry.snapshot()
                return self.reply(status, data)
            super().do_GET()

    worker = threading.Thread(target=telemetry.run, daemon=True)
    worker.start()
    httpd = ThreadingHTTPServer(('127.0.0.1', args.port), LocalHandler)
    print(f'Ojo de Marte + KSP 1: http://localhost:{args.port}/ — solo lectura', flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        telemetry.stopped.set()
        httpd.server_close()


if __name__ == '__main__':
    main()
