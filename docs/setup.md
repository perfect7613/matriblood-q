# MatriBlood Q Local Setup

## Python API with uv

```bash
uv venv
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload --app-dir services/api
```

Health check:

```bash
curl http://localhost:8001/health
```

Run tests:

```bash
uv run pytest services/api/tests
```

## Next.js Dashboard

```bash
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

## Supabase

The project uses a remote Supabase project for demo state. Apply:

```text
supabase/migrations/001_matriblood_schema.sql
supabase/seed.sql
```

The schema is intentionally small and demo-focused:

- blood banks / pharmacies
- blood inventory
- couriers
- emergency cases
- optimization runs
- procurement actions
- clinical constraints

## Environment

Copy `.env.example` to `.env.local`, then fill the local values.

Never commit `.env.local`.
