from datetime import datetime, timedelta, UTC
from config.settings import NASA_GIBS_URL_TEMPLATE


def get_earth_imagery_layers() -> list[dict]:
    """Retrieve NASA GIBS Earth Observation imagery tile layers with current date stamps."""
    yesterday = (datetime.now(UTC) - timedelta(days=1)).strftime("%Y-%m-%d")
    
    layers = [
        {
            "id": "nasa-modis-terra",
            "name": "NASA MODIS Terra Corrected Reflectance",
            "provider": "NASA Earth Science Data and Information System (ESDIS) / GIBS",
            "time": yesterday,
            "url_template": NASA_GIBS_URL_TEMPLATE.format(
                layer="MODIS_Terra_CorrectedReflectance_TrueColor",
                time=yesterday,
                z="{z}",
                y="{y}",
                x="{x}",
            ),
            "attribution": "Imagery provided by NASA GIBS, part of EOSDIS",
            "opacity": 0.90,
            "update_frequency": "Daily Snapshots (Once per day per satellite pass)",
            "description": "True-color satellite imagery captured by NASA's Terra satellite sensor.",
        },
        {
            "id": "nasa-viirs-snpp",
            "name": "NASA VIIRS SNPP True Color",
            "provider": "NASA Earth Science Data and Information System (ESDIS) / GIBS",
            "time": yesterday,
            "url_template": NASA_GIBS_URL_TEMPLATE.format(
                layer="VIIRS_SNPP_CorrectedReflectance_TrueColor",
                time=yesterday,
                z="{z}",
                y="{y}",
                x="{x}",
            ),
            "attribution": "Imagery provided by NASA GIBS, part of EOSDIS",
            "opacity": 0.90,
            "update_frequency": "Daily Snapshots (Once per day per satellite pass)",
            "description": "High-resolution visible Earth observation imagery from the Suomi NPP satellite.",
        },
        {
            "id": "nasa-night-lights",
            "name": "NASA VIIRS Earth at Night (City Lights)",
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
