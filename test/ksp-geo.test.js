import test from 'node:test';import assert from 'node:assert/strict';
import {localPosition,gridPosition,geoFromGrid,inTerrain} from '../src/ksp-geo.js';
import {buildDirections} from '../src/directions.js';
const terrain={width:33,height:33,cellMeters:25,bodyRadius:320000,center:{lat:89.9,lon:179.999},elevations:Array(1089).fill(0)};
test('native KSP geographic grid roundtrips at high latitude and longitude wrap',()=>{for(const [x,y] of [[0,0],[16,16],[32,32],[20.5,14.2]]){const p=geoFromGrid(terrain,x,y),g=gridPosition(p,terrain);assert.ok(Math.abs(g.x-x)<1e-5);assert.ok(Math.abs(g.y-y)<1e-5);}});
test('center and body radius are native, not calibrated Mars coordinates',()=>{assert.deepEqual(localPosition(terrain.center,terrain),{x:0,y:0});assert.deepEqual(gridPosition(terrain.center,terrain),{x:16,y:16});assert.ok(inTerrain({x:16,y:16},terrain));assert.ok(!inTerrain({x:34,y:16},terrain));});
test('directions support KSP waypoints with explicit grid coordinates',()=>{const path=[[0,0],[1,0],[2,0],[3,0]],stops=[{name:'Rover',grid:[0,0]},{name:'Base KSP',grid:[2,0]},{name:'Destino',grid:[3,0]}];assert.equal(buildDirections(path,terrain,stops).steps[1].kind,'waypoint');});
