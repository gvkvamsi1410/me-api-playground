# Me-API Playground (Track A backend assessment)

Minimal playground that stores your candidate profile and exposes a small API + minimal frontend.

## What is provided
- Flask backend (SQLite) with:
  - `GET /health` → 200 OK
  - `GET /profile` → read profile
  - `POST /profile` or `PUT /profile` → create / update profile (JSON)
  - `GET /projects?skill=python` → query projects by skill / keyword
  - `POST /projects` → add project
  - `PUT /projects/<id>` → update project
  - `DELETE /projects/<id>` → delete project
  - `GET /skills/top` → top skills by frequency
  - `GET /search?q=...` → search profile & projects
- `frontend/index.html` — tiny UI (calls API via fetch)
- `seed.py` — seed DB with example real data (you can edit to put your real info)

## Requirements
- Python 3.9+
- (Optional) virtualenv/venv

## Setup & run (local)
1. Create venv & install:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
