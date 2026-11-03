"""Chromium regression for persistent off-route detection in the synthetic demo."""
import sys,threading,shutil
from pathlib import Path
from http.server import ThreadingHTTPServer
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from server import Handler
from playwright.sync_api import sync_playwright
class Quiet(Handler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Quiet);threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path=shutil.which('chromium') or None,args=['--no-sandbox','--enable-unsafe-swiftshader']);page=b.new_page();plans=[]
  page.on('request',lambda r:plans.append(r.post_data_json) if r.url.endswith('/api/ksp/demo/plan') else None)
  page.goto(f'http://localhost:{server.server_port}/ksp-map.html');page.locator('#loadDemo').click();page.locator('#bodyName').filter(has_text='DEMO').wait_for()
  target=page.evaluate("async()=>{const {geoFromGrid}=await import('/src/ksp-geo.js');const r=await fetch('/api/ksp/demo/terrain');return geoFromGrid((await r.json()).terrain,28,16);}")
  page.locator('#waypointLat').fill(str(target['lat']));page.locator('#waypointLon').fill(str(target['lon']));page.locator('#addCoordinate').click();page.locator('#planKsp').click();page.locator('#routeState').filter(has_text='Ruta KSP lista').wait_for()
  page.locator('#demoDeviation').click();page.locator('#routeState').filter(has_text='recalculada').wait_for(timeout=10000)
  assert len(plans)==2,plans
  assert plans[-1]['replanReason']=='deviation',plans
  b.close();print('Persistent demo deviation recalculates once from the new position; this is not a real KSP driving test.')
finally:server.shutdown();server.server_close()
