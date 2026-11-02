import {buildDirections,distanceText} from './directions.js';
import {createSpeechQueue} from './speech-queue.js';

export function createNavigation({guideName='Marte'}={}) {
  const $=id=>document.getElementById(id),synth=window.speechSynthesis;
  const supported=!!synth&&typeof window.SpeechSynthesisUtterance==='function';
  let route={distance:0,steps:[]},voices=[],enabled=false,previousRunning=false,previousProgress=0,lastSpoken='',lastTime=0,activeStep=-1,arrived=false,settings={};
  try{settings=JSON.parse(localStorage.getItem('mars-navigation-voice')||'{}')||{};}catch{/* Preferences are optional. */}
  function save(){try{localStorage.setItem('mars-navigation-voice',JSON.stringify({voice:$('navigationVoice').value,rate:Number($('voiceRate').value),volume:Number($('voiceVolume').value)}));}catch{/* Voice still works without storage. */}}
  const speech=createSpeechQueue({cancel:()=>{if(supported)synth.cancel();},onIdle:()=>{$('voiceStatus').textContent='Voz lista.';},play:(text,done)=>{
    const utterance=new SpeechSynthesisUtterance(text),voice=voices.find(v=>v.voiceURI===$('navigationVoice').value)||voices[0];
    if(voice)utterance.voice=voice;utterance.lang=voice?.lang||'es-MX';utterance.rate=Number($('voiceRate').value);utterance.volume=Number($('voiceVolume').value);
    utterance.onstart=()=>{$('voiceStatus').textContent=`Hablando: ${text}`;};utterance.onend=done;utterance.onerror=e=>{done();if(!['canceled','interrupted'].includes(e.error))$('voiceStatus').textContent='No se pudo reproducir la voz. Prueba otra voz o usa texto.';};synth.speak(utterance);
  }});
  function cancel(){speech.clear();}
  function populate(){
    if(!supported)return;
    voices=synth.getVoices().filter(v=>v.lang.toLowerCase().startsWith('es')).sort((a,b)=>Number(b.lang.toLowerCase()==='es-mx')-Number(a.lang.toLowerCase()==='es-mx')||Number(b.localService)-Number(a.localService));
    const current=$('navigationVoice').value||settings.voice;
    $('navigationVoice').replaceChildren(new Option(voices.length?'Español · voz recomendada':'Español · voz del sistema',''),...voices.map(v=>new Option(`${v.name} · ${v.lang}`,v.voiceURI)));
    if(voices.some(v=>v.voiceURI===current))$('navigationVoice').value=current;
    $('voiceStatus').textContent=voices.length?`Disponible: ${voices.find(v=>v.voiceURI===$('navigationVoice').value)?.name||voices[0].name}. Se prioriza español de México.`:'El navegador no ha listado voces en español. Se intentará usar la voz del sistema; puedes probarla.';
  }
  function speak(text,options={}){return supported&&speech.submit(text,options);}
  function currentSpeech(){return $('navigationDistance').textContent?`${$('navigationDistance').textContent}, ${$('navigationText').textContent.toLowerCase()}`:$('navigationText').textContent;}
  $('voiceRate').value=String(Math.max(.8,Math.min(1.4,Number(settings.rate)||1)));
  $('voiceVolume').value=String(Math.max(0,Math.min(1,Number.isFinite(settings.volume)?settings.volume:1)));
  $('enableNavigationVoice').onclick=()=>{enabled=!enabled;$('enableNavigationVoice').setAttribute('aria-pressed',String(enabled));$('enableNavigationVoice').textContent=enabled?'🔊 Voz activada':'🔇 Activar voz';cancel();if(enabled)speak(route.steps.length?currentSpeech():`Guía de ${guideName} activada. Calcula una ruta e inicia el recorrido.`,{force:true});};
  $('testNavigationVoice').onclick=()=>speak(`Hola. Soy tu guía de ${guideName}. Continúa recto y, en cincuenta metros, gira a la derecha.`,{force:true});
  $('repeatDirection').onclick=()=>{if(route.steps.length)speak(currentSpeech(),{force:true});};
  for(const id of ['navigationVoice','voiceRate','voiceVolume'])$(id).onchange=()=>{cancel();save();if(id==='navigationVoice')populate();};
  if(supported){populate();synth.addEventListener('voiceschanged',populate);}else{for(const id of ['enableNavigationVoice','testNavigationVoice','navigationVoice','voiceRate','voiceVolume','repeatDirection'])$(id).disabled=true;$('voiceStatus').textContent='Este navegador no ofrece voz. Las indicaciones en pantalla siguen disponibles.';}
  window.addEventListener('pagehide',cancel);document.addEventListener('visibilitychange',()=>{if(document.hidden)cancel();});
  function update(progress,running,options={}){
    if(!route.steps.length)return;
    const traveled=Math.max(0,Math.min(1,progress))*route.distance;
    const jump=Math.abs(progress-previousProgress)>.08;

    const complete=progress>=1&&options.allowArrival!==false,index=complete?route.steps.length-1:Math.max(1,route.steps.findIndex((step,i)=>i>0&&step.distance>=traveled-3));
    const step=route.steps[index],remaining=index===route.steps.length-1&&Number.isFinite(options.remainingToDestination)?options.remainingToDestination:Math.max(0,step.distance-traveled);
    $('navigationBanner').hidden=false;
    const displayText=complete?step.text:step.text.replace('Llegaste','Llegarás');if(index!==activeStep||$('navigationText').textContent!==displayText){$('navigationText').textContent=displayText;$('navigationArrow').textContent=step.icon;for(const [i,item] of [...$('directionSteps').children].entries()){if(i===index)item.setAttribute('aria-current','step');else item.removeAttribute('aria-current');}activeStep=index;}
    $('navigationDistance').textContent=complete?'':remaining<=6?'Ahora':`En ${distanceText(remaining)}`;
    $('navigationRemaining').textContent=complete?'Destino alcanzado':`${distanceText(Number.isFinite(options.remainingToDestination)&&index===route.steps.length-1?options.remainingToDestination:route.distance-traveled)} hasta el destino`;
    if(complete&&!arrived&&(previousRunning||options.explicitArrival)){arrived=true;if(enabled)speak(step.text,{force:true});}
    if(!complete)arrived=false;
    if(enabled&&running&&!document.hidden&&!complete){
      const phase=remaining<=6?'now':'ahead',key=`${index}:${phase}`;
      if(!previousRunning){if(speak(currentSpeech())){lastSpoken=key;lastTime=performance.now();}}
      else if(!jump&&remaining<=Math.max(50,(options.speed||0)*6)&&lastSpoken!==key&&performance.now()-lastTime>4500){if(speak(currentSpeech())){lastSpoken=key;lastTime=performance.now();}}
    }
    if(!running&&previousRunning&&!complete)speech.clearGuidance();
    previousRunning=running;previousProgress=progress;
  }
  return {
    setRoute(path,terrain,stops){cancel();route=buildDirections(path,terrain,stops);lastSpoken='';previousRunning=false;previousProgress=0;activeStep=-1;arrived=false;$('navigationBanner').hidden=!route.steps.length;$('repeatDirection').disabled=!supported||!route.steps.length;
      $('directionSteps').replaceChildren(...route.steps.map((step,i)=>{const item=document.createElement('li'),text=document.createElement('span'),distance=document.createElement('small');text.textContent=`${step.icon} ${step.text}`;distance.textContent=i?`${distanceText(step.distance-route.steps[i-1].distance)} desde la indicación anterior`:'Salida';item.append(text,distance);return item;}));
      $('directionSummary').textContent=route.steps.length?`${route.steps.length} indicaciones · sigue la línea de la ruta`:'Calcula una ruta para ver las indicaciones.';if(route.steps.length)update(0,false);
    },
    update,
    announce(text,{priority=1}={}){if(enabled&&!document.hidden)speak(text,{priority});},
    maneuver(progress){const traveled=Math.max(0,Math.min(1,progress))*route.distance;const step=route.steps.find(s=>s.distance>traveled+3&&['left','right','uturn'].includes(s.kind));return step?step.distance-traveled:Infinity;},
    pause(){cancel();previousRunning=false;},
    seek(progress){cancel();lastSpoken='';previousRunning=false;update(progress,false);}
  };
}
