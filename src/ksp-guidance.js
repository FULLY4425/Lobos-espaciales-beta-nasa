import {slopeAt} from './route.js';

// Same cell, edge-grade and diagonal-corner rules as Python A*. No inferred obstacles.
export function reachableTerrain(t,origin,maxSlope,avoidWater=true,blocked=new Set()){
 const count=t.width*t.height,pass=new Uint8Array(count),reachable=new Uint8Array(count),slopes=new Float64Array(count);
 for(let y=0;y<t.height;y++)for(let x=0;x<t.width;x++){const i=y*t.width+x;slopes[i]=slopeAt(t,x,y);pass[i]=Number.isFinite(t.elevations[i])&&slopes[i]<=maxSlope&&!(avoidWater&&t.water[i])&&!blocked.has(i)?1:0;}
 const x=Math.round(origin.x),y=Math.round(origin.y),queue=[];if(x>=0&&y>=0&&x<t.width&&y<t.height&&pass[y*t.width+x]){queue.push(y*t.width+x);reachable[queue[0]]=1;}
 for(let at=0;at<queue.length;at++){const i=queue[at],x=i%t.width,y=Math.floor(i/t.width);for(const [dx,dy] of [[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]]){const a=x+dx,b=y+dy,j=b*t.width+a;if(a<0||b<0||a>=t.width||b>=t.height||!pass[j]||reachable[j])continue;if(dx&&dy&&(!pass[y*t.width+a]||!pass[b*t.width+x]))continue;const grade=Math.atan(Math.abs(t.elevations[j]-t.elevations[i])/(t.cellMeters*Math.hypot(dx,dy)))*180/Math.PI;if(grade>maxSlope)continue;reachable[j]=1;queue.push(j);}}
 return {pass,reachable,slopes,count:queue.length};
}
export function edgeDistance(t,grid){return Math.min(grid.x,grid.y,t.width-1-grid.x,t.height-1-grid.y)*t.cellMeters;}
export function drivingAdvice({speed,distance,turnDistance=Infinity,edge=Infinity,advisorySpeed=5,reactionSeconds=6}){
 const lookAhead=Math.max(30,Math.max(0,speed)*reactionSeconds),alerts=[];
 if(edge<=lookAhead)alerts.push({code:'edge',text:edge<0?'Fuera de cobertura. Carga otra región.':`Borde del mapa a ${Math.round(edge)} m. Prepara otra región.`,priority:1});
 if(speed>advisorySpeed&&(distance<=lookAhead||turnDistance<=lookAhead))alerts.unshift({code:'speed',text:`Reduce velocidad: ${speed.toFixed(1)} m/s; ${distance<=lookAhead?'destino':'giro'} próximo.`,priority:2});
 return {lookAhead,alerts};
}
// Require physical proximity AND a 3-second stop. Estimated driving speed is not a brake model.
export function arrivalState(previous,{distance,speed,now,eligible=true,radius=8}){
 const state={closest:Infinity,stopSince:null,arrived:false,passed:false,...previous};
 if(state.arrived&&distance>radius*2){state.arrived=false;state.stopSince=null;state.closest=distance;}
 if(eligible){
  if(distance<state.closest-3)state.passed=false;
  state.closest=Math.min(state.closest,distance);
  if(distance<=radius&&speed<=.5){state.stopSince??=now;if(now-state.stopSince>=3000)state.arrived=true;}
  else state.stopSince=null;
  if(!state.arrived&&state.closest<=Math.max(30,speed*6)&&distance>state.closest+Math.max(10,radius)&&speed>.5)state.passed=true;
 }else state.stopSince=null;
 return state;
}
export function cleanError(message){return String(message||'Error desconocido').trim().replace(/[.\s]+$/,'');}
export function surfaceContext(t,sample,grid){
 const outside=!grid||!Number.isFinite(grid.x)||!Number.isFinite(grid.y)||grid.x<0||grid.y<0||grid.x>t.width-1||grid.y>t.height-1;
 const airborne=['flying','sub_orbital','orbiting','escaping'].includes(sample.flight?.situation)||sample.surfaceAltitude>Math.max(30,Math.min(100,t.cellMeters*2));
 return {usable:!outside&&!airborne,outside,airborne,message:airborne?`Vehículo en vuelo; esta guía es de superficie${outside?' y su posición queda fuera de la región':''}. Selecciona un rover en la región o carga cobertura al aterrizar.`:outside?'Vehículo fuera de la región muestreada. Carga una región que incluya el vehículo y sus destinos.':'Posición dentro de la región; guía de superficie disponible.'};
}

// Meter tolerance is independent of terrain sampling; persistence/cooldown avoid reroute storms.
export function deviationState(previous,{crossTrack,now,tolerance=75}){
 const state={outsideSince:null,lastReplanAt:-Infinity,...previous,shouldReplan:false};
 const limit=Math.max(15,Math.min(250,Number(tolerance)||75));
 if(!Number.isFinite(crossTrack)||crossTrack<=limit){state.outsideSince=null;return state;}
 state.outsideSince??=now;
 if(now-state.outsideSince>=1500&&now-state.lastReplanAt>=10000){state.shouldReplan=true;state.lastReplanAt=now;state.outsideSince=null;}
 return state;
}
export function nearestReachableCell(t,reach,target,origin){
 let best=null,distance=Infinity;
 for(let i=0;i<reach.reachable.length;i++)if(reach.reachable[i]){const x=i%t.width,y=Math.floor(i/t.width);if(Math.hypot(x-origin.x,y-origin.y)<.75)continue;const d=Math.hypot(x-target.x,y-target.y);if(d<distance){best={x,y};distance=d;}}
 return best;
}
