-- Automatic installations use the Edge gateway, not direct Storage/Data API access.
create table if not exists ksp_private.devices (
 device_id uuid primary key, secret_hash text not null check(secret_hash ~ '^[a-f0-9]{64}$'),
 user_id uuid unique references auth.users(id), active boolean not null default true,
 created_at timestamptz not null default now(), last_auth_at timestamptz,
 lease uuid, lease_until timestamptz, consent_version text not null
);
create table if not exists ksp_private.device_usage (
 scope text primary key, amount bigint not null default 0, created_at timestamptz not null default now()
);
create table if not exists ksp_private.device_archives (
 path text primary key, user_id uuid not null references auth.users(id), bytes bigint not null,
 created_at timestamptz not null default now(), completed boolean not null default false,
 lease_until timestamptz
);
create index if not exists device_archives_user_idx on ksp_private.device_archives(user_id);
alter table ksp_private.devices enable row level security;
alter table ksp_private.device_usage enable row level security;
alter table ksp_private.device_archives enable row level security;
revoke all on ksp_private.devices,ksp_private.device_usage,ksp_private.device_archives from public,anon,authenticated;
grant usage on schema ksp_private to service_role;
grant select,insert,update on public.ksp_sessions to service_role;
grant select,insert,update,delete on ksp_private.devices,ksp_private.device_usage,ksp_private.device_archives to service_role;

create or replace function public.ksp_device_gateway(p_action text,p_data jsonb) returns jsonb
language plpgsql security invoker set search_path='' as $$
declare d ksp_private.devices; a ksp_private.device_archives; did uuid; uid uuid; n bigint; size bigint; scope_key text; object_path text; lease_id uuid; r jsonb; changed integer;
begin
 perform pg_advisory_xact_lock(hashtext('lobos-ksp-device-gateway'));
 if p_action='reserve' then
  did:=(p_data->>'device_id')::uuid;
  if p_data->>'secret_hash' !~ '^[a-f0-9]{64}$' or p_data->>'consent_version'<>'ksp-upload-consent-v1' then raise exception 'invalid registration'; end if;
  select * into d from ksp_private.devices where device_id=did;
  if found then
   if d.secret_hash<>p_data->>'secret_hash' or not d.active then return jsonb_build_object('error','denied'); end if;
   if d.lease_until>now() or d.last_auth_at>now()-interval '30 seconds' then return jsonb_build_object('error','busy'); end if;
  else
   foreach scope_key in array array['registration-hour-'||to_char(now() at time zone 'UTC','YYYYMMDDHH'),'registration-day-'||to_char(now() at time zone 'UTC','YYYYMMDD')] loop
    select amount into n from ksp_private.device_usage where scope=scope_key;
    if coalesce(n,0)>=(case when scope_key like 'registration-hour-%' then 50 else 200 end) then return jsonb_build_object('error','quota'); end if;
   end loop;
   foreach scope_key in array array['registration-hour-'||to_char(now() at time zone 'UTC','YYYYMMDDHH'),'registration-day-'||to_char(now() at time zone 'UTC','YYYYMMDD')] loop
    insert into ksp_private.device_usage(scope,amount) values(scope_key,1) on conflict(scope) do update set amount=device_usage.amount+1;
   end loop;
   insert into ksp_private.devices(device_id,secret_hash,consent_version) values(did,p_data->>'secret_hash',p_data->>'consent_version');
  end if;
  lease_id:=gen_random_uuid();
  update ksp_private.devices set lease=lease_id,lease_until=now()+interval '90 seconds' where device_id=did returning * into d;
  delete from ksp_private.device_usage where created_at<now()-interval '3 days';
  return jsonb_build_object('lease',lease_id,'user_id',d.user_id);
 elsif p_action='finish' then
  did:=(p_data->>'device_id')::uuid;uid:=(p_data->>'user_id')::uuid;
  select * into d from ksp_private.devices where device_id=did;
  if not found or not d.active or d.lease is distinct from (p_data->>'lease')::uuid or d.lease_until<now() or (d.user_id is not null and d.user_id<>uid) then return jsonb_build_object('error','denied'); end if;
  -- The service-only Edge gateway verifies immutable Auth metadata before this call.
  update ksp_private.devices set user_id=uid,last_auth_at=now(),lease=null,lease_until=null where device_id=did;
  return jsonb_build_object('ok',true);
 end if;
 uid:=(p_data->>'user_id')::uuid;
 select * into d from ksp_private.devices where user_id=uid and active;
 if not found then return jsonb_build_object('error','denied'); end if;
 if p_action='status' then return jsonb_build_object('ok',true,'device_id',d.device_id); end if;
 object_path:=p_data->>'path';
 if split_part(object_path,'/',1)<>uid::text then return jsonb_build_object('error','denied'); end if;
 select * into a from ksp_private.device_archives where device_archives.path=object_path;
 if p_action='reserve-upload' then
  size:=(p_data->>'bytes')::bigint;
  if size not between 1 and 52428800 then return jsonb_build_object('error','size'); end if;
  if a.path is not null then
   if a.user_id<>uid or a.bytes<>size then return jsonb_build_object('error','denied'); end if;
   if a.completed then return jsonb_build_object('already',true); end if;
   if a.lease_until>now() then return jsonb_build_object('error','busy'); end if;
   update ksp_private.device_archives set lease_until=now()+interval '90 seconds' where device_archives.path=object_path;
   return jsonb_build_object('ok',true);
  end if;
  select coalesce(sum(bytes),0) into n from ksp_private.device_archives;
  if n+size>524288000 then return jsonb_build_object('error','quota'); end if;
  select coalesce(sum(bytes),0) into n from ksp_private.device_archives where user_id=uid;
  if n+size>104857600 then return jsonb_build_object('error','quota'); end if;
  scope_key:='upload-day-'||uid::text||'-'||to_char(now() at time zone 'UTC','YYYYMMDD');
  select amount into n from ksp_private.device_usage where scope=scope_key;
  if coalesce(n,0)+size>209715200 then return jsonb_build_object('error','quota'); end if;
  insert into ksp_private.device_usage(scope,amount) values(scope_key,size) on conflict(scope) do update set amount=device_usage.amount+excluded.amount;
  insert into ksp_private.device_archives(path,user_id,bytes,lease_until) values(object_path,uid,size,now()+interval '90 seconds');
  return jsonb_build_object('ok',true);
 elsif p_action='finish-upload' then
  if a.user_id is distinct from uid then return jsonb_build_object('error','denied'); end if;
  update ksp_private.device_archives set completed=true,lease_until=null where device_archives.path=object_path;
  return jsonb_build_object('ok',true);
 elsif p_action='archive' then
  if a.user_id is distinct from uid or not a.completed then return jsonb_build_object('error','missing'); end if;
  return jsonb_build_object('ok',true,'bytes',a.bytes);
 elsif p_action='index' then
  r:=p_data->'row';
  if a.user_id is distinct from uid or not a.completed or r->>'user_id'<>uid::text or r->>'archive_path'<>object_path or r->>'id'<>split_part(object_path,'/',2) or (r->>'archive_bytes')::bigint<>a.bytes then return jsonb_build_object('error','denied'); end if;
  insert into public.ksp_sessions(id,user_id,app_version,archive_path,sha256,archive_bytes,captured_at,started_at,telemetry_samples,stopped_at,diagnostic_summary)
  values(r->>'id',uid,r->>'app_version',object_path,r->>'sha256',a.bytes,(r->>'captured_at')::timestamptz,(r->>'started_at')::timestamptz,(r->>'telemetry_samples')::bigint,(r->>'stopped_at')::timestamptz,r->'diagnostic_summary')
  on conflict(id) do update set app_version=excluded.app_version,archive_path=excluded.archive_path,sha256=excluded.sha256,archive_bytes=excluded.archive_bytes,captured_at=excluded.captured_at,started_at=excluded.started_at,telemetry_samples=excluded.telemetry_samples,stopped_at=excluded.stopped_at,diagnostic_summary=excluded.diagnostic_summary
  where ksp_sessions.user_id=excluded.user_id;
  get diagnostics changed=row_count;
  if changed<>1 then return jsonb_build_object('error','denied'); end if;
  return jsonb_build_object('ok',true);
 elsif p_action='forget-archive' then
  if a.path is null then return jsonb_build_object('ok',true); end if;
  if a.user_id is distinct from uid then return jsonb_build_object('error','denied'); end if;
  delete from ksp_private.device_archives where device_archives.path=object_path;
  return jsonb_build_object('ok',true);
 end if;
 return jsonb_build_object('error','invalid');
end $$;
revoke all on function public.ksp_device_gateway(text,jsonb) from public,anon,authenticated;
grant execute on function public.ksp_device_gateway(text,jsonb) to service_role;
