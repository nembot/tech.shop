# Repository Guidelines

## Project Structure & Module Organization

This is a Django marketplace rooted at `app_web/`. Run Django commands from that directory; `manage.py` is the entry point and `app_web/` holds project settings and URL routes. The `blog/` app implements the public catalogue, cart, checkout, authentication, and product models. The `momo/` app implements the seller dashboard, article management, orders, and statistics. Keep templates and static assets within their owning app, for example `blog/templates/`, `momo/templates/`, and each app's `static/` directory. Add schema changes as new numbered files under `blog/migrations/`; do not edit applied migrations.

## Build, Test, and Development Commands

From `app_web/`, create an isolated environment and install the pinned dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Use `python manage.py test` to run the Django test suite, and run `python manage.py makemigrations` followed by `python manage.py migrate` after changing models. Static MDB assets are checked in; there is no repository frontend build command.

## Coding Style & Naming Conventions

Write Python with four-space indentation and PEP 8-friendly spacing. Use `PascalCase` for models and class-based views, `snake_case` for functions, variables, and template context keys, and descriptive URL names such as `toggle-publish`. Keep views focused: place data rules in models or forms when they can be reused. Prefer Django ORM queries over raw SQL and use `get_object_or_404` for object lookups exposed by URLs. Preserve the existing French user-facing copy unless the feature requires a deliberate wording change.

## Testing Guidelines

Use Django's `TestCase` in each app's `tests.py`. Name tests `test_<behavior>`, for example `test_unpublished_article_is_hidden`. Cover changed model behavior, access control, POST-only mutations, and the relevant response or redirect. Run the full suite before opening a pull request; no coverage threshold is configured.

## Commit & Pull Request Guidelines

Recent history uses Conventional Commit-style subjects, e.g. `fix(design): improve checkout accessibility`. Use a concise `type(scope): summary` subject. Pull requests should state the user-visible change, list migrations or configuration effects, confirm the test command run, and include screenshots for template or styling changes.

## Configuration & Security

Do not commit `.env`, SQLite databases, uploaded media, or production credentials. Before deployment, supply a private `SECRET_KEY`, set `DEBUG=False`, restrict `ALLOWED_HOSTS`, and configure production database and media storage outside the repository.
