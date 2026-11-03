export const VERSION='ksp-upload-consent-v1';
export const MAX_ZIP=50*1024*1024;
export function registration(body){
 if(!body||body.consent_version!==VERSION||!/^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/.test(body.device_id)||!/^[a-f0-9]{64}$/.test(body.device_secret))throw Error('invalid');
 return body;
}
export function archivePath(path,uid){
 const escaped=uid.replaceAll('-','\\-');
 if(typeof path!=='string'||!new RegExp('^'+escaped+'/\\d{4}-\\d{2}-\\d{2}T\\d{2}-\\d{2}-\\d{2}Z-[a-f0-9]{12}/[a-f0-9]{64}\\.zip$').test(path))throw Error('path');
 return path;
}
export async function digest(data){return [...new Uint8Array(await crypto.subtle.digest('SHA-256',typeof data==='string'?new TextEncoder().encode(data):data))].map(x=>x.toString(16).padStart(2,'0')).join('');}
export function validateZip(data){
 const b=new Uint8Array(data),v=new DataView(data);if(b.length<22||b.length>MAX_ZIP||v.getUint32(0,true)!==0x04034b50)throw Error('zip');
 let end=-1;for(let i=b.length-22;i>=Math.max(0,b.length-65557);i--)if(v.getUint32(i,true)===0x06054b50){end=i;break;}
 if(end<0||v.getUint16(end+4,true)!==0||v.getUint16(end+6,true)!==0)throw Error('zip');
 if(end+22+v.getUint16(end+20,true)!==b.length)throw Error('zip');
 const count=v.getUint16(end+10,true);if(v.getUint16(end+8,true)!==count)throw Error('zip');let at=v.getUint32(end+16,true),total=0,manifest=false;
 const centralStart=at;if(count<1||count>1024||centralStart+v.getUint32(end+12,true)!==end)throw Error('zip');
 const names=new Set();for(let i=0;i<count;i++){
  if(at+46>end||v.getUint32(at,true)!==0x02014b50)throw Error('zip');
  const flags=v.getUint16(at+8,true),method=v.getUint16(at+10,true),size=v.getUint32(at+24,true),n=v.getUint16(at+28,true),extra=v.getUint16(at+30,true),comment=v.getUint16(at+32,true),attrs=v.getUint32(at+38,true);
  if(at+46+n+extra+comment>end||(flags&1)||![0,8].includes(method)||((attrs>>>16)&0xf000)===0xa000)throw Error('zip');
  const name=new TextDecoder('utf-8',{fatal:true}).decode(b.subarray(at+46,at+46+n));
  if(!/^(session\.json|KSP\.log|Player\.log|events\.jsonl|telemetry\.jsonl|computer\.jsonl|flight\.jsonl|analysis\.json|connector\.log(?:\.[12])?|(?:terrain|mission)-[a-f0-9]{32}\.json)$/.test(name)||names.has(name))throw Error('zip');
  const local=v.getUint32(at+42,true),compressed=v.getUint32(at+20,true);
  if(local+30>centralStart||v.getUint32(local,true)!==0x04034b50||v.getUint16(local+6,true)!==flags||v.getUint16(local+8,true)!==method)throw Error('zip');
  const localN=v.getUint16(local+26,true),localExtra=v.getUint16(local+28,true);
  if(local+30+localN+localExtra+compressed>centralStart||new TextDecoder('utf-8',{fatal:true}).decode(b.subarray(local+30,local+30+localN))!==name)throw Error('zip');
  names.add(name);manifest ||= name==='session.json';total+=size;if(total>128*1024*1024)throw Error('zip');at+=46+n+extra+comment;
 }
 if(!manifest||at!==end)throw Error('zip');return true;
}

export function diagnosticQuality(summary,indexCount){
 if(!summary||Array.isArray(summary)||summary.schema!=='ksp-session-analysis-v1')return null;
 const summaryCount=summary.telemetrySamples,valid=Number.isSafeInteger(indexCount)&&indexCount>=0&&Number.isSafeInteger(summaryCount)&&summaryCount>=0;
 return {...summary,dataQuality:{comparison:'index-vs-summary',indexTelemetrySamples:Number.isSafeInteger(indexCount)?indexCount:null,summaryTelemetrySamples:Number.isSafeInteger(summaryCount)?summaryCount:null,telemetryCountMatches:valid?indexCount===summaryCount:null,status:valid?(indexCount===summaryCount?'consistent':'stale-summary'):'unknown'}};
}
