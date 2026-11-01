// Map KSP motion onto a local mission using an explicit calibration anchor.
// Duna and Mars coordinates are never treated as interchangeable.
export function projectKsp(sample,anchor,headingOffset=0) {
  if(!anchor||sample.body!==anchor.body||sample.vesselId!==anchor.vesselId)return null;
  for(const key of ['latitude','longitude','bodyRadius'])if(!Number.isFinite(sample[key])||!Number.isFinite(anchor[key]))return null;
  if(sample.bodyRadius<=0)return null;
  const rad=Math.PI/180,dlon=((sample.longitude-anchor.longitude+540)%360)-180;
  const north=(sample.latitude-anchor.latitude)*rad*sample.bodyRadius;
  const east=dlon*rad*sample.bodyRadius*Math.cos(anchor.latitude*rad),angle=headingOffset*rad;
  return {x:east*Math.cos(angle)-north*Math.sin(angle),y:-(east*Math.sin(angle)+north*Math.cos(angle))};
}
export function nearestOnRoute(position,path,terrain) {
  if(!position||path.length<2)return null;
  const m=terrain.cellMeters,origin=path[0];let total=0,best={crossTrack:Infinity,distance:0};
  for(let i=1;i<path.length;i++){
    const a=path[i-1],b=path[i],x=(a[0]-origin[0])*m,y=(a[1]-origin[1])*m,dx=(b[0]-a[0])*m,dy=(b[1]-a[1])*m,sq=dx*dx+dy*dy;
    const t=sq?Math.max(0,Math.min(1,((position.x-x)*dx+(position.y-y)*dy)/sq)):0;
    const error=Math.hypot(position.x-x-t*dx,position.y-y-t*dy),az=terrain.elevations[a[1]*terrain.width+a[0]],bz=terrain.elevations[b[1]*terrain.width+b[0]],length=Math.hypot(dx,dy,bz-az);
    if(error<best.crossTrack)best={crossTrack:error,distance:total+t*length};total+=length;
  }
  return {...best,progress:total?best.distance/total:0};
}
