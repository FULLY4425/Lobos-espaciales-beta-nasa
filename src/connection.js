const status=document.getElementById('connectionStatus');
function updateConnection(){if(!status)return;status.hidden=navigator.onLine;status.textContent='Sin conexión al servidor. La planificación, la exportación y la telemetría requieren conexión.';}
window.addEventListener('online',updateConnection);
window.addEventListener('offline',updateConnection);
updateConnection();

// Retire this project's previous offline worker/cache without touching user points or preferences.
async function retireLegacyCache(){
  if('serviceWorker' in navigator){const registrations=await navigator.serviceWorker.getRegistrations();for(const registration of registrations){const worker=registration.active||registration.waiting||registration.installing;if(worker&&new URL(worker.scriptURL).origin===location.origin&&new URL(worker.scriptURL).pathname==='/sw.js'&&registration.scope===`${location.origin}/`)await registration.unregister();}}
  if('caches' in window){const keys=await caches.keys();await Promise.all(keys.filter(key=>key.startsWith('lobos-android-')).map(key=>caches.delete(key)));}
}
retireLegacyCache().catch(()=>{/* A failed legacy cleanup must not block the web application. */});
