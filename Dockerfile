FROM node:22-slim AS astro-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
ARG PUBLIC_API_URL=/api
ARG PUBLIC_ADMIN_URL=/admin/
ENV PUBLIC_API_URL=${PUBLIC_API_URL}
ENV PUBLIC_ADMIN_URL=${PUBLIC_ADMIN_URL}
RUN npm run build

FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ASTRO_DIST_DIR=/app/frontend-dist \
    PORT=10000
WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
COPY --from=astro-build /frontend/dist ./frontend-dist
RUN python manage.py collectstatic --noinput
EXPOSE 10000
CMD ["sh", "-c", "python manage.py migrate --noinput && exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-10000}"]
