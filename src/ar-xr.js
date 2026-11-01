import * as THREE from './vendor/three.module.js';

export async function startTabletopAR(canvas,overlay,terrain,path,options={}) {
  const session=await navigator.xr.requestSession('immersive-ar',{requiredFeatures:['hit-test'],optionalFeatures:['dom-overlay'],domOverlay:{root:overlay}});
  let renderer,hitSource,ended=false;
  const disposables=[],listeners=[];
  try {
    renderer=new THREE.WebGLRenderer({canvas,alpha:true,antialias:false,powerPreference:'low-power'});
    renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.5));renderer.setClearColor(0x000000,0);renderer.xr.enabled=true;renderer.xr.setReferenceSpaceType('local');
    const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(),root=new THREE.Group();root.visible=false;scene.add(root);
    const {width:w,height:h,cellMeters:m,elevations:z}=terrain,minimum=Math.min(...z.filter(v=>v!==null));
    const positions=[],uvs=[],indices=[];
    for(let y=0;y<h;y++)for(let x=0;x<w;x++){positions.push((x-w/2)*m,(z[y*w+x]??minimum)-minimum,(y-h/2)*m);uvs.push(x/w,1-y/h);}
    for(let y=0;y<h-1;y++)for(let x=0;x<w-1;x++){const a=y*w+x,b=a+1,c=a+w,d=c+1;if([a,c,b].every(i=>z[i]!==null))indices.push(a,c,b);if([b,c,d].every(i=>z[i]!==null))indices.push(b,c,d);}
    const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));geometry.setAttribute('uv',new THREE.Float32BufferAttribute(uvs,2));geometry.setIndex(indices);disposables.push(geometry);
    const texture=new THREE.TextureLoader().load('/public/imagery/glen-torridon-hirise.webp');texture.colorSpace=THREE.SRGBColorSpace;disposables.push(texture);
    const material=new THREE.MeshBasicMaterial({map:texture,side:THREE.DoubleSide});disposables.push(material);root.add(new THREE.Mesh(geometry,material));
    let routeLine=null;
    if(path.length){const routeGeometry=new THREE.BufferGeometry().setFromPoints(path.map(([x,y])=>new THREE.Vector3((x-w/2)*m,(z[y*w+x]??minimum)-minimum+3,(y-h/2)*m)));const routeMaterial=new THREE.LineBasicMaterial({color:'#aaffcc'});disposables.push(routeGeometry,routeMaterial);routeLine=new THREE.Line(routeGeometry,routeMaterial);root.add(routeLine);}
    let walker=null,routePoints=[],routeDistances=[0];
    if(path.length>1){routePoints=path.map(([x,y])=>new THREE.Vector3((x-w/2)*m,(z[y*w+x]??minimum)-minimum+5,(y-h/2)*m));for(let i=1;i<routePoints.length;i++)routeDistances.push(routeDistances.at(-1)+routePoints[i].distanceTo(routePoints[i-1]));const g=new THREE.SphereGeometry(7,8,6),mat=new THREE.MeshBasicMaterial({color:'#ffb379'});disposables.push(g,mat);walker=new THREE.Mesh(g,mat);root.add(walker);}
    const reticleGeometry=new THREE.RingGeometry(.07,.09,32).rotateX(-Math.PI/2),reticleMaterial=new THREE.MeshBasicMaterial({color:'#b4ffd4',side:THREE.DoubleSide});disposables.push(reticleGeometry,reticleMaterial);const reticle=new THREE.Mesh(reticleGeometry,reticleMaterial);reticle.matrixAutoUpdate=false;reticle.visible=false;scene.add(reticle);
    function size(){root.scale.setScalar(Number(options.size?.()||.5)/(w*m));}size();
    const select=()=>{if(!reticle.visible)return;root.position.setFromMatrixPosition(reticle.matrix);root.quaternion.setFromRotationMatrix(reticle.matrix);size();root.visible=true;reticle.visible=false;options.onStatus?.('Maqueta colocada. Usa Recolocar para cambiar de superficie.');};session.addEventListener('select',select);listeners.push(()=>session.removeEventListener('select',select));
    const beforeSelect=e=>{if(e.target.closest?.('button,input,select,a'))e.preventDefault();};overlay.addEventListener('beforexrselect',beforeSelect);listeners.push(()=>overlay.removeEventListener('beforexrselect',beforeSelect));
    const finish=()=>{if(ended)return;ended=true;hitSource?.cancel();renderer.setAnimationLoop(null);for(const dispose of listeners)dispose();for(const item of disposables)item.dispose();renderer.dispose();canvas.hidden=true;options.onEnd?.();};session.addEventListener('end',finish,{once:true});
    await renderer.xr.setSession(session);
    const viewer=await session.requestReferenceSpace('viewer');hitSource=await session.requestHitTestSource({space:viewer});
    canvas.hidden=false;
    renderer.setAnimationLoop((_time,frame)=>{if(!frame||ended)return;if(!root.visible){const hits=frame.getHitTestResults(hitSource);const pose=hits[0]?.getPose(renderer.xr.getReferenceSpace());reticle.visible=!!pose;if(pose)reticle.matrix.fromArray(pose.transform.matrix);}size();if(walker){const distance=Number(options.progress?.()||0)*routeDistances.at(-1);let i=1;while(i<routeDistances.length-1&&routeDistances[i]<distance)i++;walker.position.copy(routePoints[i-1]).lerp(routePoints[i],(distance-routeDistances[i-1])/(routeDistances[i]-routeDistances[i-1]||1));}renderer.render(scene,camera);});
    options.onStatus?.('Busca una superficie plana y toca el círculo para colocar la maqueta.');
    return {end:()=>session.end(),setPath(next){if(routeLine){root.remove(routeLine);routeLine.geometry.dispose();routeLine.material.dispose();}if(walker){root.remove(walker);walker.geometry.dispose();walker.material.dispose();}walker=null;routeLine=null;if(next.length<2){routePoints=[];routeDistances=[0];return;}routePoints=next.map(([x,y])=>new THREE.Vector3((x-w/2)*m,(z[y*w+x]??minimum)-minimum+5,(y-h/2)*m));routeDistances=[0];for(let i=1;i<routePoints.length;i++)routeDistances.push(routeDistances.at(-1)+routePoints[i].distanceTo(routePoints[i-1]));const g=new THREE.BufferGeometry().setFromPoints(routePoints),mat=new THREE.LineBasicMaterial({color:'#aaffcc'}),wg=new THREE.SphereGeometry(7,8,6),wm=new THREE.MeshBasicMaterial({color:'#ffb379'});disposables.push(g,mat,wg,wm);routeLine=new THREE.Line(g,mat);root.add(routeLine);walker=new THREE.Mesh(wg,wm);root.add(walker);},reposition(){root.visible=false;options.onStatus?.('Busca la nueva superficie y toca el círculo.');}};
  } catch(error){hitSource?.cancel();renderer?.setAnimationLoop(null);for(const item of disposables)item.dispose();renderer?.dispose();await session.end().catch(()=>{});throw error;}
}
