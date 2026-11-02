-- Apply in your own Supabase project's SQL editor. All uploaded files remain private.
-- No service_role key is distributed to testers. Disable public signup in Auth settings.
begin;

create table if not exists public.ksp_testers (
  user_id uuid primary key references auth.users(id) on delete cascade,
  role text not null default 'tester' check (role in ('tester','admin')),
  active boolean not null default true
);
alter table public.ksp_testers enable row level security;

-- Private definer functions avoid recursive RLS without exposing privileged RPCs.
create schema if not exists ksp_private;
revoke all on schema ksp_private from public, anon;
grant usage on schema ksp_private to authenticated;
create or replace function ksp_private.ksp_is_admin() returns boolean
language sql stable security definer set search_path = '' as $$
  select auth.uid() is not null and exists(select 1 from public.ksp_testers
    where user_id=(select auth.uid()) and active and role='admin');
$$;
create or replace function ksp_private.ksp_is_tester() returns boolean
language sql stable security definer set search_path = '' as $$
  select auth.uid() is not null and exists(select 1 from public.ksp_testers
    where user_id=(select auth.uid()) and active);
$$;
revoke all on function ksp_private.ksp_is_admin() from public, anon;
revoke all on function ksp_private.ksp_is_tester() from public, anon;
grant execute on function ksp_private.ksp_is_admin() to authenticated;
grant execute on function ksp_private.ksp_is_tester() to authenticated;
-- Public RPC wrappers are invoker-only and only disclose the current user's role.
create or replace function public.ksp_is_admin() returns boolean
language sql stable security invoker set search_path = '' as $$
  select ksp_private.ksp_is_admin();
$$;
create or replace function public.ksp_is_tester() returns boolean
language sql stable security invoker set search_path = '' as $$
  select ksp_private.ksp_is_tester();
$$;
revoke all on function public.ksp_is_admin() from public, anon;
revoke all on function public.ksp_is_tester() from public, anon;
grant execute on function public.ksp_is_admin() to authenticated;
grant execute on function public.ksp_is_tester() to authenticated;
revoke all on public.ksp_testers from public, anon, authenticated;
grant select on public.ksp_testers to authenticated;
drop policy if exists ksp_testers_read on public.ksp_testers;
create policy ksp_testers_read on public.ksp_testers for select to authenticated
  using (user_id=(select auth.uid()) or public.ksp_is_admin());

create table if not exists public.ksp_sessions (
  id text primary key,
  user_id uuid not null references auth.users(id),
  app_version text not null,
  archive_path text not null,
  sha256 text not null check (sha256 ~ '^[a-f0-9]{64}$'),
  archive_bytes bigint not null check (archive_bytes between 0 and 52428800),
  captured_at timestamptz not null,
  started_at timestamptz,
  telemetry_samples bigint check (telemetry_samples>=0),
  check (split_part(archive_path,'/',1)=user_id::text)
);
alter table public.ksp_sessions add column if not exists stopped_at timestamptz;
alter table public.ksp_sessions add column if not exists diagnostic_summary jsonb;
alter table public.ksp_sessions enable row level security;
revoke all on public.ksp_sessions from public, anon, authenticated;
grant select, insert, update on public.ksp_sessions to authenticated;
create index if not exists ksp_sessions_user_captured_idx on public.ksp_sessions(user_id,captured_at desc);
drop policy if exists ksp_sessions_read on public.ksp_sessions;
create policy ksp_sessions_read on public.ksp_sessions for select to authenticated
  using ((select ksp_private.ksp_is_admin()) or ((select ksp_private.ksp_is_tester()) and user_id=(select auth.uid())));
drop policy if exists ksp_sessions_insert on public.ksp_sessions;
create policy ksp_sessions_insert on public.ksp_sessions for insert to authenticated
  with check ((select ksp_private.ksp_is_tester()) and user_id=(select auth.uid()));
drop policy if exists ksp_sessions_update on public.ksp_sessions;
create policy ksp_sessions_update on public.ksp_sessions for update to authenticated
  using ((select ksp_private.ksp_is_tester()) and user_id=(select auth.uid()))
  with check ((select ksp_private.ksp_is_tester()) and user_id=(select auth.uid()));

insert into storage.buckets(id,name,public,file_size_limit,allowed_mime_types)
values ('ksp-evidence','ksp-evidence',false,52428800,array['application/zip'])
on conflict (id) do update set public=false,file_size_limit=excluded.file_size_limit,allowed_mime_types=excluded.allowed_mime_types;

drop policy if exists ksp_evidence_read on storage.objects;
create policy ksp_evidence_read on storage.objects for select to authenticated
  using (bucket_id='ksp-evidence' and ((select ksp_private.ksp_is_admin()) or ((select ksp_private.ksp_is_tester()) and (storage.foldername(name))[1]=(select auth.uid())::text)));
drop policy if exists ksp_evidence_insert on storage.objects;
create policy ksp_evidence_insert on storage.objects for insert to authenticated
  with check (bucket_id='ksp-evidence' and (select ksp_private.ksp_is_tester()) and (storage.foldername(name))[1]=(select auth.uid())::text);
drop policy if exists ksp_evidence_update on storage.objects;
create policy ksp_evidence_update on storage.objects for update to authenticated
  using (bucket_id='ksp-evidence' and (select ksp_private.ksp_is_tester()) and (storage.foldername(name))[1]=(select auth.uid())::text)
  with check (bucket_id='ksp-evidence' and (select ksp_private.ksp_is_tester()) and (storage.foldername(name))[1]=(select auth.uid())::text);
drop policy if exists ksp_evidence_delete on storage.objects;
create policy ksp_evidence_delete on storage.objects for delete to authenticated
  using (bucket_id='ksp-evidence' and (select ksp_private.ksp_is_tester()) and (storage.foldername(name))[1]=(select auth.uid())::text);

commit;
-- After creating a tester in Authentication > Users, authorize its UUID:
-- insert into public.ksp_testers(user_id,role) values ('USER_UUID','tester');
-- Use role='admin' for your own Auth user to read all evidence through an authenticated client.
