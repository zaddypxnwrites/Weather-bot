import math
import os
import requests
from config.settings import PUBLIC_CAMERAS, WINDY_WEBCAMS_API_KEY
from models.schemas import Camera
from services.location_service import geocode_location


def get_all_cameras() -> list[dict]:
    """Return verified public cameras directory."""
    cameras = [Camera(**cam_data).to_dict() for cam_data in PUBLIC_CAMERAS]
    
    # Fetch additional webcams dynamically if WINDY_WEBCAMS_API_KEY is configured
    if WINDY_WEBCAMS_API_KEY:
        windy_cams = fetch_windy_webcams()
        cameras.extend(windy_cams)
        
    return cameras


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate Haversine distance between two lat/lon points in km."""
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def filter_cameras(category: str = None, query: str = None) -> list[dict]:
    """Filter cameras by category and search query, with nearest location fallbacks."""
    all_cameras = get_all_cameras()
    cameras = list(all_cameras)
    
    if category and category.lower() not in ["all", "favorites", "⭐ favorites"]:
        norm_cat = category.strip().lower().replace("🌍 ", "").replace("🚦 ", "").replace("✈ ", "").replace("🚢 ", "").replace("🏖 ", "")
        cameras = [
            cam for cam in cameras
            if norm_cat in cam["category"].lower() or norm_cat in cam["name"].lower()
        ]
        
    if query and query.strip():
        q = query.strip().lower()
        matched = [
            cam for cam in cameras
            if q in cam["city"].lower()
            or q in cam["country"].lower()
            or q in cam["state"].lower()
            or q in cam["name"].lower()
            or q in cam["category"].lower()
        ]

        if matched:
            return matched

        # Fallback: if no direct string match, geocode query and find nearest cameras by distance
        locations = geocode_location(query)
        if locations:
            target_lat = locations[0]["lat"]
            target_lon = locations[0]["lon"]
            
            # Sort all cameras by distance to target location
            sorted_by_dist = sorted(
                all_cameras,
                key=lambda c: calculate_distance(target_lat, target_lon, c["lat"], c["lon"])
            )
            # Return nearest 4 public cameras
            return sorted_by_dist[:4]
            
    return cameras


def get_camera_by_id(cam_id: str) -> dict | None:
    """Retrieve a single camera by ID."""
    all_cams = get_all_cameras()
    for cam in all_cams:
        if cam["id"] == cam_id:
            return cam
    return None


def fetch_windy_webcams() -> list[dict]:
    """Wrapper to query Windy Webcams v3 API if API key is supplied."""
    if not WINDY_WEBCAMS_API_KEY:
        return []
    
    headers = {"x-windy-api-key": WINDY_WEBCAMS_API_KEY}
    url = "https://api.windy.com/api/webcams/v2/list/limit=20?show=webcams:url,location,player"
    try:
        res = requests.get(url, headers=headers, timeout=5)
        res.raise_for_status()
        data = res.json()
        webcams = data.get("result", {}).get("webcams", [])
        results = []
        for wc in webcams:
            cam_obj = Camera(
                id=f"windy-{wc.get('id')}",
                name=wc.get("title", "Public Webcam"),
                category="Public Webcams",
                city=wc.get("location", {}).get("city", "Unknown"),
                state=wc.get("location", {}).get("region", ""),
                country=wc.get("location", {}).get("country", "Global"),
                lat=float(wc.get("location", {}).get("latitude", 0.0)),
                lon=float(wc.get("location", {}).get("longitude", 0.0)),
                type="embed",
                embed_url=wc.get("player", {}).get("day", {}).get("embed", ""),
                status="Online",
                provider="Windy Webcams API",
                last_updated="Live",
            )
            results.append(cam_obj.to_dict())
        return results
    except Exception:
        return []

