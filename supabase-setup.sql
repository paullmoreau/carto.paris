-- Tournée Générale : base de données partagée (Supabase)
-- À coller une seule fois dans Supabase > SQL Editor > New query, puis « Run ».
--
-- Ce que fait ce script :
--   * places    : les lieux ajoutés par les visiteurs (lecture et ajout ouverts à tous)
--   * events    : les soirées ajoutées par les visiteurs (lecture et ajout ouverts à tous)
--   * overrides : les corrections de l'admin (lecture pour tous, écriture seulement
--                 via la fonction admin_edit, qui vérifie le mot de passe côté serveur)
--   * admin_secret : l'empreinte du mot de passe admin, illisible depuis l'application

create extension if not exists pgcrypto with schema extensions;

create table if not exists public.places (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  name text not null check (char_length(name) between 1 and 80),
  games text[] not null check (cardinality(games) between 1 and 14),
  lat double precision not null check (lat between -90 and 90),
  lon double precision not null check (lon between -180 and 180),
  address text check (char_length(address) <= 160),
  kind text check (char_length(kind) <= 60),
  hours text check (char_length(hours) <= 200),
  phone text check (char_length(phone) <= 40),
  website text check (char_length(website) <= 200),
  note text check (char_length(note) <= 300),
  osm_type text check (osm_type in ('node', 'way', 'relation')),
  osm_id bigint
);

create table if not exists public.events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  type text not null check (type in ('quiz','blindtest','karaoke','jam','echecs','tournoi','theme','jeux')),
  title text not null check (char_length(title) between 1 and 80),
  venue text not null check (char_length(venue) between 1 and 80),
  address text check (char_length(address) <= 160),
  days smallint[] not null default '{}' check (days <@ array[0,1,2,3,4,5,6]::smallint[]),
  date date,
  start_time text check (start_time = '' or start_time ~ '^([01][0-9]|2[0-3]):[0-5][0-9]$'),
  price text check (char_length(price) <= 40),
  note text check (char_length(note) <= 300),
  lat double precision,
  lon double precision,
  check (cardinality(days) > 0 or date is not null)
);

create table if not exists public.overrides (
  key text primary key check (char_length(key) <= 160),
  data jsonb not null,
  updated_at timestamptz not null default now()
);

create table if not exists public.admin_secret (
  id int primary key default 1 check (id = 1),
  hash text not null
);

alter table public.places enable row level security;
alter table public.events enable row level security;
alter table public.overrides enable row level security;
alter table public.admin_secret enable row level security;   -- aucune règle : personne ne peut la lire

drop policy if exists "lecture publique" on public.places;
drop policy if exists "ajout public" on public.places;
drop policy if exists "lecture publique" on public.events;
drop policy if exists "ajout public" on public.events;
drop policy if exists "lecture publique" on public.overrides;
create policy "lecture publique" on public.places for select using (true);
create policy "ajout public" on public.places for insert with check (true);
create policy "lecture publique" on public.events for select using (true);
create policy "ajout public" on public.events for insert with check (true);
create policy "lecture publique" on public.overrides for select using (true);

-- Mot de passe admin : remplace TON-MOT-DE-PASSE ci-dessous AVANT de lancer le script.
-- Il n'est stocké que sous forme chiffrée dans la base, jamais dans le code de l'app.
-- Pour le changer plus tard :
--   update public.admin_secret set hash = extensions.crypt('nouveau-mot-de-passe', extensions.gen_salt('bf'));
insert into public.admin_secret (id, hash)
values (1, extensions.crypt('TON-MOT-DE-PASSE', extensions.gen_salt('bf')))
on conflict (id) do nothing;

create or replace function public.admin_check(p_password text)
returns boolean
language sql
security definer
set search_path = public, extensions
as $$
  select exists (select 1 from public.admin_secret where hash = extensions.crypt(p_password, hash));
$$;

create or replace function public.admin_edit(p_key text, p_data jsonb, p_password text)
returns void
language plpgsql
security definer
set search_path = public, extensions
as $$
begin
  if not public.admin_check(p_password) then
    raise exception 'mot de passe incorrect' using errcode = '28000';
  end if;
  insert into public.overrides (key, data, updated_at)
  values (p_key, p_data, now())
  on conflict (key) do update set data = excluded.data, updated_at = now();
end;
$$;

grant execute on function public.admin_check(text) to anon;
grant execute on function public.admin_edit(text, jsonb, text) to anon;
