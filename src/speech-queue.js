// At most one pending status and one latest direction; old guidance expires.
export function createSpeechQueue({play,cancel,now=()=>Date.now(),onIdle=()=>{}}){
 let active=null,pending=[],serial=0;
 function start(item){active=item;const token=++serial;play(item.text,()=>{if(token!==serial)return;active=null;pending=pending.filter(p=>now()-p.at<8000);const next=pending.shift();if(next)start(next);else onIdle();});}
 return {
  submit(text,{priority=0,force=false}={}){if(!text)return false;const item={text,priority,at:now()};if(active?.text===text)return true;
   if(force||(active&&priority>active.priority&&priority>=2)){serial++;cancel();active=null;pending=[];}
   if(!active)start(item);else{pending=pending.filter(p=>p.priority!==priority);pending.push(item);pending.sort((a,b)=>b.priority-a.priority);pending=pending.slice(0,2);}return true;},
  clear(){serial++;active=null;pending=[];cancel();},
  clearGuidance(){pending=pending.filter(p=>p.priority>0);if(active?.priority===0){serial++;active=null;cancel();const next=pending.shift();if(next)start(next);}},
 };
}
