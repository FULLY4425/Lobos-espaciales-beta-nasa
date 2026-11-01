export function waypointDistances(mission,terrain){
 const lengths=[0],path=mission.gridPath,m=terrain.cellMeters;
 for(let i=1;i<path.length;i++){const a=path[i-1],b=path[i];lengths.push(lengths.at(-1)+Math.hypot((b[0]-a[0])*m,(b[1]-a[1])*m,terrain.elevations[b[1]*terrain.width+b[0]]-terrain.elevations[a[1]*terrain.width+a[0]]));}
 if(Array.isArray(mission.stopPathIndices)&&mission.stopPathIndices.length===mission.stops.length)return mission.stopPathIndices.map(i=>lengths[i]||0);
 let cursor=0;return mission.stops.map(stop=>{const x=Math.round((stop.lon-terrain.west)/terrain.degreeStep),y=Math.round((terrain.north-stop.lat)/terrain.degreeStep);for(let i=cursor;i<path.length;i++)if(path[i][0]===x&&path[i][1]===y){cursor=i;break;}return lengths[cursor]||0;});
}
export function remainingStops(mission,terrain,progress){
 const distances=waypointDistances(mission,terrain),traveled=(distances.at(-1)||0)*Math.max(0,Math.min(1,progress));
 return mission.stops.filter((_,i)=>i>0&&(i===mission.stops.length-1||distances[i]>=traveled-3));
}
export function replanPayload(mission,terrain,position,progress,weather,reason='deviation'){
 if(!position||!Number.isFinite(position.x)||!Number.isFinite(position.y)||position.x<0||position.y<0||position.x>terrain.width-1||position.y>terrain.height-1)throw Error('La posición actual está fuera del terreno disponible. Guía en pausa.');
 const remaining=remainingStops(mission,terrain,progress),names=new Set(remaining.map(p=>p.name));let name='Posición actual';while(names.has(name))name+=' ·';
 return {stops:[{type:'custom',name,lat:terrain.north-position.y*terrain.degreeStep,lon:terrain.west+position.x*terrain.degreeStep},...remaining.map(p=>p.type==='custom'?{type:'custom',name:p.name,lat:p.lat,lon:p.lon}:p.name)],maxSlopeDegrees:mission.maxSlopeDegrees,weather,replanReason:reason};
}
export async function replanMission(mission,terrain,position,progress,weather,reason='deviation',signal){
 const payload=replanPayload(mission,terrain,position,progress,weather,reason),controller=new AbortController(),abort=()=>controller.abort();signal?.addEventListener('abort',abort,{once:true});if(signal?.aborted)controller.abort();const timer=setTimeout(abort,8000);
 try{const response=await fetch('/api/plan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),signal:controller.signal});const data=await response.json();if(!response.ok)throw Error(data.error||'No se pudo recalcular.');return data;}finally{clearTimeout(timer);signal?.removeEventListener('abort',abort);}
}
export function scenarioEnvironment(config,key,terrain){const preset=config.scenarios[key];return {...preset,weather:key,sourceType:'synthetic',notice:config.notice,restrictions:preset.zones.map(z=>({name:z.name,lon:terrain.west+z.xFraction*(terrain.width-1)*terrain.degreeStep,lat:terrain.north-z.yFraction*(terrain.height-1)*terrain.degreeStep,radiusMeters:z.radiusCells*terrain.cellMeters}))};}
export function positionAtProgress(path,terrain,progress){
 const m=terrain.cellMeters,lengths=[0];for(let i=1;i<path.length;i++){const a=path[i-1],b=path[i];lengths.push(lengths.at(-1)+Math.hypot((b[0]-a[0])*m,(b[1]-a[1])*m,terrain.elevations[b[1]*terrain.width+b[0]]-terrain.elevations[a[1]*terrain.width+a[0]]));}
 if(path.length<2)return {x:path[0]?.[0]||0,y:path[0]?.[1]||0};const distance=Math.max(0,Math.min(1,progress))*lengths.at(-1);let i=1;while(i<lengths.length-1&&lengths[i]<distance)i++;const f=(distance-lengths[i-1])/(lengths[i]-lengths[i-1]||1);return {x:path[i-1][0]+(path[i][0]-path[i-1][0])*f,y:path[i-1][1]+(path[i][1]-path[i-1][1])*f};
}
