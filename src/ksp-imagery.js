import {geoFromGrid} from './ksp-geo.js';
import {elevationRange,elevationRGB} from './terrain-style.js';
export function validateTexture(meta,t){
 if(!meta||meta.schema!=='ksp-texture-v1'||meta.body!==t.body||meta.bodyRadius!==t.bodyRadius)throw Error('La textura necesita metadatos del mismo cuerpo y radio que el mapa.');
 if(typeof meta.credit!=='string'||!meta.credit.trim())throw Error('Indica la procedencia de la textura en credit.');
 if(meta.projection==='local-grid'){
  const g=meta.grid;if(!g||g.width!==t.width||g.height!==t.height||g.cellMeters!==t.cellMeters||Math.abs(g.center?.lat-t.center.lat)>1e-8||Math.abs(g.center?.lon-t.center.lon)>1e-8||!Number.isFinite(g.center?.lat)||!Number.isFinite(g.center?.lon))throw Error('La textura local no coincide con la región.');
 }else if(meta.projection==='equirectangular'){
  if(![meta.west,meta.east,meta.north,meta.south].every(Number.isFinite)||meta.east<=meta.west||meta.east-meta.west>360||meta.north<=meta.south||meta.north>90||meta.south< -90)throw Error('Límites geográficos no válidos.');
 }else throw Error('Usa proyección equirectangular o local-grid.');
 return meta;
}
export function texturePixel(meta,geo,width,height){
 const span=meta.east-meta.west;let lon=geo.lon;
 if(lon<meta.west||lon>meta.east)lon=meta.west+((lon-meta.west)%360+360)%360;
 const u=(lon-meta.west)/span,v=(meta.north-geo.lat)/(meta.north-meta.south);
 if(u<0||u>1||v<0||v>1)return null;
 const x=Math.max(0,Math.min(width-1,Math.round(u*(meta.pixelConvention==='scansat'?width:width-1)))),y=Math.max(0,Math.min(height-1,Math.round(v*(meta.pixelConvention==='scansat'?height:height-1)-(meta.pixelConvention==='scansat'?1:0))));if(meta.coverage){if(meta.coverage.width!==width||meta.coverage.height!==height)throw Error('La máscara no coincide con la imagen.');const ranges=meta.coverage.rows?.[String(y)];if(!Array.isArray(ranges)||!ranges.some(([a,b])=>x>=a&&x<=b))return null;}return {x,y};
}
export async function projectTexture(image,meta,t,size=512){
 validateTexture(meta,t);const source=document.createElement('canvas');source.width=image.naturalWidth;source.height=image.naturalHeight;if(!source.width||source.width*source.height>20e6)throw Error('La textura admite hasta 20 millones de píxeles.');
 const sc=source.getContext('2d',{willReadFrequently:true});sc.drawImage(image,0,0);const pixels=sc.getImageData(0,0,source.width,source.height).data,output=document.createElement('canvas');output.width=output.height=size;const ctx=output.getContext('2d'),data=ctx.createImageData(size,size),range=elevationRange(t);let covered=0,total=0;
 for(let y=0;y<size;y++){
  for(let x=0;x<size;x++){const gx=x/(size-1)*(t.width-1),gy=y/(size-1)*(t.height-1),ix=Math.min(t.width-2,Math.floor(gx)),iy=Math.min(t.height-2,Math.floor(gy)),fx=gx-ix,fy=gy-iy,a=iy*t.width+ix,indices=fx+fy<=1?[a,a+1,a+t.width]:[a+1,a+t.width,a+t.width+1];if(indices.some(i=>t.elevations[i]===null))continue;
   const pixel=meta.projection==='local-grid'?{x:Math.round(x/(size-1)*(source.width-1)),y:Math.round(y/(size-1)*(source.height-1))}:texturePixel(meta,geoFromGrid(t,gx,gy),source.width,source.height);const to=(y*size+x)*4;total++;if(!pixel){const z=t.elevations[Math.round(gy)*t.width+Math.round(gx)];data.data.set([...elevationRGB(z??range.min,range.min,range.max),255],to);continue;}const from=(pixel.y*source.width+pixel.x)*4;data.data.set(pixels.subarray(from,from+4),to);covered++;
  }
  if(y%32===31)await new Promise(resolve=>setTimeout(resolve,0));
 }
 ctx.putImageData(data,0,0);output.dataset.coverage=String(total?covered/total:0);return output;
}
export async function loadImage(url){const image=new Image();image.src=url;await image.decode();return image;}
