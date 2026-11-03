// In-memory retries while the view is open; the session journal is the local fallback.
export function createEventQueue(send,{id=()=>crypto.randomUUID(),limit=200}={}){
 const queue=[];let pending=null,running=null;
 return {get size(){return queue.length+(pending?.events.length||0);},push(event,instanceId){if(queue.length>=limit)queue.shift();queue.push({event,instanceId});},flush(instanceId){
  if(running)return running;
  if(pending&&pending.instanceId!==instanceId)pending=null;
  while(queue.length&&queue[0].instanceId!==undefined&&queue[0].instanceId!==instanceId)queue.shift();
  if(!pending&&queue.length){const events=[];while(queue.length&&events.length<20){if(queue[0].instanceId!==undefined&&queue[0].instanceId!==instanceId)break;const next=queue[0].event;if(events.length&&new TextEncoder().encode(JSON.stringify({events:[...events,next]})).length>12000)break;events.push(queue.shift());}pending={batchId:id(),instanceId,events};}
  if(!pending)return Promise.resolve(true);
  running=(async()=>{try{const response=await send(pending);if(response.ok){pending=null;return true;}if(response.status===409)pending=null;return false;}catch{return false;}finally{running=null;}})();return running;
 }};
}
