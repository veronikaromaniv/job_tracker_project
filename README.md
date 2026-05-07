# JobTracker

A web application for tracking job applications during the job search process.

**Live demo:** https://jobtrackerproject-production.up.railway.app

## Features

- Add and manage job applications with statuses (Applied, Interview, Offer, Rejected)
- Search, filter, and sort applications
- Calendar view with upcoming interviews and deadlines (FullCalendar)
- Events per job (interviews, deadlines, other)
- Export to CSV and iCal
- Authentication via Google OAuth or username/password login; new users can register directly from the login page
- User profile management
- Django Admin panel

## Tech Stack

- **Backend:** Python 3.13, Django 6.0
- **Database:** PostgreSQL (production), SQLite (development)
- **Auth:** django-allauth (Google OAuth2)
- **Frontend:** Bootstrap 5, FullCalendar 6
- **Hosting:** Railway
- **Other:** gunicorn, whitenoise, python-decouple

## Project Structure

```
job_tracker_project/
├── accounts/        # Registration, profile, CSV/iCal export
├── tracker/         # Job applications, events, calendar
├── config/
│   └── settings/
│       ├── base.py  # Shared settings
│       ├── dev.py   # Local development
│       └── prod.py  # Production (Railway)
└── templates/
    ├── base.html
    ├── account/     # Allauth templates
    ├── accounts/    # Profile template
    └── tracker/     # App templates
```

## Local Setup

1. Clone the repository:
```bash
git clone https://github.com/veronikaromaniv/job_tracker_project.git
cd job_tracker_project
```

2. Create and activate virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```
SECRET_KEY=your-secret-key
DEBUG=True
```

5. Run migrations and start the server:
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

6. Create job statuses in Django Admin (`/admin/`):
   - Applied, Interview, Offer, Rejected

## Running Tests

```bash
python manage.py test tracker accounts
```

## Deployment

The project is deployed on [Railway](https://railway.app) and configured to run automatically on push.

**How it works:**

The `Procfile` runs three commands on every deploy:
```
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn config.wsgi --log-file -
```

**Production settings** (`config/settings/prod.py`):
- `DEBUG = False`
- PostgreSQL via `DATABASE_URL`
- Static files served by WhiteNoise
- HTTPS enforced (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`)

**Required Railway environment variables:**

| Variable | Value |
|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.prod` |
| `SECRET_KEY` | your Django secret key |
| `DATABASE_URL` | set automatically by Railway PostgreSQL plugin |
| `ALLOWED_HOSTS` | your Railway domain (e.g. `yourapp.up.railway.app`) |

## Environment Variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | True for development, False for production |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts |
| `DATABASE_URL` | PostgreSQL connection URL (Railway) |
| `DJANGO_SETTINGS_MODULE` | Settings module to use |
