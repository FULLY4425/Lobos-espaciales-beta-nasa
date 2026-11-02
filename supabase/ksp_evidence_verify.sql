-- Read-only verification for the owner in Supabase SQL Editor.
-- Does not upload evidence, modify policies or expose credentials/user rows.
select 'private_bucket' as check_name,
       exists(select 1 from storage.buckets where id='ksp-evidence' and public=false
              and file_size_limit=52428800) as ok
union all
select 'sessions_rls', exists(select 1 from pg_class c join pg_namespace n on n.oid=c.relnamespace
    where n.nspname='public' and c.relname='ksp_sessions' and c.relrowsecurity)
union all
select 'testers_rls', exists(select 1 from pg_class c join pg_namespace n on n.oid=c.relnamespace
    where n.nspname='public' and c.relname='ksp_testers' and c.relrowsecurity)
union all
select 'tester_function', to_regprocedure('public.ksp_is_tester()') is not null
union all
select 'admin_function', to_regprocedure('public.ksp_is_admin()') is not null
union all
select 'session_policies', (select count(*)=3 from pg_policies where schemaname='public'
    and tablename='ksp_sessions' and policyname in ('ksp_sessions_read','ksp_sessions_insert','ksp_sessions_update'))
union all
select 'storage_policies', (select count(*)=4 from pg_policies where schemaname='storage'
    and tablename='objects' and policyname in ('ksp_evidence_read','ksp_evidence_insert','ksp_evidence_update','ksp_evidence_delete'));
-- All true confirms expected objects exist, not that every possible policy is safe.
-- Review other permissive policies and verify isolation with two authorized test users.
