insert into blood_banks (id, name, source_type, eta_minutes, phone, is_tie_up_partner) values
  ('bank-a', 'Blood Bank A', 'blood_bank', 8, '+91-080-0000-1001', true),
  ('bank-b', 'Blood Bank B', 'blood_bank', 18, '+91-080-0000-1002', true),
  ('bank-c', 'Blood Bank C', 'blood_bank', 25, '+91-080-0000-1003', true),
  ('pharmacy-d', 'Pharmacy D', 'pharmacy', 14, '+91-080-0000-2001', true)
on conflict (id) do update set
  name = excluded.name,
  source_type = excluded.source_type,
  eta_minutes = excluded.eta_minutes,
  phone = excluded.phone,
  is_tie_up_partner = excluded.is_tie_up_partner;

delete from blood_inventory where source_id in ('bank-a', 'bank-b', 'bank-c', 'pharmacy-d');

insert into blood_inventory (source_id, product_type, blood_group, units_available, expires_at, notes) values
  ('bank-a', 'PRBC', 'O-', 1, null, null),
  ('bank-a', 'FFP', 'O-', 2, null, null),
  ('bank-b', 'PRBC', 'O-', 1, null, null),
  ('bank-b', 'platelets', 'O-', 1, now() + interval '8 hours', 'Near-expiry but valid in demo window'),
  ('bank-b', 'FFP', 'O-', 1, null, null),
  ('bank-c', 'PRBC', 'O-', 4, null, null),
  ('bank-c', 'FFP', 'O-', 4, null, null),
  ('bank-c', 'platelets', 'O-', 2, null, null),
  ('pharmacy-d', 'tranexamic_acid', null, 5, null, null),
  ('pharmacy-d', 'oxytocin', null, 3, null, null);

insert into couriers (id, name, capacity_units, available) values
  ('courier-1', 'Courier 1', 4, true),
  ('courier-2', 'Courier 2', 4, true)
on conflict (id) do update set
  name = excluded.name,
  capacity_units = excluded.capacity_units,
  available = excluded.available;

insert into emergency_cases (
  id,
  transcript,
  case_type,
  patient_status,
  target_minutes,
  urgency_score,
  required_products,
  missing_fields,
  parser_confidence,
  status
) values (
  'case-pph-001',
  'Postpartum hemorrhage emergency. Patient unstable. Need 2 O negative PRBC, 2 FFP, 1 platelet, tranexamic acid and oxytocin within 30 minutes.',
  'postpartum_hemorrhage',
  'unstable',
  30,
  10,
  '[
    {"product_type":"PRBC","blood_group":"O-","units":2,"critical":true},
    {"product_type":"FFP","blood_group":"O-","units":2,"critical":true},
    {"product_type":"platelets","blood_group":"O-","units":1,"critical":true},
    {"product_type":"tranexamic_acid","blood_group":null,"units":1,"critical":true},
    {"product_type":"oxytocin","blood_group":null,"units":1,"critical":true}
  ]'::jsonb,
  '[]'::jsonb,
  1,
  'seeded'
) on conflict (id) do update set
  transcript = excluded.transcript,
  required_products = excluded.required_products,
  status = excluded.status;

insert into clinical_constraints (item_name, item_type, storage_rule, urgency_role, compatibility_note, citation_url, notes) values
  ('Postpartum hemorrhage', 'condition', null, 'High urgency obstetric emergency', 'This system supports procurement only, not treatment decisions.', 'https://www.who.int/publications/i/item/9789240081802', 'WHO roadmap source for problem framing.'),
  ('Platelets', 'blood_component', 'Short shelf-life; use valid near-expiry inventory when clinically appropriate.', 'Critical in selected bleeding scenarios when requested by clinician.', 'Compatibility simplified for MVP and must be validated by specialists.', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC12822613/', 'Used as science-backed demo constraint.')
on conflict do nothing;
