# Cozy Weather & Live Earth Platform

Cozy Weather is a modern environmental intelligence platform combining real-time weather analytics, 5-day forecasts, custom clothing recommendations, air quality monitoring, and an interactive **Live Earth** observation portal (`/live-earth`).

**Developer:** Miles

---

## 🌟 Key Features

- **Current Weather Dashboard (`/` & `/weather`):** Instant search for any location globally with metric (°C, m/s) and imperial (°F, mph) unit toggling, day/night sky visuals, clothing advice, and Air Quality Index (AQI) ratings.
- **Detailed Forecast Breakdown (`/forecast`):** Deep-dive 3-hour forecast views with wind vectors, precipitation probability, rain/snow volume, pressure, and humidity.
- **🌍 Live Earth Portal (`/live-earth`):**
  - **Interactive World Map:** Built on Leaflet.js with CartoDB Dark Matter & Esri Satellite base maps, zoom/pan controls, Locate Me, Fullscreen, and marker clusters.
  - **Verified Public & Traffic Cameras:** Filter by category (Traffic, Airports, Harbors, Public Webcams) and location (Lagos, London, Paris, Tokyo, Dubai, New York, etc.). Displays official public stream embeds or clear fallback messaging when no public camera exists.
  - **Weather Satellite Layers:** Overlay global cloud cover, RainViewer real-time precipitation radar, thermal temperature maps, and wind speed vectors.
  - **Earth Observation Imagery:** Daily high-resolution satellite imagery from NASA GIBS (Terra MODIS / VIIRS) and NASA Black Marble night lights.
  - **Favorites System:** Save favorite locations, webcams, and satellite views using local browser storage.
  - **Live Status Panel:** Real-time connection status, active data provider, camera count, and refresh timers.

---

## 🚀 Setup & Installation

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Configure environment variables in `.env`:
   ```text
   OPENWEATHER_API_KEY=your_openweather_api_key_here
   GROK_API_KEY=your_grok_api_key_here
   WINDY_WEBCAMS_API_KEY=your_windy_webcams_api_key_here
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
   Navigate to `http://localhost:5000` (or `http://localhost:5000/live-earth`).

5. Run test suite:
   ```bash
   py -3 -m pytest
   ```

---

## 📡 Integrated Public APIs & Data Sources

| Provider | Layer / Feature | Config Required |
| :--- | :--- | :--- |
| **OpenWeatherMap** | Current weather, forecast, geocoding, cloud & temp tiles | `OPENWEATHER_API_KEY` (Required for weather data) |
| **RainViewer** | Global real-time precipitation radar tiles | *Free / Open (No key required)* |
| **NASA GIBS** | MODIS & VIIRS daily Earth observation satellite tiles | *Free / Open (No key required)* |
| **CartoDB & OpenStreetMap** | Dark-mode base map tiles | *Free / Open (No key required)* |
| **Esri World Imagery** | High-resolution satellite basemap | *Free / Open (No key required)* |
| **Public Transport DOTs** | London TfL, NYC DOT, Lagos LASTMA, Shibuya Traffic feeds | *Free / Public Embeds* |
| **Windy Webcams** | Expanded global webcam directory | `WINDY_WEBCAMS_API_KEY` (Optional) |

---

## 🌐 Deployment

### Render Deployment
1. Create a new Web Service in Render connected to your repository.
2. Configure Environment Variables in Render Dashboard:
   - `OPENWEATHER_API_KEY`
   - `GROK_API_KEY` (Optional)
   - `WINDY_WEBCAMS_API_KEY` (Optional)
3. Build Command:
   ```bash
   pip install -r requirements.txt
   ```
4. Start Command:
   ```bash
   gunicorn --bind 0.0.0.0:$PORT wsgi:app
   ```

### GitHub Actions CI/CD
The repository includes `.github/workflows/deploy.yml` which automatically runs Pytest unit tests on push to `main` and triggers deployment to Render using `RENDER_API_KEY` and `RENDER_SERVICE_ID`.
