const rad=Math.PI/180,clamp=v=>Math.max(-1,Math.min(1,v));
export function localPosition(point,terrain){
 const lat0=terrain.center.lat*rad,lat=point.lat*rad,dl=((point.lon-terrain.center.lon+540)%360-180)*rad;
 const c=Math.acos(clamp(Math.sin(lat0)*Math.sin(lat)+Math.cos(lat0)*Math.cos(lat)*Math.cos(dl)));
 if(c<1e-10)return {x:0,y:0};if(c>Math.PI/2)throw Error('Fuera de la proyección local.');const k=terrain.bodyRadius*c/Math.sin(c);
 return {x:k*Math.cos(lat)*Math.sin(dl),y:-k*(Math.cos(lat0)*Math.sin(lat)-Math.sin(lat0)*Math.cos(lat)*Math.cos(dl))};
}
export function gridPosition(point,terrain){const p=localPosition(point,terrain);return {x:p.x/terrain.cellMeters+(terrain.width-1)/2,y:p.y/terrain.cellMeters+(terrain.height-1)/2};}
export function geoFromGrid(terrain,x,y){const east=(x-(terrain.width-1)/2)*terrain.cellMeters,north=-(y-(terrain.height-1)/2)*terrain.cellMeters,rho=Math.hypot(east,north),lat0=terrain.center.lat*rad,lon0=terrain.center.lon*rad;if(rho<1e-10)return {...terrain.center};const c=rho/terrain.bodyRadius;const lat=Math.asin(clamp(Math.cos(c)*Math.sin(lat0)+north*Math.sin(c)*Math.cos(lat0)/rho));const lon=lon0+Math.atan2(east*Math.sin(c),rho*Math.cos(lat0)*Math.cos(c)-north*Math.sin(lat0)*Math.sin(c));return {lat:lat/rad,lon:((lon/rad+540)%360)-180};}
export function inTerrain(p,t){return Number.isFinite(p.x)&&Number.isFinite(p.y)&&p.x>=0&&p.y>=0&&p.x<=t.width-1&&p.y<=t.height-1;}
