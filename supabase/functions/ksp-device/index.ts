import {VERSION,MAX_ZIP,registration,archivePath,digest,validateZip} from './core.mjs';
import publicKey from './public-key.json' with {type:'json'};
const base=Deno.env.get('SUPABASE_URL')!,service=Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
const json=(body:unknown,status=200)=>new Response(JSON.stringify(body),{status,headers:{'content-type':'application/json','cache-control':'no-store'}});
class Failure extends Error{constructor(public status:number,public code:string){super(code);}}
async function limited(req:Request,max:number){const declared=Number(req.headers.get('content-length'));if(declared>max)throw new Failure(413,'size');const reader=req.body?.getReader();if(!reader)throw new Failure(400,'body');const parts:Uint8Array[]=[];let n=0;while(true){const {value,done}=await reader.read();if(done)break;n+=value.length;if(n>max){await reader.cancel();throw new Failure(413,'size');}parts.push(value);}const data=new Uint8Array(n);let i=0;for(const p of parts){data.set(p,i);i+=p.length;}return data;}
async function readJSON(req:Request,max=16384){try{return JSON.parse(new TextDecoder().decode(await limited(req,max)));}catch(e){if(e instanceof Failure)throw e;throw new Failure(400,'json');}}
async function api(path:string,method='GET',body?:unknown,authorization=service){
 const r=await fetch(base+path,{method,headers:{apikey:service,authorization:'Bearer '+authorization,'content-type':'application/json'},body:body===undefined?undefined:JSON.stringify(body),signal:AbortSignal.timeout(20000)});
 if(!r.ok)throw new Failure(r.status===401||r.status===403?403:503,'backend');
 const text=await r.text();return text?JSON.parse(text):null;
}
async function rpc(action:string,data:unknown){const v=await api('/rest/v1/rpc/ksp_device_gateway','POST',{p_action:action,p_data:data});if(v?.error)throw new Failure(['busy','quota'].includes(v.error)?429:403,v.error);return v;}
async function password(id:string,secret:string){const key=await crypto.subtle.importKey('raw',new TextEncoder().encode(service),{name:'HMAC',hash:'SHA-256'},false,['sign']);const sig=await crypto.subtle.sign('HMAC',key,new TextEncoder().encode(id+':'+secret));return 'Ksp!A1-'+[...new Uint8Array(sig)].map(x=>x.toString(16).padStart(2,'0')).join('');}
async function signIn(email:string,password:string){const r=await fetch(base+'/auth/v1/token?grant_type=password',{method:'POST',headers:{apikey:service,'content-type':'application/json'},body:JSON.stringify({email,password}),signal:AbortSignal.timeout(20000)});return r.ok?await r.json():null;}
async function enroll(req:Request){
 let body;try{body=registration(await readJSON(req,4096));}catch(e){if(e instanceof Failure)throw e;throw new Failure(400,'registration');}
 const reservation=await rpc('reserve',{device_id:body.device_id,secret_hash:await digest(body.device_secret),consent_version:body.consent_version});
 const email=`device-${body.device_id}@ksp.lobos.invalid`,pass=await password(body.device_id,body.device_secret);
 let token;
 if(reservation.user_id){
  const u=await api('/auth/v1/admin/users/'+reservation.user_id);
  if(u.app_metadata?.ksp_device!==true||u.app_metadata?.ksp_device_id!==body.device_id)throw new Failure(403,'identity');
  await api('/auth/v1/admin/users/'+reservation.user_id,'PUT',{password:pass});token=await signIn(email,pass);
 }else{
  token=await signIn(email,pass);
  if(!token){await api('/auth/v1/admin/users','POST',{email,password:pass,email_confirm:true,app_metadata:{ksp_device:true,ksp_device_id:body.device_id}});token=await signIn(email,pass);}
 }
 if(!token?.user?.id||token.user.app_metadata?.ksp_device!==true||token.user.app_metadata?.ksp_device_id!==body.device_id)throw new Failure(503,'session');
 await rpc('finish',{device_id:body.device_id,user_id:token.user.id,lease:reservation.lease});
 return json({access_token:token.access_token,refresh_token:token.refresh_token,expires_in:token.expires_in,user:{id:token.user.id,app_metadata:{ksp_device:true,ksp_device_id:body.device_id}}});
}
async function identity(req:Request){const auth=req.headers.get('authorization')||'';if(!auth.startsWith('Bearer ')||auth.length>8192)throw new Failure(401,'auth');const user=await api('/auth/v1/user','GET',undefined,auth.slice(7));if(user.app_metadata?.ksp_device!==true)throw new Failure(403,'device');const state=await rpc('status',{user_id:user.id});if(state.device_id!==user.app_metadata.ksp_device_id)throw new Failure(403,'device');return user.id;}
Deno.serve(async req=>{
 try{
  if(req.headers.get('apikey')!==publicKey.key)throw new Failure(401,'key');
  if(req.headers.has('origin'))throw new Failure(403,'desktop-only');
  const url=new URL(req.url),action=url.pathname.split('/').pop();
  if(action==='register'&&req.method==='POST')return await enroll(req);
  const uid=await identity(req);
  if(action==='status'&&req.method==='GET')return json({ok:true,mode:'device',private:true});
  if(action==='upload'&&req.method==='POST'){
   const path=archivePath(url.searchParams.get('path'),uid),data=await limited(req,MAX_ZIP);
   try{validateZip(data.buffer);}catch{throw new Failure(400,'zip');}
   if(await digest(data)!==path.split('/').pop()!.slice(0,-4))throw new Failure(400,'hash');
   const reserve=await rpc('reserve-upload',{user_id:uid,path,bytes:data.length});
   if(!reserve.already){
    const r=await fetch(base+'/storage/v1/object/ksp-evidence/'+path,{method:'POST',headers:{apikey:service,authorization:'Bearer '+service,'content-type':'application/zip','x-upsert':'true'},body:data,signal:AbortSignal.timeout(60000)});
    if(!r.ok){await rpc('forget-archive',{user_id:uid,path});throw new Failure(503,'storage');}
    await rpc('finish-upload',{user_id:uid,path});
   }
   return json({ok:true});
  }
  if(action==='index'&&req.method==='POST'){
   const body=await readJSON(req,65536),path=archivePath(body.archive_path,uid),archive=await rpc('archive',{user_id:uid,path});
   if(body.user_id!==uid||body.id!==path.split('/')[1]||body.sha256!==path.split('/')[2].slice(0,-4)||body.archive_bytes!==archive.bytes)throw new Failure(400,'index');
   if(typeof body.app_version!=='string'||body.app_version.length>40||!Number.isFinite(Date.parse(body.captured_at)))throw new Failure(400,'index');
   const row={id:body.id,user_id:uid,app_version:body.app_version,archive_path:path,sha256:body.sha256,archive_bytes:archive.bytes,captured_at:body.captured_at,started_at:body.started_at??null,telemetry_samples:body.telemetry_samples??null,stopped_at:body.stopped_at??null,diagnostic_summary:body.diagnostic_summary??null};
   await rpc('index',{user_id:uid,path,row});return json({ok:true});
  }
  if(action==='delete'&&req.method==='POST'){
   const body=await readJSON(req);if(!Array.isArray(body.paths)||body.paths.length>10)throw new Failure(400,'paths');
   const paths=body.paths.map((p:string)=>archivePath(p,uid));
   for(const path of paths){
    const session=path.split('/')[1],current=await api('/rest/v1/ksp_sessions?select=archive_path&id=eq.'+encodeURIComponent(session)+'&user_id=eq.'+uid);
    if(current.some((r:{archive_path:string})=>r.archive_path===path))throw new Failure(409,'current-archive');
    await api('/storage/v1/object/ksp-evidence','DELETE',{prefixes:[path]});await rpc('forget-archive',{user_id:uid,path});
   }
   return json({ok:true});
  }
  throw new Failure(404,'route');
 }catch(e){const status=e instanceof Failure?e.status:400;return json({error:e instanceof Failure?e.code:'invalid'},status);}
});
