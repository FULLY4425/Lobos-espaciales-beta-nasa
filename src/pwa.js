const install=document.getElementById('installApp'),status=document.getElementById('connectionStatus');let prompt;
function connection(){status.hidden=navigator.onLine;status.textContent='Sin conexión: puedes consultar el mapa guardado. Calcular y exportar rutas requiere el servidor Python.';}
window.addEventListener('online',connection);window.addEventListener('offline',connection);connection();
window.addEventListener('beforeinstallprompt',event=>{event.preventDefault();prompt=event;install.hidden=false;});
install.onclick=async()=>{if(!prompt)return;await prompt.prompt();await prompt.userChoice;prompt=null;install.hidden=true;};
window.addEventListener('appinstalled',()=>{prompt=null;install.hidden=true;});
if('serviceWorker' in navigator&&window.isSecureContext){navigator.serviceWorker.register('/sw.js').catch(()=>{status.hidden=false;status.textContent='No se pudo guardar la aplicación para uso sin conexión. Puedes seguir usándola en línea.';});}
