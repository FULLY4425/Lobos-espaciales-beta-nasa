// Directions describe the computed route; simplified geometry is never used to navigate.
export function distanceText(meters) {
  return meters>=1000?`${(meters/1000).toFixed(1)} kilómetros`:`${Math.max(0,Math.round(meters/5)*5)} metros`;
}
function simplifiedIndices(path,start,end,tolerance) {
  const keep=new Set([start,end]),stack=[[start,end]];
  while(stack.length){const [a,b]=stack.pop();if(b-a<2)continue;const [x,y]=path[a],dx=path[b][0]-x,dy=path[b][1]-y,length=dx*dx+dy*dy;let max=tolerance*tolerance,at=-1;
    for(let i=a+1;i<b;i++){const px=path[i][0]-x,py=path[i][1]-y,t=length?Math.max(0,Math.min(1,(px*dx+py*dy)/length)):0,d=(px-t*dx)**2+(py-t*dy)**2;if(d>max){max=d;at=i;}}
    if(at!==-1){keep.add(at);stack.push([a,at],[at,b]);}
  }
  return [...keep].sort((a,b)=>a-b);
}
function turn(a,b,c) {
  const ax=b[0]-a[0],ay=b[1]-a[1],bx=c[0]-b[0],by=c[1]-b[1];
  const angle=Math.atan2(ax*by-ay*bx,ax*bx+ay*by)*180/Math.PI,amount=Math.abs(angle);
  if(amount<30)return null;
  if(amount>155)return {kind:'uturn',icon:'↶',text:'Da media vuelta'};
  const right=angle>0,side=right?'derecha':'izquierda';
  return {kind:right?'right':'left',icon:right?'↱':'↰',text:amount<60?`Gira ligeramente a la ${side}`:amount>120?`Gira pronunciadamente a la ${side}`:`Gira a la ${side}`};
}
export function buildDirections(path,terrain,stops=[]) {
  if(path.length<2)return {distance:0,steps:[]};
  const lengths=[0],m=terrain.cellMeters;
  for(let i=1;i<path.length;i++){const a=path[i-1],b=path[i],az=terrain.elevations[a[1]*terrain.width+a[0]],bz=terrain.elevations[b[1]*terrain.width+b[0]];lengths.push(lengths.at(-1)+Math.hypot((b[0]-a[0])*m,(b[1]-a[1])*m,bz-az));}
  const distance=lengths.at(-1),anchors=[0],waypoints=new Map();let cursor=0;
  for(const stop of stops.slice(1,-1)){const [x,y]=Array.isArray(stop.grid)?stop.grid:[Math.round((stop.lon-terrain.west)/terrain.degreeStep),Math.round((terrain.north-stop.lat)/terrain.degreeStep)];let found=-1;for(let i=cursor;i<path.length;i++)if(path[i][0]===x&&path[i][1]===y){found=i;break;}if(found>=0){cursor=found;anchors.push(found);waypoints.set(found,[...(waypoints.get(found)||[]),stop.name]);}}
  anchors.push(path.length-1);
  const indices=new Set();for(let i=1;i<anchors.length;i++)for(const index of simplifiedIndices(path,anchors[i-1],anchors[i],1.05))indices.add(index);
  const simple=[...indices].sort((a,b)=>a-b),steps=[{kind:'depart',icon:'↑',text:'Inicia el recorrido y sigue la ruta marcada',distance:0,index:0}];
  for(let i=1;i<simple.length-1;i++){const index=simple[i],instruction=turn(path[simple[i-1]],path[index],path[simple[i+1]]),names=waypoints.get(index);if(names){steps.push({kind:'waypoint',icon:'⚑',text:`Llegaste a ${names.join(' y ')}${instruction?`. ${instruction.text}`:'. Continúa por la ruta marcada'}`,distance:lengths[index],index});}else if(instruction)steps.push({...instruction,distance:lengths[index],index});}
  steps.push({kind:'arrive',icon:'⚑',text:`Llegaste a ${stops.at(-1)?.name||'tu destino'}. Fin del recorrido`,distance,index:path.length-1});
  return {distance,steps};
}
