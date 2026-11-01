// Compatibility endpoint only: retire previously installed workers and their old caches.
// The current web application does not register a service worker.
self.addEventListener('install',()=>self.skipWaiting());
self.addEventListener('activate',event=>event.waitUntil((async()=>{
  const keys=await caches.keys();
  await Promise.all(keys.filter(key=>key.startsWith('lobos-android-')).map(key=>caches.delete(key)));
  await self.registration.unregister();
})()));
