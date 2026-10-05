# DevPulse

DevPulse is a Django app with account registration and login, PostgreSQL-ready storage, chat groups, memberships, profiles, and group messages.

## Run locally

1. Create and activate a Python virtual environment.
2. Install dependencies with `python -m pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and set `DATABASE_URL` to your PostgreSQL connection string. Django loads `.env` automatically. Keep real credentials out of source control.
4. Run the database migrations and start the development server:

   ```powershell
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

   If `DATABASE_URL` is not set, Django uses a local SQLite database for development.

Open `http://127.0.0.1:8000/`. Visitors can view groups; creating groups, following them, and posting messages requires an account. Only group members can see and send that group's messages.

The superuser can manage accounts, groups, memberships, and messages at `http://127.0.0.1:8000/admin/`. Group messages are stored in the database and shown when the chat page reloads; live WebSocket messaging is not configured.

## Test on GitHub

Create an empty repository on GitHub, then open PowerShell in the project folder and push the code:

```powershell
git init
git add .
git commit -m "Add DevPulse Django app"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Replace the GitHub URL with your repository's URL. `.env`, local database files, and collected static files are excluded by `.gitignore`. The workflow in `.github/workflows/tests.yml` runs Django checks and the test suite against PostgreSQL whenever you push or open a pull request. To run the same checks locally:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

## Deploy from GitHub

GitHub stores your code and runs tests, but GitHub Pages cannot run Django or PostgreSQL. This repository includes `render.yaml` for deploying the Django app and creating a PostgreSQL database on Render:

1. Push the repository to GitHub and make sure the **Django tests** workflow passes.
2. Sign in to Render, choose **New → Blueprint**, and connect your GitHub repository.
3. Review the services from `render.yaml` and deploy. Render generates `DJANGO_SECRET_KEY`, connects the app to the provisioned database, and applies migrations when the service starts.
4. Once deployment succeeds, open the `onrender.com` URL provided by Render and test account creation, login, group creation, following, profiles, and chat messages.

Check Render's current pricing and database retention before choosing a plan. Never commit `.env`, database passwords, or production secrets. After pushing later code changes to the connected branch, Render can redeploy the app automatically.

## Deploy on Vercel

Vercel can run this Django project as a Python function and serve its collected static files. The project reads Vercel's deployment URL environment variables to allow the deployed host and use HTTPS-aware CSRF checks.

1. Import the GitHub repository into a Vercel project. Vercel detects Django from `manage.py`; leave the root directory at the repository root.
2. In **Project Settings → Environment Variables**, add `DJANGO_SECRET_KEY` with a new, private random value. Do not reuse the development key or publish it in GitHub.
3. Add `DATABASE_URL` with a PostgreSQL connection URL from a database provider such as Neon. The local SQLite database is not persistent on Vercel and must not be used for deployed accounts or messages.
4. Optionally add `DJANGO_DEBUG` with the value `False`; production Vercel deployments default to debug off.
5. For local development with Neon, link the project using the Neon CLI. Its ignored `.env.local` file is loaded automatically by Django. Run `python manage.py migrate` locally to create the tables in the linked Neon database.
6. Redeploy after saving the environment variables. Set `DATABASE_URL` in Vercel separately; the local `.env.local` file is not deployed.

Vercel Hobby and database-provider free plans have usage limits and terms; check that they fit your use. If you use a custom domain, add its host to `DJANGO_ALLOWED_HOSTS` and its `https://` origin to `CSRF_TRUSTED_ORIGINS`.
