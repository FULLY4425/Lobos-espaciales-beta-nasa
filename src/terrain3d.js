import * as THREE from './vendor/three.module.js';
import {slopeAt} from './route.js';
import {nearestOnRoute} from './ar-tracking.js';

// Coordinates are meters: east = X, height = Y, south = Z. No vertical exaggeration.
export function createTerrain3D(canvas, terrain, onSelect, onPlace=()=>false, navigation=null,events={}) {
  const renderer=new THREE.WebGLRenderer({canvas,antialias:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));
  renderer.setClearColor('#11191c');
  const scene=new THREE.Scene(), camera=new THREE.PerspectiveCamera(45,1,.1,30000);
  const {width:w,height:h,cellMeters:m,elevations:z}=terrain;
  const valid=z.filter(v=>v!==null),floor=Math.min(...valid),ceiling=Math.max(...valid),span=Math.max(w,h)*m;
  const focus=new THREE.Vector3(0,30,0);
  let yaw=0,pitch=1.32,distance=span*1.15,active=false,frame=0,state,flight=false,animation=0,lastTime=0,transition=null;
  const geometry=new THREE.BufferGeometry(),vertices=[],uvs=[],indices=[];
  for(let y=0;y<h;y++)for(let x=0;x<w;x++) {
    vertices.push((x-w/2)*m,(z[y*w+x]??floor)-floor,(y-h/2)*m);
    uvs.push(x/w,1-y/h);
  }
  for(let y=0;y<h-1;y++)for(let x=0;x<w-1;x++) {
    const a=y*w+x,b=a+1,c=a+w,d=c+1;
    // Missing elevations remain holes rather than invented terrain.
    if([a,c,b].every(i=>z[i]!==null))indices.push(a,c,b);
    if([b,c,d].every(i=>z[i]!==null))indices.push(b,c,d);
  }
  geometry.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));
  geometry.setAttribute('uv',new THREE.Float32BufferAttribute(uvs,2));
  geometry.setIndex(indices);geometry.computeVertexNormals();
  const textureCanvas=document.createElement('canvas');textureCanvas.width=w*12;textureCanvas.height=h*12;
  const texture=new THREE.CanvasTexture(textureCanvas);texture.colorSpace=THREE.SRGBColorSpace;
  texture.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());
  const mesh=new THREE.Mesh(geometry,new THREE.MeshBasicMaterial({map:texture,side:THREE.DoubleSide}));scene.add(mesh);
  const overlays=new THREE.Group();scene.add(overlays);
  const raycaster=new THREE.Raycaster();raycaster.params.Points.threshold=10;
  let pickable=null,pickTargets=[],worldMode='terrain',running=false,progress=0,totalLength=0,routePoints=[],routeLengths=[],routeKey='',walkTime=0,lookYaw=0,lookPitch=0,offRoutePosition=null,hold=false;
  const globeScene=new THREE.Scene();globeScene.background=new THREE.Color('#060d16');
  const globe=new THREE.Mesh(new THREE.SphereGeometry(500,96,64),new THREE.MeshBasicMaterial({color:0xffffff}));globeScene.add(globe);
  const globalTexture=new THREE.TextureLoader().load('/public/imagery/mars-global.jpg',()=>render(),undefined,()=>{document.getElementById('journeyStatus').textContent='No se pudo cargar la textura del globo. Puedes usar el terreno local.';});globalTexture.colorSpace=THREE.SRGBColorSpace;globe.material.map=globalTexture;
  const lat=terrain.north*Math.PI/180,lon=terrain.west*Math.PI/180;
  const sitePosition=new THREE.Vector3(Math.cos(lat)*Math.cos(lon),Math.sin(lat),-Math.cos(lat)*Math.sin(lon));
  const site=new THREE.Mesh(new THREE.SphereGeometry(7,16,12),new THREE.MeshBasicMaterial({color:'#77ffe1'}));site.position.copy(sitePosition.clone().multiplyScalar(506));globeScene.add(site);
  const ring=new THREE.Mesh(new THREE.TorusGeometry(16,1.5,8,48),new THREE.MeshBasicMaterial({color:'#77ffe1'}));ring.position.copy(sitePosition.clone().multiplyScalar(508));ring.lookAt(sitePosition.clone().multiplyScalar(600));globeScene.add(ring);
  const astronauts=[];
  function astronaut(color){const group=new THREE.Group(),material=new THREE.MeshBasicMaterial({color}),dark=new THREE.MeshBasicMaterial({color:'#182d3d'});
    function part(geometry,mat,x,y,z){const item=new THREE.Mesh(geometry,mat);item.position.set(x,y,z);group.add(item);return item;}
    part(new THREE.CapsuleGeometry(.25,.5,4,8),material,0,1,0);part(new THREE.SphereGeometry(.28,16,12),material,0,1.65,0);part(new THREE.SphereGeometry(.21,12,8),dark,0,1.67,.17);part(new THREE.BoxGeometry(.45,.6,.25),material,0,1,-.28);
    const limbs=[];for(const side of [-1,1]){const leg=part(new THREE.CapsuleGeometry(.1,.45,4,8),material,side*.15,.35,0);const arm=part(new THREE.CapsuleGeometry(.09,.4,4,8),material,side*.4,1,0);limbs.push(leg,arm);}scene.add(group);astronauts.push({group,limbs});}
  astronaut('#fff4df');astronaut('#f9a06b');
  function routeAt(d){if(!routePoints.length)return new THREE.Vector3();d=THREE.MathUtils.clamp(d,0,totalLength);let i=1;while(i<routeLengths.length-1&&routeLengths[i]<d)i++;if(routePoints.length===1)return routePoints[0].clone();const t=(d-routeLengths[i-1])/(routeLengths[i]-routeLengths[i-1]||1);return routePoints[i-1].clone().lerp(routePoints[i],t);}
  function setRoute(points){const key=JSON.stringify(points);if(key===routeKey)return;routeKey=key;running=false;progress=0;offRoutePosition=null;hold=false;routePoints=points.map(([x,y])=>point(x,y,0));routeLengths=[0];totalLength=0;for(let i=1;i<routePoints.length;i++){totalLength+=routePoints[i].distanceTo(routePoints[i-1]);routeLengths.push(totalLength);}document.getElementById('walkRoute').disabled=totalLength===0;document.getElementById('routeProgress').disabled=totalLength===0;document.getElementById('walkRoute').setAttribute('aria-pressed','false');document.getElementById('journeyStatus').textContent=totalLength?'Ruta lista. Inicia el recorrido simulado.':'Calcula una ruta para recorrerla con los astronautas.';}
  function updateAstronauts(){for(const [i,a] of astronauts.entries()){a.group.visible=worldMode!=='globe'&&totalLength>0&&!(worldMode==='surface'&&i===0);const d=Math.max(0,progress*totalLength-i*8),pos=routeAt(d),ahead=routeAt(Math.min(totalLength,d+3));if(i===0&&offRoutePosition)pos.copy(point(offRoutePosition.x,offRoutePosition.y,0));a.group.position.copy(pos);a.group.rotation.y=Math.atan2(ahead.x-pos.x,ahead.z-pos.z);a.group.scale.setScalar(worldMode==='surface'||worldMode==='follow'?1:6);for(const [j,limb] of a.limbs.entries())limb.rotation.x=running?Math.sin(walkTime*5+(j%2?Math.PI:0)+(j>1?Math.PI:0))*.5:0;}}
  function startAnimation(){if(!animation){lastTime=performance.now();animation=requestAnimationFrame(animate);}}
  function setMode(mode){stop();running=false;worldMode=mode;lookYaw=lookPitch=0;document.getElementById('walkRoute').setAttribute('aria-pressed','false');
    for(const [id,key] of [['showGlobe','globe'],['showTerrain','terrain'],['showSurface','surface'],['showFollow','follow']])document.getElementById(id).setAttribute('aria-pressed',String(mode===key));
    document.querySelector('.workspace').dataset.worldMode=mode;
    document.getElementById('surfaceNote').hidden=mode!=='surface';document.getElementById('globeNote').hidden=mode!=='globe';
    if(mode==='globe'){yaw=Math.atan2(sitePosition.x,sitePosition.z);pitch=.18;distance=1500;focus.set(0,0,0);}else if(mode==='terrain'){yaw=0;pitch=1.32;distance=span*1.15;focus.set(0,30,0);}render();}
  function toggleWalk(){if(hold)return false;if(!totalLength)return false;if(worldMode==='globe')setMode('follow');transition=null;flight=false;if(progress>=1)progress=0;running=!running;if(!running)navigation?.pause();if(running)startAnimation();render();return running;}
  function seek(value){stop();navigation?.seek(value);progress=THREE.MathUtils.clamp(value,0,1);render();}

  function moveAstronaut(x,y){if(hold||!Number.isFinite(x)||!Number.isFinite(y)||x<0||y<0||x>w-1||y>h-1||z[Math.round(y)*w+Math.round(x)]===null)return;stop();offRoutePosition={x,y};render();}
  function navigationState(){const here=routeAt(progress*totalLength);return {progress,running,position:offRoutePosition||{x:here.x/m+w/2,y:here.z/m+h/2}};}
  function displace(){if(!totalLength||hold)return null;stop();const origin=navigationState().position;for(const [dx,dy] of [[0,4],[0,-4],[4,0],[-4,0],[4,4],[-4,-4],[0,6],[0,-6]]){const x=Math.round(origin.x+dx),y=Math.round(origin.y+dy);if(x<0||y<0||x>=w||y>=h||z[y*w+x]===null||slopeAt(terrain,x,y)>state.maxSlope)continue;const near=nearestOnRoute({x:(x-state.path[0][0])*m,y:(y-state.path[0][1])*m},state.path,terrain);if(near&&near.crossTrack>30){offRoutePosition={x,y};render();return navigationState();}}return null;}
  function point(x,y,lift=4){const ix=Math.max(0,Math.min(w-1,Math.round(x))),iy=Math.max(0,Math.min(h-1,Math.round(y)));return new THREE.Vector3((x-w/2)*m,(z[iy*w+ix]??floor)-floor+lift,(y-h/2)*m);}
  function targetPoint(p,lift){return point((p.lon-terrain.west)/terrain.degreeStep,(terrain.north-p.lat)/terrain.degreeStep,lift);}
  function clearOverlays(){for(const child of [...overlays.children]){child.geometry.dispose();child.material.dispose();overlays.remove(child);}}
  function update(next){
    state=next;setRoute(next.path);
    const ctx=textureCanvas.getContext('2d');ctx.fillStyle='#5d5144';ctx.fillRect(0,0,textureCanvas.width,textureCanvas.height);
    if(next.satellite&&next.image.complete&&next.image.naturalWidth)ctx.drawImage(next.image,0,0,textureCanvas.width,textureCanvas.height);
    else for(let y=0;y<h;y++)for(let x=0;x<w;x++){const v=z[y*w+x];if(v===null)continue;const n=(v-floor)/(ceiling-floor||1);ctx.fillStyle=next.relief?`hsl(28 25% ${28+n*35}%)`:'#766657';ctx.fillRect(x*12,y*12,12,12);}
    if(next.slopes)for(let y=0;y<h;y++)for(let x=0;x<w;x++){const s=slopeAt(terrain,x,y);ctx.fillStyle=s>next.maxSlope?'#ef614b99':s>10?'#e8c26444':'#74b9a422';ctx.fillRect(x*12,y*12,12,12);}
    texture.needsUpdate=true;clearOverlays();pickable=null;
    for(const zone of next.weather?.restrictions||[]){const cx=(zone.lon-terrain.west)/terrain.degreeStep,cy=(terrain.north-zone.lat)/terrain.degreeStep,r=zone.radiusMeters/m;const ring=[];for(let i=0;i<65;i++){const a=i/64*Math.PI*2;ring.push(point(cx+Math.cos(a)*r,cy+Math.sin(a)*r,8));}overlays.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(ring),new THREE.LineBasicMaterial({color:'#ff725c'})));}
    if(next.science){pickTargets=next.targets;const g=new THREE.BufferGeometry().setFromPoints(pickTargets.map(p=>targetPoint(p,5)));pickable=new THREE.Points(g,new THREE.PointsMaterial({color:'#b5e5d2',size:4,sizeAttenuation:false,depthTest:true}));overlays.add(pickable);}
    if(next.path.length){const g=new THREE.BufferGeometry().setFromPoints(next.path.map(([x,y])=>point(x,y,5)));const line=new THREE.Line(g,new THREE.LineBasicMaterial({color:'#ffad74'}));line.userData.route=true;overlays.add(line);}
    for(const p of next.stops){const marker=new THREE.Mesh(new THREE.SphereGeometry(7,12,8),new THREE.MeshBasicMaterial({color:'#ff945c'}));marker.position.copy(targetPoint(p,8));overlays.add(marker);}
    if(next.selected){const marker=new THREE.Mesh(new THREE.SphereGeometry(11,12,8),new THREE.MeshBasicMaterial({color:'white',wireframe:true}));marker.position.copy(targetPoint(next.selected,8));overlays.add(marker);}
    render();
  }
  function render(){if(!active)return;if(offRoutePosition&&!hold&&state?.path?.length>1){const origin=state.path[0],nearest=nearestOnRoute({x:(offRoutePosition.x-origin[0])*m,y:(offRoutePosition.y-origin[1])*m},state.path,terrain);const restricted=state.weather?.restrictions.some(zone=>Math.hypot(offRoutePosition.x-(zone.lon-terrain.west)/terrain.degreeStep,offRoutePosition.y-(terrain.north-zone.lat)/terrain.degreeStep)*m<=zone.radiusMeters);if(nearest?.crossTrack>30||restricted){hold=true;running=false;const snapshot={...navigationState(),reason:restricted?'weather':'deviation'};queueMicrotask(()=>events.onDeviation?.(snapshot));}else if(nearest){progress=nearest.progress;}}const rect=canvas.getBoundingClientRect();if(!rect.width||!rect.height)return;renderer.setSize(rect.width,rect.height,false);camera.aspect=rect.width/rect.height;camera.updateProjectionMatrix();camera.position.set(focus.x+distance*Math.sin(yaw)*Math.cos(pitch),focus.y+distance*Math.sin(pitch),focus.z+distance*Math.cos(yaw)*Math.cos(pitch));camera.lookAt(focus);
    if(worldMode==='follow'&&routePoints.length){const here=offRoutePosition?point(offRoutePosition.x,offRoutePosition.y,0):routeAt(progress*totalLength),ahead=routeAt(Math.min(totalLength,progress*totalLength+10)),direction=ahead.clone().sub(here).setY(0).normalize();if(direction.length()<.1)direction.set(0,0,-1);camera.position.copy(here).addScaledVector(direction,-65).add(new THREE.Vector3(0,38,0));camera.lookAt(here.clone().add(new THREE.Vector3(0,8,0)));}
    if(worldMode==='surface'){const start=offRoutePosition?point(offRoutePosition.x,offRoutePosition.y,0):routePoints.length?routeAt(progress*totalLength):point(w/2,h/2,0),ahead=routePoints.length?routeAt(Math.min(totalLength,progress*totalLength+10)):point(w/2,h/2-10,0);camera.position.copy(start).add(new THREE.Vector3(0,1.7,0));const direction=ahead.sub(start);if(direction.length()<.1)direction.set(0,0,-1);direction.normalize().applyAxisAngle(new THREE.Vector3(0,1,0),lookYaw);direction.y+=lookPitch;camera.lookAt(camera.position.clone().add(direction.multiplyScalar(20)));}
    for(const child of overlays.children)if(child.userData.route)child.material.color.set(hold?'#77837f':'#ffad74');overlays.visible=worldMode!=='surface';scene.background=new THREE.Color(worldMode==='surface'?'#9c7861':'#11191c');scene.fog=worldMode==='surface'?new THREE.Fog('#9c7861',300,2300):state?.weather?.fogDensity?new THREE.FogExp2('#ac8566',state.weather.fogDensity):null;updateAstronauts();renderer.render(worldMode==='globe'?globeScene:scene,camera);
    if(!hold)navigation?.update(progress,running);document.getElementById('routeProgress').value=Math.round(progress*1000);document.getElementById('journeyDistance').textContent=totalLength?`${Math.round(progress*totalLength)} / ${Math.round(totalLength)} m`:'Sin ruta';const bearing=((yaw*180/Math.PI)%360+360)%360;document.getElementById('cameraBearing').textContent=`${bearing.toFixed(0).padStart(3,'0')}°`;document.getElementById('cameraHeight').textContent=`${Math.round(camera.position.y+(worldMode==='globe'?0:floor))} m`;document.getElementById('compassNeedle').style.transform=`rotate(${-bearing}deg)`;}
  function stop(){navigation?.pause();running=false;document.getElementById('walkRoute').setAttribute('aria-pressed','false');flight=false;transition=null;cancelAnimationFrame(animation);animation=0;document.getElementById('orbitFlight').setAttribute('aria-pressed','false');}
  function animate(now){if(!active){stop();return;}const dt=Math.min((now-lastTime)/1000,.05);lastTime=now;
    if(transition){const t=Math.min(1,(now-transition.start)/1100),ease=t*t*(3-2*t);yaw=THREE.MathUtils.lerp(transition.yaw,transition.to.yaw,ease);pitch=THREE.MathUtils.lerp(transition.pitch,transition.to.pitch,ease);distance=THREE.MathUtils.lerp(transition.distance,transition.to.distance,ease);focus.lerpVectors(transition.focus,new THREE.Vector3(0,30,0),ease);if(t===1)transition=null;}
    if(flight)yaw+=dt*.12;
    if(running){const speed=Number(document.getElementById('walkSpeed').value);walkTime+=dt*speed;progress=Math.min(1,progress+dt*((state?.weather?.speedKmH||2)/3.6)*speed/totalLength);if(progress>=1){running=false;document.getElementById('walkRoute').setAttribute('aria-pressed','false');document.getElementById('journeyStatus').textContent='Llegaste al final de la ruta.';}}
    render();if(transition||flight||running)animation=requestAnimationFrame(animate);else animation=0;
  }
  function preset(name){if(worldMode!=='terrain')setMode('terrain');stop();const presets={overview:{yaw:0,pitch:1.32,distance:span*1.15},flyover:{yaw:-.35,pitch:.38,distance:span*.72},north:{yaw:0,pitch:1.56,distance:span*1.15}};transition={yaw,pitch,distance,focus:focus.clone(),start:performance.now(),to:presets[name]||presets.overview};lastTime=performance.now();animation=requestAnimationFrame(animate);}
  function toggleFlight(){if(flight){stop();return false;}flight=true;lastTime=performance.now();if(!animation)animation=requestAnimationFrame(animate);return true;}
  function reset(){preset('overview');}
  function zoom(factor){if(worldMode==='surface'||worldMode==='follow')return;distance=THREE.MathUtils.clamp(distance/factor,worldMode==='globe'?650:80,worldMode==='globe'?3000:span*4);render();}
  function pan(dx,dy){const k=distance*.001;focus.x+=(-dx*Math.cos(yaw)-dy*Math.sin(yaw))*k;focus.z+=(dx*Math.sin(yaw)-dy*Math.cos(yaw))*k;focus.x=THREE.MathUtils.clamp(focus.x,-span,span);focus.z=THREE.MathUtils.clamp(focus.z,-span,span);}
  const pointers=new Map();let moved=false,start=null;
  canvas.oncontextmenu=e=>e.preventDefault();
  canvas.onpointerdown=e=>{stop();canvas.focus();canvas.setPointerCapture(e.pointerId);pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});start={x:e.clientX,y:e.clientY};moved=false;};
  canvas.onpointermove=e=>{
    const old=pointers.get(e.pointerId);if(!old)return;
    const dx=e.clientX-old.x,dy=e.clientY-old.y;
    if(start&&Math.hypot(e.clientX-start.x,e.clientY-start.y)>5)moved=true;
    if(pointers.size===2){const other=[...pointers.entries()].find(([id])=>id!==e.pointerId)[1];const before=Math.hypot(old.x-other.x,old.y-other.y),after=Math.hypot(e.clientX-other.x,e.clientY-other.y);if(before&&after)zoom(after/before);pan(dx/2,dy/2);moved=true;}
    else if(e.shiftKey||e.buttons===2)pan(dx,dy);
    else if(worldMode==='surface'){lookYaw-=dx*.005;lookPitch=THREE.MathUtils.clamp(lookPitch-dy*.003,-.7,.7);}
    else{yaw-=dx*.007;pitch=THREE.MathUtils.clamp(pitch+dy*.005,worldMode==='globe'?-1.5:.12,Math.PI/2-.01);}
    pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});render();
  };
  canvas.onpointerup=e=>{
    pointers.delete(e.pointerId);
    if(!moved&&e.button===0&&worldMode==='globe'){const r=canvas.getBoundingClientRect();raycaster.setFromCamera(new THREE.Vector2((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1),camera);if(raycaster.intersectObject(site).length||raycaster.intersectObject(ring).length)setMode('terrain');}
    if(!moved&&e.button===0&&worldMode==='terrain'){const r=canvas.getBoundingClientRect();raycaster.setFromCamera(new THREE.Vector2((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1),camera);const hit=raycaster.intersectObject(mesh)[0];if(hit&&onPlace(hit.point.x/m+w/2,hit.point.z/m+h/2))return;}
    if(!moved&&e.button===0&&worldMode==='terrain'&&pickable){const r=canvas.getBoundingClientRect();raycaster.setFromCamera(new THREE.Vector2((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1),camera);const hits=raycaster.intersectObject(pickable);const surface=raycaster.intersectObject(mesh)[0];const hit=hits.find(hit=>!surface||hit.distance<=surface.distance+15);if(hit)onSelect(pickTargets[hit.index]);}
  };
  canvas.onpointercancel=e=>{pointers.delete(e.pointerId);moved=true;};
  canvas.addEventListener('wheel',e=>{stop();e.preventDefault();zoom(Math.exp(-e.deltaY*.0015));},{passive:false});
  canvas.onkeydown=e=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','=','-','0','w','a','s','d'].includes(e.key))return;e.preventDefault();if(worldMode==='surface'&&['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','w','a','s','d'].includes(e.key)){lookYaw+=e.key==='ArrowLeft'?.1:e.key==='ArrowRight'?-.1:0;lookPitch=THREE.MathUtils.clamp(lookPitch+(e.key==='ArrowUp'?.08:e.key==='ArrowDown'?-.08:0),-.7,.7);if(totalLength&&['w','a','s','d'].includes(e.key)){const here=navigationState().position,base=routeAt(Math.min(totalLength,progress*totalLength+10)).sub(routeAt(progress*totalLength));let angle=Math.atan2(base.x,-base.z)+lookYaw;if(e.key==='s')angle+=Math.PI;if(e.key==='a')angle-=Math.PI/2;if(e.key==='d')angle+=Math.PI/2;moveAstronaut(here.x+Math.sin(angle)*4/m,here.y-Math.cos(angle)*4/m);}render();return;}if(e.key==='0')reset();else if(['+','=','-'].includes(e.key))zoom(e.key==='-'?1/1.3:1.3);else if(['w','a','s','d'].includes(e.key))pan(e.key==='a'?30:e.key==='d'?-30:0,e.key==='w'?30:e.key==='s'?-30:0);else{yaw+=e.key==='ArrowLeft'?.15:e.key==='ArrowRight'?-.15:0;pitch=THREE.MathUtils.clamp(pitch+(e.key==='ArrowUp'?.1:e.key==='ArrowDown'?-.1:0),.12,Math.PI/2-.01);render();}};
  new ResizeObserver(()=>{cancelAnimationFrame(frame);frame=requestAnimationFrame(render);}).observe(canvas);
  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();document.getElementById('view2d').click();document.getElementById('viewStatus').textContent='Se perdió el contexto 3D. Puedes continuar en el mapa 2D.';});
  return {update,zoom,reset,preset,toggleFlight,setMode,toggleWalk,seek,navigationState,displace,moveAstronaut,restartRoute(){stop();progress=0;offRoutePosition=null;hold=false;},setHold(value){hold=value;if(value)stop();render();},setActive(value){active=value;if(!value){stop();running=false;document.getElementById('walkRoute').setAttribute('aria-pressed','false');}pointers.clear();if(active&&state)render();}};
}
