import test from 'node:test';
import assert from 'node:assert/strict';
import {projectKsp,nearestOnRoute} from '../src/ar-tracking.js';
const origin={body:'Duna',vesselId:'rover',bodyRadius:320000,latitude:0,longitude:0};
test('KSP north projects to local north and uses actual body radius',()=>{
 const point=projectKsp({...origin,latitude:180/Math.PI/origin.bodyRadius},origin);
 assert.ok(Math.abs(point.y+1)<1e-8);assert.equal(point.x,0);
});
test('crossing longitude wrap keeps displacement local',()=>{
 const anchor={...origin,longitude:179.999};
 const point=projectKsp({...anchor,longitude:-179.999},anchor);
 assert.ok(point.x>0&&point.x<12);
});
test('changing body or vessel requires calibration',()=>{
 assert.equal(projectKsp({...origin,body:'Kerbin'},origin),null);
 assert.equal(projectKsp({...origin,vesselId:'other'},origin),null);
 assert.equal(projectKsp({...origin,latitude:NaN},origin),null);
});
test('heading calibration rotates displacement without changing distance',()=>{
 const point=projectKsp({...origin,latitude:180/Math.PI/origin.bodyRadius},origin,90);
 assert.ok(Math.abs(point.x+1)<1e-8);assert.ok(Math.abs(point.y)<1e-8);
});
test('route projection reports progress and off-route distance',()=>{
 const terrain={cellMeters:10,width:3,elevations:[0,0,0]};
 const point=nearestOnRoute({x:10,y:4},[[0,0],[1,0],[2,0]],terrain);
 assert.equal(point.crossTrack,4);assert.equal(point.progress,.5);
 assert.equal(nearestOnRoute(null,[],terrain),null);
});
