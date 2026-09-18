# TerraLens AI

Evidence-grounded biodiversity intelligence for land stewards. TerraLens retrieves traceable environmental research, reasons across interacting landscape metrics, and produces measurable interventions with confidence, time horizon, and source provenance.

## Quick start

### Docker

```bash
docker compose up --build
```

Open `http://localhost:4173`. The API is available at `http://localhost:8000/docs`.

### Local development

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r backend/requirements-dev.txt
cd frontend
pnpm install
```

Run the API from `backend`:

```bash
../.venv/Scripts/python -m uvicorn app.main:app --reload
```

Run the client from `frontend`:

```bash
pnpm dev
```

Detailed architecture, evidence provenance, API examples, testing, and reviewer guidance are documented below as the implementation is completed.
