# Shop Project Backend

Django + DRF backend using MongoDB (MongoEngine) for a vehicle shop domain (`users`, `cars`, `spare_parts`, `tyres`, `rims`, `orders`, `inventory`).

## Local Setup

1. Create and activate virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy env file and configure values:

```bash
cp .env.example .env
```

4. Run app:

```bash
python manage.py runserver
```

Health endpoint:

```text
GET /
```

## Run Tests

```bash
python manage.py test
```

Focused inventory tests:

```bash
python manage.py test tests.test_inventory_api
```

## DigitalOcean App Platform Deployment

This repository includes:

- `Dockerfile` for production runtime (`gunicorn` on port `8080`)
- `.do/app.yaml` for App Platform configuration

### Required Steps

1. Push this repo to GitHub.
2. Update `.do/app.yaml`:
   - `github.repo`
   - `github.branch`
   - `CORS_ALLOWED_ORIGINS`
   - DigitalOcean Spaces values
3. In App Platform, create app from repo (or from spec file) and set secret env vars.

### Required Environment Variables

- `SECRET_KEY`
- `JWT_SECRET`
- `SECRET_KEY_FOR_STAFF_USER`
- `SECRET_KEY_FOR_ADMIN_USER`
- `MONGO_DB_URI`
- `MONGO_DB_NAME`
- `ALLOWED_HOSTS`
- `DEBUG=False`

Optional / media:

- `DO_SPACES_KEY`
- `DO_SPACES_SECRET`
- `DO_SPACES_BUCKET`
- `DO_SPACES_REGION`
- `DO_SPACES_ENDPOINT`
- `DO_SPACES_BASE_URL`

Optional / MongoDB Atlas TLS:

- `MONGO_TLS_CA_FILE`
- `MONGO_SERVER_SELECTION_TIMEOUT_MS`
- `MONGO_CONNECT_TIMEOUT_MS`
- `MONGO_SOCKET_TIMEOUT_MS`

## Notes

- `config/settings.py` is environment-driven and production-safe by default (`DEBUG=False`).
- Atlas connections use the system CA store plus `certifi` by default; set `MONGO_TLS_CA_FILE` only if you need to override the CA bundle path in your deployment environment.
- CORS is configurable with:
  - `CORS_ALLOW_ALL_ORIGINS`
  - `CORS_ALLOWED_ORIGINS`
- App Platform health check path is `/`.
