# Django API and database

```sh
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The Astro admin is at <http://localhost:4321/admin/>. Django provides the API at <http://localhost:8000/api/>. The legacy Django admin fallback is at `/django-admin/`.

The project defaults to local SQLite. To use Turso, copy `.env.example` to `.env`, configure `TURSO_DATABASE_URL` and `TURSO_AUTH_TOKEN`, then run `python manage.py migrate`. Do not commit `.env`. If those variables are absent, Django uses `db.sqlite3`.

Public API: `GET /api/captions/?q=...&category=...` and `POST /api/captions/<id>/like/`.
