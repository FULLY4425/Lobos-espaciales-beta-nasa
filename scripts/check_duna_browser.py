"""Optional local Chromium smoke test for Duna; not a real KSP/hardware test."""
import sys,threading,json,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from server import Handler
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
class Quiet(Handler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Quiet);threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path=shutil.which('chromium') or None,args=['--no-sandbox','--enable-unsafe-swiftshader']);page=b.new_page(viewport={'width':1450,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://localhost:{server.server_port}');f=page.frame_locator('#kspWorkspaceFrame');f.locator('#atlasStatus').filter(has_text='529.220').wait_for(timeout=25000)
  assert f.locator('#atlas2d').is_visible();page.screenshot(path='/tmp/duna-full.png');f.locator('#globalGlobe').click();f.locator('#atlas3d').wait_for(state='visible');page.wait_for_timeout(500);page.screenshot(path='/tmp/duna-globe.png');f.locator('#atlasStyle').select_option('height');f.locator('#globalMap2d').click();f.locator('#atlasStyle').select_option('texture');f.locator('#atlas2d').click(position={'x':535,'y':420});f.locator('#openAtlasRegion').click();f.locator('#atlasOverlay').wait_for(state='hidden');f.locator('#loadCatalogMap').click();f.locator('#textureStatus').filter(has_text='Cobertura de imagen:').wait_for();f.locator('#map3dButton').click();f.locator('#cameraSurface').click();f.locator('#cameraFollow').click();f.locator('#cameraFlyover').click();f.locator('#cameraAerial').click();f.locator('#surfaceStyle').select_option('mixed');f.locator('#dunaObjective option').nth(1).wait_for(state='attached');f.locator('#dunaObjective').select_option(label='Travesía · llegada registrada');f.locator('#addObjective').click()
  assert 'llegada registrada' in f.locator('#waypointList').inner_text();f.locator('#clearWaypoints').click();f.locator('#waypointName').fill('Destino de ensayo');f.locator('#waypointLat').fill('2.03246');f.locator('#waypointLon').fill('-71.62612');f.locator('#addCoordinate').click();f.locator('#kspSlope').fill('40');f.locator('#kspSlope').dispatch_event('change');f.locator('#planKsp').click();f.locator('#routeState').filter(has_text='Ruta KSP lista').wait_for();f.locator('#dunaWeather').select_option('wind');f.locator('#windDirection').fill('270');f.locator('#windDirection').dispatch_event('change');f.locator('#windReadout').filter(has_text='desde 270°').wait_for();assert f.locator('#windStreaks').is_visible();assert not f.locator('#shareGameWeather').is_checked();f.locator('#routeState').filter(has_text='Ruta KSP lista').wait_for();f.locator('#dunaWeather').select_option('storm');page.wait_for_timeout(800)
  plans=[];page.on('request',lambda r:plans.append(r.url) if r.url.endswith('/api/ksp/maps/plan') else None)
  f.locator('#dunaWeather').dispatch_event('change');page.wait_for_timeout(300);assert not plans,'El mismo escenario no debe recalcular'
  assert 'Ruta KSP lista' in f.locator('#routeState').inner_text(),f.locator('#routeState').inner_text();f.locator('#dunaWeather').select_option('clear');page.wait_for_timeout(500);f.locator('#rehearseRoute').click();page.wait_for_timeout(500)
  assert 'ENSAYO VIRTUAL' in f.locator('#rehearsalStatus').inner_text();f.locator('#rehearseRoute').click();f.locator('#rehearsalProgress').fill('500');f.locator('#rehearsalProgress').dispatch_event('input');f.locator('#nativeAR').click();f.locator('#nativeARStatus').filter(has_text='WebXR AR').wait_for();f.locator('#nativeHud').click()
  assert f.locator('aside').is_hidden();f.locator('#exitNativeHud').click()
  assert f.locator('aside').is_visible();page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(300)
  assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
  assert not f.locator('html').evaluate('(e)=>e.scrollWidth>innerWidth')
  page.set_viewport_size({'width':1450,'height':1000});f.locator('#lightweightMode').check();assert f.locator('#lightweightMode').is_checked();f.locator('#globalGlobe').click();f.locator('#atlas3d').wait_for(state='visible');page.wait_for_timeout(300);f.locator('#closeAtlas').click();f.locator('#lightweightMode').uncheck()
  assert not errors,errors;print('Duna full atlas/globe, source texture, objectives, mixed layer, cameras, weather reroute, rehearsal, HUD, AR fallback and compact layout passed.',errors);b.close()
finally:server.shutdown();server.server_close()
