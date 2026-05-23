create extension if not exists pgcrypto;

create table if not exists blood_banks (
  id text primary key,
  name text not null,
  source_type text not null check (source_type in ('blood_bank', 'pharmacy')),
  eta_minutes integer not null check (eta_minutes >= 0),
  phone text,
  is_tie_up_partner boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists blood_inventory (
  id uuid primary key default gen_random_uuid(),
  source_id text not null references blood_banks(id) on delete cascade,
  product_type text not null,
  blood_group text,
  units_available integer not null check (units_available >= 0),
  expires_at timestamptz,
  notes text,
  last_updated_at timestamptz not null default now()
);

create table if not exists couriers (
  id text primary key,
  name text not null,
  capacity_units integer not null check (capacity_units >= 1),
  available boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists emergency_cases (
  id text primary key,
  conversation_id text,
  transcript text not null,
  case_type text not null,
  patient_status text not null,
  target_minutes integer not null check (target_minutes > 0),
  urgency_score integer not null check (urgency_score between 1 and 10),
  required_products jsonb not null,
  missing_fields jsonb not null default '[]'::jsonb,
  parser_confidence numeric not null default 1,
  status text not null default 'parsed',
  created_at timestamptz not null default now()
);

create table if not exists optimization_runs (
  id uuid primary key default gen_random_uuid(),
  emergency_case_id text not null references emergency_cases(id) on delete cascade,
  baseline_result_json jsonb not null,
  qiskit_result_json jsonb not null,
  solver_type text not null,
  objective_value numeric not null,
  improvement_summary text,
  created_at timestamptz not null default now()
);

create table if not exists procurement_actions (
  id uuid primary key default gen_random_uuid(),
  optimization_run_id uuid references optimization_runs(id) on delete cascade,
  source_id text references blood_banks(id),
  product_type text not null,
  blood_group text,
  units_requested integer not null check (units_requested >= 1),
  eta_minutes integer not null check (eta_minutes >= 0),
  priority_order integer not null,
  courier_id text references couriers(id),
  reason text not null,
  action_status text not null default 'pending' check (action_status in ('pending', 'confirmed', 'dispatched', 'completed', 'cancelled')),
  created_at timestamptz not null default now()
);

create table if not exists clinical_constraints (
  id uuid primary key default gen_random_uuid(),
  item_name text not null,
  item_type text not null,
  storage_rule text,
  urgency_role text,
  compatibility_note text,
  citation_url text,
  notes text,
  created_at timestamptz not null default now()
);

alter table blood_banks enable row level security;
alter table blood_inventory enable row level security;
alter table couriers enable row level security;
alter table emergency_cases enable row level security;
alter table optimization_runs enable row level security;
alter table procurement_actions enable row level security;
alter table clinical_constraints enable row level security;

do $$
begin
  create policy "public read blood_banks" on blood_banks for select using (true);
exception when duplicate_object then null;
end $$;

do $$
begin
  create policy "public read inventory" on blood_inventory for select using (true);
exception when duplicate_object then null;
end $$;

do $$
begin
  create policy "public read couriers" on couriers for select using (true);
exception when duplicate_object then null;
end $$;

do $$
begin
  create policy "public read emergency_cases" on emergency_cases for select using (true);
exception when duplicate_object then null;
end $$;

do $$
begin
  create policy "public read optimization_runs" on optimization_runs for select using (true);
exception when duplicate_object then null;
end $$;

do $$
begin
  create policy "public read procurement_actions" on procurement_actions for select using (true);
exception when duplicate_object then null;
end $$;

do $$
begin
  create policy "public read clinical_constraints" on clinical_constraints for select using (true);
exception when duplicate_object then null;
end $$;
