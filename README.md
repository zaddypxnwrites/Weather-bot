# Cozy Trading Bot

A Flask dashboard project currently using weather data APIs, rebranded as Cozy Trading Bot.

## Setup

1. Copy `.env.example` to `.env`.
2. Add your OpenWeather API key and Grok API key to `.env`:

```text
OPENWEATHER_API_KEY=your_openweather_api_key_here
GROK_API_KEY=your_grok_api_key_here
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

The repo contains a GitHub Actions workflow at `.github/workflows/deploy.yml` that runs tests and triggers a Render deploy.

To use the workflow, add the following GitHub repository secrets:

- `RENDER_API_KEY`
- `RENDER_SERVICE_ID`

Once the repo is connected to Render and the secrets are configured, pushes to `main` will run tests and request a Render deployment.
