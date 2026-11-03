"""Local Chromium test: accepted event + lost response retries once without duplicate recording."""
import sys,threading,shutil
from pathlib import Path
from unittest.mock import Mock
from http.server import ThreadingHTTPServer
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from integrations.ksp_server import Telemetry,create_handler
from playwright.sync_api import sync_playwright
telemetry=Telemetry();telemetry.record=Mock()
server=ThreadingHTTPServer(('127.0.0.1',0),create_handler(telemetry))
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=shutil.which('chromium') or None,args=['--no-sandbox','--enable-unsafe-swiftshader'])
  page=browser.new_page();page.goto(f'http://localhost:{server.server_port}/ksp-map.html')
  result=page.evaluate('''async instance=>{
   const {createEventQueue}=await import('/src/ksp-events.js');let first=true;
   const q=createEventQueue(async body=>{const r=await fetch('/api/ksp/session/events',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});if(first){first=false;throw Error('Synthetic lost response');}return r;});
   q.push({type:'arrival-confirmed',text:'Synthetic event delivery test'},instance);
   const firstResult=await q.flush(instance),secondResult=await q.flush(instance);
   return {firstResult,secondResult,size:q.size};
  }''',telemetry.instance_id)
  assert result==dict(firstResult=False,secondResult=True,size=0),result
  telemetry.record.assert_called_once_with('browser-arrival-confirmed',dict(text='Synthetic event delivery test'))
  browser.close();print('Browser → local connector retry and deduplication passed; no remote uploads.')
finally:server.shutdown();server.server_close()
