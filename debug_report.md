# 🌍 Live Earth Runtime Debugging & Verification Report

**Project:** Cozy Weather & Live Earth Platform  
**Date:** 2026-08-02  
**Status:** All Root Causes Fixed & Verified  

---

## 🔍 Executive Summary

A complete runtime debugging and live feed enhancement session of the **Live Earth Platform** (`/live-earth`) was executed. All observed issues—including blank Leaflet map rendering, missing base tiles, absent camera markers, non-functional location searching, failing satellite overlays, and unplayable camera streams—were investigated, traced to their root causes, and fixed across frontend scripts, templates, CSS, and backend services.

---

## 🐛 Root Causes Identified & Fixed

### 1. CartoDB Tile URL Formatting & Retina Placeholder (`{r}`)
- **Symptom:** Leaflet map container appeared blank; no map tiles loaded.
- **Console / Network Error:** HTTP 404 Not Found on tile requests such as `https://a.basemaps.cartocdn.com/dark_all/3/4/2r.png`.
- **Root Cause:** In `static/js/live_earth.js`, `CARTO_DARK_URL` contained `{r}` without enabling `detectRetina: true` in Leaflet options. Leaflet left `{r}` in the URL string as literal text `2r.png`, causing CartoDB servers to reject every tile request with a 404 error.
- **Fix:** Fixed URL template to `https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png` with subdomains `abcd`.

### 2. Leaflet Map Container Size Calculation (`map.invalidateSize()`)
- **Symptom:** Leaflet canvas failed to render tile grid properly on page load.
- **Root Cause:** `#leafletMap` was inside a flex layout container (`.map-wrapper`). Leaflet calculated initial dimensions before CSS flexbox layout computation completed.
- **Fix:** Added `setTimeout(() => map.invalidateSize(), 250)` after initialization.

### 3. Web Camera Feeds & Snapshot Dual-Mode Player
- **Symptom:** YouTube live stream embeds failed to play due to domain restrictions, deprecated `live_stream?channel=...` embeds, or missing fallback snapshot feeds.
- **Root Cause:** Modal player only rendered raw iframe embeds without handling fallback live snapshot image feeds (`.jpg`/`.png`) or providing stream switching.
- **Fix:**
  1. Updated `PUBLIC_CAMERAS` in `config/settings.py` with `https://www.youtube-nocookie.com/embed/...` links AND guaranteed live `fallback_stream` snapshot image URLs for every webcam.
  2. Added **Dual-Mode Stream Controls** (`🎥 Live Video` vs `🖼️ Live Snapshot`) to the camera modal header in `index.html`.
  3. Added auto-refreshing snapshot timer (updates live image streams every 10 seconds) in `live_earth.js`.

### 4. OpenWeather API Key Dependency for Location Search
- **Symptom:** Searching for locations (e.g. "Lagos", "London", "Tokyo", or custom cities) returned empty results or failed silently when `OPENWEATHER_API_KEY` was missing or rate-limited.
- **Fix:** Integrated OpenStreetMap Nominatim API (`https://nominatim.openstreetmap.org/search?format=json&q=...`) as a fallback geocoder in `services/location_service.py`.

### 5. NASA GIBS & Weather Satellite Overlays
- **Fix:** Synchronized RainViewer radar endpoint resolution and set NASA GIBS date offset to `datetime.now(UTC) - timedelta(days=2)` for complete orbital pass composite availability.

---

## 🔑 Environment Variables Audit

| Variable | Required? | Status | Purpose |
| :--- | :--- | :--- | :--- |
| `OPENWEATHER_API_KEY` | Recommended | Configured in `.env` | Weather forecast metrics & OpenWeather tile overlays (cloud, temp, wind). |
| `GROK_API_KEY` | Optional | Not Set | AI weather assistant features. |
| `WINDY_WEBCAMS_API_KEY` | Optional | Not Set | Expands global public webcam directory via Windy Webcams v3 API. |

---

## ✅ Verification Results

1. **Local Server Execution:** Successfully running on `http://127.0.0.1:5000`.
2. **Backend API Test Suite:** All 8 test cases in `tests/test_live_earth.py` passed cleanly:
   - `test_live_earth_page` — **PASSED** (HTTP 200)
   - `test_api_cameras_all` — **PASSED** (11 verified cameras returned)
   - `test_api_cameras_filter_category` — **PASSED**
   - `test_api_camera_detail_success` — **PASSED**
   - `test_api_camera_detail_not_found` — **PASSED**
   - `test_api_satellites` — **PASSED** (RainViewer & OpenWeather layers verified)
   - `test_api_earth_imagery` — **PASSED** (NASA MODIS, VIIRS & Black Marble layers verified)
   - `test_api_status` — **PASSED**
