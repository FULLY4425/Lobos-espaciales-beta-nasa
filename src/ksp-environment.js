export function trainingWeather(t,scenario='clear',windDirection=90){
 if(!['clear','wind','dust','storm'].includes(scenario))throw Error('Escenario no válido.');
 if(!Number.isFinite(windDirection)||windDirection<0||windDirection>=360)throw Error('Dirección de viento no válida.');
 const [speedMS,gustMS,visibilityMeters]={clear:[0,0,20000],wind:[12,20,5000],dust:[8,14,1500],storm:[25,40,200]}[scenario];
 const zones=t&&scenario==='storm'?[{x:(t.width-1)*.65,y:(t.height-1)*.48,radiusCells:Math.max(1,(Math.min(t.width,t.height)-1)*.1)}]:[];
 const blocked=new Set();if(t)for(let y=0;y<t.height;y++)for(let x=0;x<t.width;x++)if(zones.some(z=>Math.hypot(x-z.x,y-z.y)<=z.radiusCells))blocked.add(y*t.width+x);
 return {scenario,wind:{speedMS,gustMS,fromDegrees:windDirection},visibilityMeters,zones,blocked,opacity:{clear:0,wind:.03,dust:.08,storm:.18}[scenario],speedFactor:{clear:1,wind:.85,dust:.75,storm:.5}[scenario]};
}
