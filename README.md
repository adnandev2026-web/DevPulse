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
