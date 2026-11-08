# little lines

A Bengali caption library with an Astro + Tailwind site and admin panel backed by Django APIs.

## Run locally

1. Start Django:
   ```sh
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```
2. In another terminal, start Astro:
   ```sh
   cd frontend
   npm install
   npm run dev
   ```
3. Open <http://localhost:4321> for the public site and <http://localhost:4321/admin/> for the admin workspace. The legacy Django admin URL at <http://localhost:8000/admin/> redirects to the Astro panel; the Django admin fallback is at `/django-admin/`.

Caption reads, writes, login sessions, and likes are handled by Django. The Astro admin calls Django with session cookies and CSRF protection. Saved captions and duplicate-like prevention are stored in the viewer's browser. Set `PUBLIC_API_URL` in the frontend environment to point at Django outside local development. Configure Django's `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, and `DJANGO_DEBUG` for deployment.

## Turso database

Django uses local SQLite by default. To use the configured Turso database, copy `backend/.env.example` to `backend/.env` and set `TURSO_DATABASE_URL` and `TURSO_AUTH_TOKEN`. The local `.env` is ignored by Git. Then run `python manage.py migrate`; the backend uses Django's ORM with the `django-libsql-backend` driver. The existing captions and admin account have already been copied to the configured Turso database.

Remote Turso connections use HTTP. The Django driver documents that remote transactions are buffered and best-effort, so keep migrations and bulk write operations small and verify critical changes. Without Turso environment variables, development falls back to `backend/db.sqlite3`.

## Deploy frontend and backend together on Render

This repository includes a single-service Docker deployment. In Render, choose **New → Blueprint**, connect this repository, and apply `render.yaml`. Enter `TURSO_DATABASE_URL` and `TURSO_AUTH_TOKEN` when prompted. Render builds Astro into the Django image, then Django serves the public site at `/`, the admin at `/admin/`, and the API at `/api/` from the same origin. The container applies Django migrations when it starts.

For a manual web service, use the repository root and the included `Dockerfile`. Set `DJANGO_SECRET_KEY` to a generated secret and `DJANGO_DEBUG=0`; set Turso credentials in Render's Environment page. Do not put credentials in `render.yaml` or commit a `.env` file.
