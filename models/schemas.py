from dataclasses import asdict, dataclass
from typing import Any, Optional


@dataclass
class Camera:
    id: str
    name: str
    category: str
    city: str
    state: str
    country: str
    lat: float
    lon: float
    type: str
    embed_url: str
    status: str
    provider: str
    last_updated: str
    fallback_stream: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SatelliteLayer:
    id: str
    name: str
    category: str
    type: str
    url_template: str
    attribution: str
    opacity: float
    update_interval: str
    description: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EarthImageryLayer:
    id: str
    name: str
    provider: str
    time: str
    url_template: str
    attribution: str
    update_frequency: str
    description: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
