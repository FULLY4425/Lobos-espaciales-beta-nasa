import {mkdir,cp,rm} from 'node:fs/promises';
await rm('dist',{recursive:true,force:true});await mkdir('dist');for(const f of ['index.html','src','public','docs'])await cp(f,'dist/'+f,{recursive:true});console.log('Static build generated in dist/');
