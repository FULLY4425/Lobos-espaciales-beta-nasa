import {geoFromGrid} from './ksp-geo.js';
export function globalPixel(data,lat,lon){
 if(!Number.isFinite(lat)||Math.abs(lat)>90||!Number.isFinite(lon))return null;
 const wrap=((lon+180)%360+360)%360-180,x=Math.round((wrap+180)/360*data.width)%data.width,y=Math.max(0,Math.min(data.height-1,Math.round((90-lat)/180*data.height-1)));
 return {x,y};
}
export function globalHeight(data,lat,lon){const p=globalPixel(data,lat,lon);if(!p)return null;const z=data.heights[p.y*data.width+p.x];return z===null?null:z*data.heightScale;}
export function regionFromGlobal(data,lat,lon,{size=17,cell=2000}={}){
 if(!globalPixel(data,lat,lon)||size!==17||cell!==2000)throw Error('Región o coordenadas no válidas.');
 const terrain={width:size,height:size,cellMeters:cell,bodyRadius:data.bodyRadius,body:data.body,center:{lat,lon:((lon+540)%360)-180},projection:'local-azimuthal-equidistant',sourceType:'SCANsat-CSV',elevations:[],water:[]};
 for(let y=0;y<size;y++)for(let x=0;x<size;x++){const p=geoFromGrid(terrain,x,y);terrain.elevations.push(globalHeight(data,p.lat,p.lon));terrain.water.push(false);}
 if(!terrain.elevations.some(Number.isFinite))throw Error('Esta zona no tiene alturas escaneadas. Elige una zona coloreada.');
 return {schema:'ksp-terrain-v1',terrain};
}
export function globePoint(lat,lon,radius=1){const a=lat*Math.PI/180,b=lon*Math.PI/180;return {x:radius*Math.cos(a)*Math.sin(b),y:radius*Math.sin(a),z:radius*Math.cos(a)*Math.cos(b)};}
export function globeGeo(p){const radius=Math.hypot(p.x,p.y,p.z);return {lat:Math.asin(p.y/radius)*180/Math.PI,lon:Math.atan2(p.x,p.z)*180/Math.PI};}
