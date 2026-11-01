export const REPOSITORY='FULLY4425/Lobos-espaciales-beta-nasa';
export const VERSION='1.3.0';
export const REPORT_PREFIX='[KSP][PRUEBA]';
export const REPORT_LIST=`https://github.com/${REPOSITORY}/issues?q=${encodeURIComponent('is:issue "[KSP][PRUEBA]" in:title')}`;
export const AREAS=['Mapa nativo KSP','HUD de entrenamiento conectado a KSP','Mapas importados con KSP / SCANsat','Conector kRPC y telemetría'];
export const RESULTS=['Funcionó','Funcionó parcialmente','Prueba bloqueada'];
export const CHECKS=['Conexión y reconexión kRPC','Posición y cuerpo correctos','Rumbo frente a la navball','Muestreo de alturas','Creación de destinos y ruta','Recálculo al desviarse','Pausa al perder conexión / salir de región','Indicaciones y voz','Importación / exportación de mapas','Fluidez y consumo de recursos'];
export const CHECK_RESULTS=['No probado','Correcto','Falló','No aplica'];
export const MAX_FILE_BYTES=2*1024*1024,MAX_TOTAL_BYTES=5*1024*1024;
export function redactLog(text){return String(text)
 .replace(/\b(?:github_pat_[A-Za-z0-9_]+|gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,})\b/g,'[CREDENCIAL OCULTA]')
 .replace(/\b(authorization\s*[:=]\s*)(?:bearer|basic)\s+[^\s"',;]+/gi,'$1[CREDENCIAL OCULTA]')
 .replace(/(["']?(?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|passwd|secret)["']?\s*[:=]\s*)["']?[^\s"',;}]+["']?/gi,'$1[VALOR OCULTO]')
 .replace(/([A-Za-z]:\\Users\\)[^\\\r\n]+/g,'$1[USUARIO]')
 .replace(/(\/(?:home|Users)\/)[^/\s]+/g,'$1[USUARIO]');}
export function reviewFiles(files){
 if(files.length>3)throw Error('Selecciona como máximo 3 archivos de texto. Puedes adjuntar más evidencias directamente en GitHub.');
 if(files.reduce((n,f)=>n+f.size,0)>MAX_TOTAL_BYTES)throw Error('Los archivos superan 5 MB en total. Adjunta los logs grandes directamente en GitHub.');
 for(const file of files){if(!/\.(log|txt|json|csv)$/i.test(file.name))throw Error('Para revisión local usa .log, .txt, .json o .csv. Los ZIP y capturas se adjuntan en GitHub.');if(file.size>MAX_FILE_BYTES)throw Error('Cada archivo para revisión local admite hasta 2 MB. Los logs mayores se adjuntan directamente en GitHub.');}
}
function plain(value){return String(value||'').replace(/[\r\n]/g,' ').replace(/[|`*_[\]<>]/g,'').trim();}
function indented(value){return String(value).split('\n').map(line=>'    '+line).join('\n');}
export function buildReport(data){
 if(data.realTest!==true)throw Error('Esta bitácora requiere una prueba con KSP real. La demo y el modo sin juego no son pruebas de integración.');
 const required=['title','tester','date','appVersion','kspVersion','krpcVersion','os','browser','body','setup','steps','expected','actual','improvements'];
 for(const key of required)if(typeof data[key]!=='string'||!data[key].trim())throw Error('Completa los campos obligatorios del informe.');
 if(!AREAS.includes(data.area)||!RESULTS.includes(data.result))throw Error('Selecciona el área KSP y el resultado.');
 if(!data.logs?.trim()&&!data.files?.length&&!data.missingLogs?.trim())throw Error('Añade logs, selecciona archivos o explica por qué no fue posible obtenerlos.');
 if(required.some(key=>data[key].length>4000))throw Error('Reduce los campos a un máximo de 4000 caracteres cada uno.');
 const files=(data.files||[]).map(f=>({name:plain(f.name),text:redactLog(f.text)}));
 const sections=[`<!-- ksp-integration-report:v1 -->\n# ${plain(data.title)}`,
 `## Sesión KSP real\n- Probador: ${plain(data.tester)}\n- Fecha: ${plain(data.date)}\n- Área: ${data.area}\n- Resultado: ${data.result}\n- Aplicación / commit: ${plain(data.appVersion)}\n- KSP: ${plain(data.kspVersion)}\n- kRPC mod / cliente: ${plain(data.krpcVersion)}\n- Sistema operativo: ${plain(data.os)}\n- Navegador: ${plain(data.browser)}\n- Equipo: ${plain(data.hardware)||'No indicado'}\n- Cuerpo / vehículo: ${plain(data.body)} / ${plain(data.craft)||'No indicado'}\n- Mods: ${plain(data.mods)||'No indicados; revisar al reproducir'}`];
 for(const [title,key] of [['Configuración y preparación','setup'],['Pasos para reproducir','steps'],['Resultado esperado','expected'],['Resultado observado y experiencia','actual'],['Errores y momentos relevantes','errors'],['Mejoras y sugerencias','improvements']])sections.push(`## ${title}\n${redactLog(data[key]||'No indicado.')}`);
 sections.push('## Comprobaciones\n'+CHECKS.map((name,i)=>`- ${name}: ${CHECK_RESULTS.includes(data.checks?.[i])?data.checks[i]:'No probado'}`).join('\n'));
 if(data.logs?.trim())sections.push('## Extracto de logs pegado\n'+indented(redactLog(data.logs).slice(0,6000)));
 if(data.missingLogs?.trim())sections.push('## Logs no disponibles\n'+redactLog(data.missingLogs));
 for(const file of files)sections.push(`## Archivo: ${file.name}\nExtracto de hasta 2000 caracteres; adjuntar el archivo revisado completo en GitHub.\n\n${indented(file.text.slice(0,2000))}${file.text.length>2000?'\n\n[Extracto recortado; el archivo completo está en la descarga local.]':''}`);
 if(data.diagnostic)sections.push('## Diagnóstico puntual del conector\nNo sustituye los logs de la sesión.\n\n'+indented(redactLog(JSON.stringify(data.diagnostic,null,2))));
 sections.push('## Evidencias completas\nAdjuntar los logs revisados y las capturas en el campo «Logs y evidencias adjuntas» de GitHub. Los archivos seleccionados en la web no se suben automáticamente.');
 const markdown=sections.join('\n\n');if(markdown.length>58000)throw Error('El informe supera 58 000 caracteres. Resume los campos y adjunta los detalles como archivo.');
 return {markdown,files};
}
export function submission(data,markdown){
 const url=new URL(`https://github.com/${REPOSITORY}/issues/new`);url.searchParams.set('template','ksp-integration.yml');url.searchParams.set('title',`${REPORT_PREFIX} ${plain(data.title).slice(0,100)}`);url.searchParams.set('ksp-version',data.kspVersion);url.searchParams.set('integration',data.area);url.searchParams.set('result',data.result);url.searchParams.set('improvements',data.improvements);url.searchParams.set('report',markdown);
 const needsPaste=url.href.length>7000;if(needsPaste){for(const key of ['report','improvements','ksp-version'])url.searchParams.delete(key);}
 return {url:url.href,needsPaste};
}
export function publicReports(items){if(!Array.isArray(items))throw Error('Respuesta de GitHub no válida.');return items.filter(x=>!x.pull_request&&typeof x.title==='string'&&x.title.startsWith(REPORT_PREFIX)&&new RegExp(`^https://github\\.com/${REPOSITORY}/issues/\\d+$`).test(x.html_url)).slice(0,20);}
