"""Run with python3 server.py. Development server; no external packages needed."""
import json
import os
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit
from mars.planner import plan_mission
from integrations.ksp_navigation import demo_terrain, plan_ksp_mission
from integrations.ksp_maps import read_archive, archive, plan_archive
KSP_DEMO = demo_terrain()

ROOT = Path(__file__).resolve().parent
TERRAIN = json.loads((ROOT/'public/data/terrain.json').read_text())
TARGETS = json.loads((ROOT/'public/data/targets.json').read_text())

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT),**kwargs)

    def reply(self,status,data,attachment=False):
        body=json.dumps(data,ensure_ascii=False,allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(body)))
        self.send_header('Cache-Control','no-store')
        if attachment:
            self.send_header('Content-Disposition','attachment; filename="lobos-espaciales-mision.json"')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        pathname=unquote(urlsplit(self.path).path)
        if pathname=='/api/ksp/demo/terrain':
            return self.reply(200,dict(status='complete',terrain=KSP_DEMO))
        if pathname in ('/api/ksp','/api/ksp/terrain'):
            return self.reply(503,dict(status='unavailable',error='KSP requiere el conector local integrations/ksp_server.py en el PC del juego.',readOnly=True))
        if pathname=='/api/health':
            return self.reply(200,dict(status='ok',engine='python',targets=len(TARGETS)))
        # Only serve application assets and public research, never Git metadata or code directories.
        resolved=(ROOT/pathname.lstrip('/')).resolve()
        allowed=pathname in ('/','/index.html','/ar.html','/ksp.html','/ksp-map.html','/sw.js') or pathname.startswith(('/src/','/public/','/docs/'))
        if not allowed or not resolved.is_relative_to(ROOT) or any(p.startswith('.') for p in Path(pathname).parts):
            return self.send_error(404)
        if resolved.is_dir() and pathname != "/":
            return self.send_error(404)
        super().do_GET()

    def do_POST(self):
        pathname=urlsplit(self.path).path
        if pathname in ('/api/ksp/terrain','/api/ksp/terrain/cancel','/api/ksp/plan'):
            return self.reply(503,dict(error='Abre la aplicación del conector local KSP en el PC del juego.'))
        if pathname not in ('/api/plan','/api/export','/api/ksp/demo/plan','/api/ksp/maps/validate','/api/ksp/maps/plan'):
            return self.reply(404,dict(error='Ruta desconocida.'))
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=(512*1024 if pathname.startswith('/api/ksp/maps/') else 16384):
                return self.reply(413,dict(error='Solicitud demasiado grande o vacía.'))
            payload=json.loads(self.rfile.read(length))
            if not isinstance(payload,dict):
                raise ValueError('Se requiere un objeto JSON.')
            if pathname=='/api/ksp/maps/validate':
                return self.reply(200,archive(read_archive(payload)))
            if pathname=='/api/ksp/maps/plan':
                return self.reply(200,plan_archive(payload))
            mission=plan_ksp_mission(KSP_DEMO,payload) if pathname=='/api/ksp/demo/plan' else plan_mission(TERRAIN,TARGETS,payload)
            self.reply(200,mission,attachment=pathname=='/api/export')
        except (ValueError,TypeError) as exc:
            self.reply(400,dict(error=str(exc)))

if __name__=='__main__':
    port=int(os.environ.get('PORT','5173'))
    print(f'Lobos Espaciales · Python · port {port}',flush=True)
    ThreadingHTTPServer(('0.0.0.0',port),Handler).serve_forever()
