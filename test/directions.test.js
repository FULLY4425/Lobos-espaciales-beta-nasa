import test from 'node:test';
import assert from 'node:assert/strict';
import {buildDirections} from '../src/directions.js';
const terrain={width:30,height:30,cellMeters:10,elevations:Array(900).fill(0),west:137,north:-4,degreeStep:.001};
const stop=(name,x,y)=>({name,lon:terrain.west+x*terrain.degreeStep,lat:terrain.north-y*terrain.degreeStep});
test('east then south is a right turn, reverse is a left turn',()=>{
 const p=[[0,0],[1,0],[2,0],[2,1],[2,2]];
 assert.equal(buildDirections(p,terrain).steps[1].kind,'right');
 assert.equal(buildDirections(p.toReversed(),terrain).steps[1].kind,'left');
});
test('straight route produces departure and arrival without false turns',()=>{
 const result=buildDirections([[0,0],[1,0],[2,0],[3,0]],terrain,[stop('A',0,0),stop('B',3,0)]);
 assert.deepEqual(result.steps.map(s=>s.kind),['depart','arrive']);
 assert.equal(result.distance,30);assert.match(result.steps.at(-1).text,/B/);
});
test('small grid zigzags do not cause a turn at every cell',()=>{
 const path=Array.from({length:25},(_,i)=>[i,i%2]);
 assert.ok(buildDirections(path,terrain).steps.length<8);
});
test('intermediate custom stop is announced and distances follow original 3D path',()=>{
 const t={...terrain,elevations:[...terrain.elevations]};t.elevations[1]=10;
 const result=buildDirections([[0,0],[1,0],[2,0],[3,0]],t,[stop('Salida',0,0),stop('Base propia',1,0),stop('Llegada',3,0)]);
 assert.equal(result.steps[1].kind,'waypoint');assert.match(result.steps[1].text,/Base propia/);
 assert.equal(result.steps[1].distance,Math.hypot(10,10));
 assert.equal(result.distance,2*Math.hypot(10,10)+10);
});
test('empty and same-cell routes do not invent instructions',()=>{
 assert.deepEqual(buildDirections([],terrain).steps,[]);
 assert.deepEqual(buildDirections([[0,0]],terrain).steps,[]);
});
test('opposite incoming and outgoing directions announce a U-turn',()=>{
 const result=buildDirections([[0,0],[1,0],[2,0],[1,0],[0,0]],terrain);
 assert.ok(result.steps.some(s=>s.kind==='uturn'));
});

test('KSP fractional endpoints preserve distance and intermediate arrival anchor',()=>{const t={...terrain,cellMeters:2000},path=[[2.1,2],[2.2,2],[2.4,2]],stops=[{name:'A',grid:[2,2],pathIndex:0},{name:'B',grid:[2,2],pathIndex:1},{name:'C',grid:[2,2],pathIndex:2}],result=buildDirections(path,t,stops);assert.ok(Math.abs(result.distance-600)<1e-8);assert.ok(result.steps.some(s=>s.text.includes('B')));assert.ok(result.steps.every(s=>Number.isFinite(s.distance)));});
