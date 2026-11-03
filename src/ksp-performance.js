const sizes=new WeakMap();
export function resizeRenderer(renderer,camera,width,height){
 const ratio=renderer.getPixelRatio?.()??1,previous=sizes.get(renderer);
 if(previous?.width===width&&previous?.height===height&&previous?.ratio===ratio)return false;
 renderer.setSize(width,height,false);camera.aspect=width/height;camera.updateProjectionMatrix();sizes.set(renderer,{width,height,ratio});return true;
}
export function recordTiming(stats,kind,ms){
 if(!Number.isFinite(ms)||ms<0)return;
 const value=stats[kind]??={count:0,totalMs:0,maxMs:0,over50Ms:0,recent:[]};
 value.count++;value.totalMs+=Math.round(ms*100)/100;value.maxMs=Math.max(value.maxMs,Math.round(ms*100)/100);if(ms>50)value.over50Ms++;
 value.recent.push(ms);if(value.recent.length>120)value.recent.shift();
 value.meanMs=Math.round(value.totalMs/value.count*100)/100;const sorted=[...value.recent].sort((a,b)=>a-b);value.p95RecentMs=Math.round(sorted[Math.ceil(sorted.length*.95)-1]*100)/100;
}
export function timingSnapshot(stats){return Object.fromEntries(Object.entries(stats).map(([key,{recent,...value}])=>[key,value]));}
