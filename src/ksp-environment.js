export function trainingWeather(t,scenario='clear'){
 if(!['clear','dust','storm'].includes(scenario))throw Error('Escenario no válido.');
 const zones=t&&scenario==='storm'?[{x:(t.width-1)*.65,y:(t.height-1)*.48,radiusCells:Math.max(1,(Math.min(t.width,t.height)-1)*.1)}]:[];
 const blocked=new Set();if(t)for(let y=0;y<t.height;y++)for(let x=0;x<t.width;x++)if(zones.some(z=>Math.hypot(x-z.x,y-z.y)<=z.radiusCells))blocked.add(y*t.width+x);
 return {scenario,zones,blocked,opacity:{clear:0,dust:.08,storm:.18}[scenario],speedFactor:{clear:1,dust:.75,storm:.5}[scenario]};
}
