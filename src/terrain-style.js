export function elevationRange(t){const z=t.elevations.filter(Number.isFinite);return {min:Math.min(...z),max:Math.max(...z)};}
const palette=[[40,73,79],[66,113,108],[137,149,105],[190,150,105],[227,194,148],[248,240,219]];
export function elevationRGB(z,min,max){const n=Math.max(0,Math.min(1,(z-min)/(max-min||1)))*(palette.length-1),i=Math.min(palette.length-2,Math.floor(n)),f=n-i;return palette[i].map((c,j)=>Math.round(c+(palette[i+1][j]-c)*f));}
export function contourSegments(t,requestedStep=25){
 const {min,max}=elevationRange(t),step=Math.max(Number(requestedStep)||25,(max-min)/60),segments=[];
 for(let y=0;y<t.height-1;y++)for(let x=0;x<t.width-1;x++)for(const tri of [[[x,y],[x+1,y],[x,y+1]],[[x+1,y],[x+1,y+1],[x,y+1]]]){
  const points=tri.map(([x,y])=>({x,y,z:t.elevations[y*t.width+x]}));if(points.some(p=>!Number.isFinite(p.z)))continue;
  const low=Math.min(...points.map(p=>p.z)),high=Math.max(...points.map(p=>p.z));
  for(let z=Math.ceil(low/step)*step;z<high;z+=step){const hits=[];for(let i=0;i<3;i++){const a=points[i],b=points[(i+1)%3];if((a.z<=z&&b.z>z)||(b.z<=z&&a.z>z)){const f=(z-a.z)/(b.z-a.z);hits.push({x:a.x+(b.x-a.x)*f,y:a.y+(b.y-a.y)*f,z});}}if(hits.length===2)segments.push(hits);}
 }
 return {segments,step};
}
export function drawContours(ctx,t,view,requestedStep=25){const result=contourSegments(t,requestedStep);ctx.save();ctx.strokeStyle='#f5e4bfbb';ctx.lineWidth=1;ctx.beginPath();for(const [a,b] of result.segments){ctx.moveTo(view.x+a.x*view.scale,view.y+a.y*view.scale);ctx.lineTo(view.x+b.x*view.scale,view.y+b.y*view.scale);}ctx.stroke();ctx.restore();return result.step;}
