# Weather Bot

A simple Flask weather dashboard using the OpenWeather API.

## Setup

1. Copy `.env.example` to `.env`.
2. Add your OpenWeather API key to `.env`:

```text
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

3. Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. Run locally:

```bash
py -3 app.py
```

## Deployment

### Render

1. Create a new Web Service in Render.
2. Connect your GitHub repo.
3. Set the environment variable in Render Dashboard:

- `OPENWEATHER_API_KEY`

4. Build command:

```bash
pip install -r requirements.txt
```

5. Start command:

```bash
gunicorn --bind 0.0.0.0:$PORT wsgi:app
```

### GitHub Actions

The repo currently contains a GitHub Actions workflow at `.github/workflows/deploy.yml` that deploys to Heroku. If you are using Render instead, you can remove or disable that workflow.
