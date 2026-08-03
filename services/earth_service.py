from datetime import datetime, timedelta, UTC
from config.settings import NASA_GIBS_URL_TEMPLATE


def get_earth_imagery_layers() -> list[dict]:
    """Retrieve NASA GIBS & Multi-Provider Earth Observation imagery tile layers."""
    # Use 2 days prior to guarantee complete global orbital composite synthesis
    recent_date = (datetime.now(UTC) - timedelta(days=2)).strftime("%Y-%m-%d")
    
    layers = [
        {
            "id": "nasa-modis-terra",
            "name": "NASA Terra MODIS (True Color)",
            "provider": "NASA EOSDIS / GIBS",
            "time": recent_date,
            "url_template": NASA_GIBS_URL_TEMPLATE.format(
                layer="MODIS_Terra_CorrectedReflectance_TrueColor",
                time=recent_date,
                z="{z}",
                y="{y}",
                x="{x}",
            ),
            "attribution": "Imagery provided by NASA GIBS, part of EOSDIS",
            "opacity": 0.90,
            "update_frequency": "Daily Orbital Pass Snapshots",
            "description": "True-color satellite imagery captured by NASA's Terra satellite sensor.",
        },
        {
            "id": "nasa-viirs-snpp",
            "name": "NASA VIIRS SNPP (High-Res Visible)",
            "provider": "NASA EOSDIS / GIBS",
            "time": recent_date,
            "url_template": NASA_GIBS_URL_TEMPLATE.format(
                layer="VIIRS_SNPP_CorrectedReflectance_TrueColor",
                time=recent_date,
                z="{z}",
                y="{y}",
                x="{x}",
            ),
            "attribution": "Imagery provided by NASA GIBS, part of EOSDIS",
            "opacity": 0.90,
            "update_frequency": "Daily Snapshots",
            "description": "High-resolution visible Earth observation imagery from Suomi NPP satellite.",
        },
        {
            "id": "nasa-noaa-20",
            "name": "NASA NOAA-20 VIIRS True Color",
            "provider": "NASA EOSDIS / GIBS",
            "time": recent_date,
            "url_template": NASA_GIBS_URL_TEMPLATE.format(
                layer="VIIRS_NOAA20_CorrectedReflectance_TrueColor",
                time=recent_date,
                z="{z}",
                y="{y}",
                x="{x}",
            ),
            "attribution": "Imagery provided by NASA GIBS / NOAA-20",
            "opacity": 0.90,
            "update_frequency": "Daily Snapshots",
            "description": "Next-generation polar-orbiting satellite sensor true-color imagery.",
        },
        {
            "id": "goes-east",
            "name": "GOES-East Geostationary (Americas)",
            "provider": "NOAA / NESDIS / NASA GIBS",
            "time": recent_date,
            "url_template": "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/GOES-East_ABI_Band2_Red/default/{time}/GoogleMapsCompatible_Level9/{{z}}/{{y}}/{{x}}.jpg".format(time=recent_date),
            "attribution": "Imagery provided by NOAA / NASA GIBS",
            "opacity": 0.85,
            "update_frequency": "Geostationary 10-Minute Feed",
            "description": "Geostationary satellite coverage over North America, South America & Atlantic Ocean.",
        },
        {
            "id": "goes-west",
            "name": "GOES-West Geostationary (Pacific)",
            "provider": "NOAA / NESDIS / NASA GIBS",
            "time": recent_date,
            "url_template": "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/GOES-West_ABI_Band2_Red/default/{time}/GoogleMapsCompatible_Level9/{{z}}/{{y}}/{{x}}.jpg".format(time=recent_date),
            "attribution": "Imagery provided by NOAA / NASA GIBS",
            "opacity": 0.85,
            "update_frequency": "Geostationary 10-Minute Feed",
            "description": "Geostationary satellite coverage over Hawaii, Alaska, and Pacific Ocean.",
        },
        {
            "id": "meteosat",
            "name": "Meteosat Geostationary (Europe & Africa)",
            "provider": "EUMETSAT / NASA GIBS",
            "time": recent_date,
            "url_template": "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Aqua_CorrectedReflectance_TrueColor/default/{time}/GoogleMapsCompatible_Level9/{{z}}/{{y}}/{{x}}.jpg".format(time=recent_date),
            "attribution": "EUMETSAT / NASA GIBS",
            "opacity": 0.85,
            "update_frequency": "Geostationary Feed",
            "description": "Composite satellite coverage across Europe, Africa, and the Indian Ocean.",
        },
        {
            "id": "himawari",
            "name": "Himawari Geostationary (Asia & Australia)",
            "provider": "JMA / NASA GIBS",
            "time": recent_date,
            "url_template": "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/Himawari_AHI_Band3_Red/default/{time}/GoogleMapsCompatible_Level9/{{z}}/{{y}}/{{x}}.jpg".format(time=recent_date),
            "attribution": "Japan Meteorological Agency / NASA GIBS",
            "opacity": 0.85,
            "update_frequency": "Geostationary 10-Minute Feed",
            "description": "Geostationary satellite imagery over East Asia, Australia, and Western Pacific.",
        },
        {
            "id": "nasa-night-lights",
            "name": "NASA Black Marble (Earth at Night)",
            "provider": "NASA EOSDIS / GIBS",
            "time": "2016-01-01",
            "url_template": "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_Black_Marble/default/2016-01-01/GoogleMapsCompatible_Level8/{z}/{y}/{x}.png",
            "attribution": "Imagery provided by NASA GIBS / Black Marble",
            "opacity": 0.85,
            "update_frequency": "Global Mosaic Archive",
            "description": "Global composite view of human settlement and city night lights observed from space.",
        },
    ]
    return layers
