import * as THREE from './vendor/three.module.js';
import {slopeAt} from './route.js';

// Coordinates are meters: east = X, height = Y, south = Z. No vertical exaggeration.
export function createTerrain3D(canvas, terrain, onSelect) {
  const renderer=new THREE.WebGLRenderer({canvas,antialias:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));
  renderer.setClearColor('#11191c');
  const scene=new THREE.Scene(), camera=new THREE.PerspectiveCamera(45,1,1,30000);
  const {width:w,height:h,cellMeters:m,elevations:z}=terrain;
  const valid=z.filter(v=>v!==null),floor=Math.min(...valid),ceiling=Math.max(...valid),span=Math.max(w,h)*m;
  const focus=new THREE.Vector3(0,30,0);
  let yaw=0,pitch=.85,distance=span*1.25,active=false,frame=0,state;
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
  let pickable=null,pickTargets=[];
  function point(x,y,lift=4){const ix=Math.max(0,Math.min(w-1,Math.round(x))),iy=Math.max(0,Math.min(h-1,Math.round(y)));return new THREE.Vector3((x-w/2)*m,(z[iy*w+ix]??floor)-floor+lift,(y-h/2)*m);}
  function targetPoint(p,lift){return point((p.lon-terrain.west)/terrain.degreeStep,(terrain.north-p.lat)/terrain.degreeStep,lift);}
  function clearOverlays(){for(const child of [...overlays.children]){child.geometry.dispose();child.material.dispose();overlays.remove(child);}}
  function update(next){
    state=next;
    const ctx=textureCanvas.getContext('2d');ctx.fillStyle='#5d5144';ctx.fillRect(0,0,textureCanvas.width,textureCanvas.height);
    if(next.satellite&&next.image.complete&&next.image.naturalWidth)ctx.drawImage(next.image,0,0,textureCanvas.width,textureCanvas.height);
    else for(let y=0;y<h;y++)for(let x=0;x<w;x++){const v=z[y*w+x];if(v===null)continue;const n=(v-floor)/(ceiling-floor||1);ctx.fillStyle=next.relief?`hsl(28 25% ${28+n*35}%)`:'#766657';ctx.fillRect(x*12,y*12,12,12);}
    if(next.slopes)for(let y=0;y<h;y++)for(let x=0;x<w;x++){const s=slopeAt(terrain,x,y);ctx.fillStyle=s>next.maxSlope?'#ef614b99':s>10?'#e8c26444':'#74b9a422';ctx.fillRect(x*12,y*12,12,12);}
    texture.needsUpdate=true;clearOverlays();pickable=null;
    if(next.science){pickTargets=next.targets;const g=new THREE.BufferGeometry().setFromPoints(pickTargets.map(p=>targetPoint(p,5)));pickable=new THREE.Points(g,new THREE.PointsMaterial({color:'#b5e5d2',size:4,sizeAttenuation:false,depthTest:true}));overlays.add(pickable);}
    if(next.path.length){const g=new THREE.BufferGeometry().setFromPoints(next.path.map(([x,y])=>point(x,y,5)));overlays.add(new THREE.Line(g,new THREE.LineBasicMaterial({color:'#ffad74'})));}
    for(const p of next.stops){const marker=new THREE.Mesh(new THREE.SphereGeometry(7,12,8),new THREE.MeshBasicMaterial({color:'#ff945c'}));marker.position.copy(targetPoint(p,8));overlays.add(marker);}
    if(next.selected){const marker=new THREE.Mesh(new THREE.SphereGeometry(11,12,8),new THREE.MeshBasicMaterial({color:'white',wireframe:true}));marker.position.copy(targetPoint(next.selected,8));overlays.add(marker);}
    render();
  }
  function render(){if(!active)return;const rect=canvas.getBoundingClientRect();if(!rect.width||!rect.height)return;renderer.setSize(rect.width,rect.height,false);camera.aspect=rect.width/rect.height;camera.updateProjectionMatrix();camera.position.set(focus.x+distance*Math.sin(yaw)*Math.cos(pitch),focus.y+distance*Math.sin(pitch),focus.z+distance*Math.cos(yaw)*Math.cos(pitch));camera.lookAt(focus);renderer.render(scene,camera);}
  function reset(){yaw=0;pitch=.85;distance=span*1.25;focus.set(0,30,0);render();}
  function zoom(factor){distance=THREE.MathUtils.clamp(distance/factor,80,span*4);render();}
  function pan(dx,dy){const k=distance*.001;focus.x+=(-dx*Math.cos(yaw)-dy*Math.sin(yaw))*k;focus.z+=(dx*Math.sin(yaw)-dy*Math.cos(yaw))*k;focus.x=THREE.MathUtils.clamp(focus.x,-span,span);focus.z=THREE.MathUtils.clamp(focus.z,-span,span);}
  const pointers=new Map();let moved=false,start=null;
  canvas.oncontextmenu=e=>e.preventDefault();
  canvas.onpointerdown=e=>{canvas.focus();canvas.setPointerCapture(e.pointerId);pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});start={x:e.clientX,y:e.clientY};moved=false;};
  canvas.onpointermove=e=>{
    const old=pointers.get(e.pointerId);if(!old)return;
    const dx=e.clientX-old.x,dy=e.clientY-old.y;
    if(start&&Math.hypot(e.clientX-start.x,e.clientY-start.y)>5)moved=true;
    if(pointers.size===2){const other=[...pointers.entries()].find(([id])=>id!==e.pointerId)[1];const before=Math.hypot(old.x-other.x,old.y-other.y),after=Math.hypot(e.clientX-other.x,e.clientY-other.y);if(before&&after)zoom(after/before);pan(dx/2,dy/2);moved=true;}
    else if(e.shiftKey||e.buttons===2)pan(dx,dy);
    else{yaw-=dx*.007;pitch=THREE.MathUtils.clamp(pitch+dy*.005,.12,Math.PI/2-.01);}
    pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});render();
  };
  canvas.onpointerup=e=>{
    pointers.delete(e.pointerId);
    if(!moved&&e.button===0&&pickable){const r=canvas.getBoundingClientRect();raycaster.setFromCamera(new THREE.Vector2((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1),camera);const hits=raycaster.intersectObject(pickable);const surface=raycaster.intersectObject(mesh)[0];const hit=hits.find(hit=>!surface||hit.distance<=surface.distance+15);if(hit)onSelect(pickTargets[hit.index]);}
  };
  canvas.onpointercancel=e=>{pointers.delete(e.pointerId);moved=true;};
  canvas.addEventListener('wheel',e=>{e.preventDefault();zoom(Math.exp(-e.deltaY*.0015));},{passive:false});
  canvas.onkeydown=e=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','=','-','0','w','a','s','d'].includes(e.key))return;e.preventDefault();if(e.key==='0')reset();else if(['+','=','-'].includes(e.key))zoom(e.key==='-'?1/1.3:1.3);else if(['w','a','s','d'].includes(e.key))pan(e.key==='a'?30:e.key==='d'?-30:0,e.key==='w'?30:e.key==='s'?-30:0);else{yaw+=e.key==='ArrowLeft'?.15:e.key==='ArrowRight'?-.15:0;pitch=THREE.MathUtils.clamp(pitch+(e.key==='ArrowUp'?.1:e.key==='ArrowDown'?-.1:0),.12,Math.PI/2-.01);render();}};
  new ResizeObserver(()=>{cancelAnimationFrame(frame);frame=requestAnimationFrame(render);}).observe(canvas);
  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();document.getElementById('view2d').click();document.getElementById('viewStatus').textContent='Se perdió el contexto 3D. Puedes continuar en el mapa 2D.';});
  return {update,zoom,reset,setActive(value){active=value;pointers.clear();if(active&&state)render();}};
}
