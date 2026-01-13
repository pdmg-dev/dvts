# Copilot / AI Agent Instructions — dvts

This file captures concise, actionable knowledge an AI coding agent needs to be productive in this Flask repository.

## Big picture

- App factory: `create_app` in `app/__init__.py` constructs the Flask app and registers three blueprints: `auth`, `voucher`, `admin`.
- Database: SQLAlchemy models live in `app/models/` (see `app/models/voucher.py` for patterns: timestamp columns, relationships, cascade rules).
- Migrations: Alembic/Flask-Migrate is used; migration files are in `migrations/`.
- Assets & UI: Jinja templates under `app/templates/`, modular blueprint templates in `app/blueprints/*/templates`. HTMX is used (returns fragment templates when `HX-Request` header present).
- Realtime: `flask-socketio` is initialized via `app/extensions.py` and `socketio.init_app(app)` — websocket support exists and `eventlet` is a dependency.

## How to run (developer workflow)

- Virtualenv: project typically uses a venv at `.venv`. Activate it before commands: `source .venv/bin/activate`.
- Flask entrypoint: `.flaskenv` sets `FLASK_APP=app:create_app` and dev port (`5500`). Use `flask run` for normal development:

  ```bash
  source .venv/bin/activate
  flask run
  ```

- SocketIO (if you need the WebSocket server and full realtime behavior): run via `socketio.run` so the SocketIO server is used (eventlet is installed):

  ```bash
  python -c "from app import create_app, socketio; socketio.run(create_app(), host='0.0.0.0', port=5500)"
  ```

- Database migrations:
  - `flask db migrate -m "msg"`
  - `flask db upgrade`
  - Migration files live in `migrations/`.

## Project conventions and patterns (concrete examples)

- Config selection: `app/config.py` reads `FLASK_ENV` and returns `DevelopmentConfig` / `TestingConfig` / `ProductionConfig`. Set `DATABASE_URL`, `SECRET_KEY` in environment to override defaults.
- Uploads: routes expect `current_app.config['UPLOAD_FOLDER']` (see `app/blueprints/voucher/routes.py`). Ensure this config key is set in environment or Config if you work with attachments.
- HTMX fragments: routes frequently return fragment templates when `request.headers.get('HX-Request')` is truthy — prefer returning only the fragment when implementing or changing HTMX endpoints.
- Templates: project uses Prettier with `prettier-plugin-jinja-template` for HTML/Jinja formatting (see `package.json`). Python formatting/linting: Black + Ruff (configured in `pyproject.toml` and `.pre-commit-config.yaml`).

## Tests & CI

- There are no automated tests in the repo. When adding tests, follow existing patterns (use `app.create_app` to create an app instance, use `TestingConfig` from `app/config.py` to point at `sqlite:///test.db`).

## Helpful files to inspect when coding

- App factory and blueprint registration: [app/**init**.py](app/__init__.py)
- Config logic: [app/config.py](app/config.py)
- Extensions (db, socketio, migrate, login): [app/extensions.py](app/extensions.py)
- Example CRUD and HTMX patterns: [app/blueprints/voucher/routes.py](app/blueprints/voucher/routes.py)
- Data model example: [app/models/voucher.py](app/models/voucher.py)
- Migrations and Alembic: `migrations/`
- Local DB file (dev): `instance/dev.db`

## When proposing changes, prefer:

- Small, atomic changes that update both templates and routes together for HTMX behavior.
- Preserving existing SQLAlchemy naming and relationship patterns (see `category`, `resp_center`, `attachments` in `DisbursementVoucher`).
- Adding `UPLOAD_FOLDER` config or reading it from environment rather than hardcoding paths.

If anything is ambiguous or you need project-specific credentials/ENV values (e.g., `UPLOAD_FOLDER`, `DATABASE_URL`, or a production socket server config), ask the repo owner. Ready to iterate on any section you'd like expanded.
