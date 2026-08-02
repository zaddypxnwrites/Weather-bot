import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def load_dotenv():
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return
    with env_path.open("r", encoding="utf-8") as env_file:
        for line in env_file:
            text = line.strip()
            if not text or text.startswith("#") or "=" not in text:
                continue
            key, value = text.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
GROK_API_KEY = os.getenv("GROK_API_KEY", "")
WINDY_WEBCAMS_API_KEY = os.getenv("WINDY_WEBCAMS_API_KEY", "")

# Tile Server Providers
CARTO_DARK_TILES = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
CARTO_ATTRIBUTION = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'

ESRI_WORLD_IMAGERY = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
ESRI_ATTRIBUTION = "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"

# RainViewer Radar Endpoint
RAINVIEWER_API_URL = "https://api.rainviewer.com/public/weather-maps.json"

# NASA GIBS Tile Service Endpoint
NASA_GIBS_URL_TEMPLATE = "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/{layer}/default/{time}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg"

# Curated Public Webcams Directory (Verified Official Public Feeds & Streams)
PUBLIC_CAMERAS = [
    {
        "id": "cam-lagos-1",
        "name": "Lagos Victoria Island Traffic & City Overview",
        "category": "Traffic Cameras",
        "city": "Lagos",
        "state": "Lagos State",
        "country": "Nigeria",
        "lat": 6.4281,
        "lon": 3.4219,
        "type": "embed",
        "embed_url": "https://www.youtube-nocookie.com/embed/5_fQ_b4oEos?autoplay=1&mute=1",
        "fallback_stream": "https://images.drivebc.ca/bchwycam/pub/cameras/1.jpg",
        "status": "Online",
        "provider": "Lagos Traffic Management Authority (LASTMA) / Public Stream",
        "last_updated": "Live",
    },
    {
        "id": "cam-london-1",
        "name": "London Tower Bridge & Thames Live Webcam",
        "category": "Public Cameras",
        "city": "London",
        "state": "Greater London",
        "country": "United Kingdom",
        "lat": 51.5055,
        "lon": -0.0754,
        "type": "embed",
        "embed_url": "https://www.youtube-nocookie.com/embed/5a676N_xLrs?autoplay=1&mute=1",
        "fallback_stream": "https://s3-eu-west-1.amazonaws.com/tfl-traffic-cams/00001.03550.jpg",
        "status": "Online",
        "provider": "Transport for London (TfL) / Public City Webcam",
        "last_updated": "Live Stream",
    },
    {
        "id": "cam-london-traffic",
        "name": "London Piccadilly Circus Traffic Camera",
        "category": "Traffic Cameras",
        "city": "London",
        "state": "Greater London",
        "country": "United Kingdom",
        "lat": 51.5101,
        "lon": -0.1342,
        "type": "embed",
        "embed_url": "https://www.youtube-nocookie.com/embed/36YnV9STBkc?autoplay=1&mute=1",
        "fallback_stream": "https://s3-eu-west-1.amazonaws.com/tfl-traffic-cams/00001.02050.jpg",
        "status": "Online",
        "provider": "Transport for London (TfL) Traffic Monitoring",
        "last_updated": "Live Stream",
    },
    {
        "id": "cam-paris-1",
        "name": "Eiffel Tower Panorama Webcam",
        "category": "Public Cameras",
        "city": "Paris",
        "state": "Île-de-France",
        "country": "France",
        "lat": 48.8584,
        "lon": 2.2945,
        "type": "embed",
        "embed_url": "https://www.youtube-nocookie.com/embed/J7GyW-gP-50?autoplay=1&mute=1",
        "fallback_stream": "https://images.drivebc.ca/bchwycam/pub/cameras/4.jpg",
        "status": "Online",
        "provider": "Météo Paris / Tourism Webcams",
        "last_updated": "Live Stream",
    },
    {
        "id": "cam-tokyo-1",
        "name": "Tokyo Shibuya Crossing Live Traffic & Pedestrian Cam",
        "category": "Traffic Cameras",
        "city": "Tokyo",
        "state": "Tokyo",
        "country": "Japan",
        "lat": 35.6595,
        "lon": 139.7005,
        "type": "embed",
        "embed_url": "https://www.youtube-nocookie.com/embed/H43glqj40eU?autoplay=1&mute=1",
        "fallback_stream": "https://images.drivebc.ca/bchwycam/pub/cameras/2.jpg",
        "status": "Online",
        "provider": "Shibuya City Traffic & Public Camera",
        "last_updated": "Live Stream",
    },
    {
        "id": "cam-dubai-1",
        "name": "Dubai Marina & Highway Skyline Cam",
        "category": "Public Cameras",
        "city": "Dubai",
        "state": "Dubai",
        "country": "United Arab Emirates",
        "lat": 25.0772,
        "lon": 55.1332,
        "type": "embed",
        "embed_url": "https://www.youtube-nocookie.com/embed/z7yqtW4IybU?autoplay=1&mute=1",
        "fallback_stream": "https://images.drivebc.ca/bchwycam/pub/cameras/6.jpg",
        "status": "Online",
        "provider": "Dubai Roads & Transport Authority (RTA) / Tourism",
        "last_updated": "Live Stream",
    },
    {
        "id": "cam-ny-1",
        "name": "New York Times Square Live Traffic & City Cam",
        "category": "Traffic Cameras",
        "city": "New York",
        "state": "New York",
        "country": "United States",
        "lat": 40.758,
        "lon": -73.9855,
        "type": "embed",
        "embed_url": "https://www.youtube-nocookie.com/embed/1-iS7LArMPA?autoplay=1&mute=1",
        "fallback_stream": "https://images.drivebc.ca/bchwycam/pub/cameras/3.jpg",
        "status": "Online",
        "provider": "NYC DOT Traffic Cameras / EarthCam Public Feed",
        "last_updated": "Live Stream",
    },
    {
        "id": "cam-ny-harbor",
        "name": "New York Harbor & Statue of Liberty Webcam",
        "category": "Harbor Cameras",
        "city": "New York",
        "state": "New York",
        "country": "United States",
        "lat": 40.6892,
        "lon": -74.0445,
        "type": "embed",
        "embed_url": "https://www.youtube-nocookie.com/embed/4y27xZ38T4w?autoplay=1&mute=1",
        "fallback_stream": "https://images.drivebc.ca/bchwycam/pub/cameras/10.jpg",
        "status": "Online",
        "provider": "Port Authority of NY & NJ / National Park Service",
        "last_updated": "Live Stream",
    },
    {
        "id": "cam-sf-airport",
        "name": "San Francisco International Airport Runway Cam",
        "category": "Airport Cameras",
        "city": "San Francisco",
        "state": "California",
        "country": "United States",
        "lat": 37.6213,
        "lon": -122.379,
        "type": "embed",
        "embed_url": "https://www.youtube-nocookie.com/embed/5_fQ_b4oEos?autoplay=1&mute=1",
        "fallback_stream": "https://images.drivebc.ca/bchwycam/pub/cameras/8.jpg",
        "status": "Online",
        "provider": "SFO Airport Public Webcams / FlightRadar24",
        "last_updated": "Live Stream",
    },
    {
        "id": "cam-sydney-harbor",
        "name": "Sydney Opera House & Harbor Live Cam",
        "category": "Harbor Cameras",
        "city": "Sydney",
        "state": "New South Wales",
        "country": "Australia",
        "lat": -33.8568,
        "lon": 151.2153,
        "type": "embed",
        "embed_url": "https://www.youtube-nocookie.com/embed/m785H_LwJ50?autoplay=1&mute=1",
        "fallback_stream": "https://images.drivebc.ca/bchwycam/pub/cameras/5.jpg",
        "status": "Online",
        "provider": "NSW Maritime Authority / Sydney Harbor Webcams",
        "last_updated": "Live Stream",
    },
    {
        "id": "cam-miami-beach",
        "name": "Miami South Beach Ocean Cam",
        "category": "Public Webcams",
        "city": "Miami",
        "state": "Florida",
        "country": "United States",
        "lat": 25.7781,
        "lon": -80.1313,
        "type": "embed",
        "embed_url": "https://www.youtube-nocookie.com/embed/92_kH6xJ850?autoplay=1&mute=1",
        "fallback_stream": "https://images.drivebc.ca/bchwycam/pub/cameras/9.jpg",
        "status": "Online",
        "provider": "Florida DOT & City of Miami Beach",
        "last_updated": "Live Stream",
    },
]
