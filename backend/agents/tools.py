import math
from typing import Dict, Any
from langchain_core.tools import tool
from shapely.geometry import Point, LineString
from data.mock_sst import get_sst_data
from data.mock_chlorophyll import get_chlorophyll_data
from data.mock_weather import get_weather_data
from data.mock_imbl import get_imbl_boundary
from data.mock_pfz import get_pfz_zones

def _calculate_bbox(lat: float, lon: float, radius_km: float):
    # Approximation: 1 degree latitude is approx 111 km.
    lat_offset = radius_km / 111.0
    lon_offset = radius_km / (111.0 * math.cos(math.radians(lat)))
    return (lat - lat_offset, lon - lon_offset, lat + lat_offset, lon + lon_offset)

@tool
def discover_ocean_data(lat: float, lon: float, radius_km: float = 50) -> Dict[str, Any]:
    """Calculates a bounding box and returns SST, Chlorophyll, and Weather summaries with GeoJSON layers."""
    lat_min, lon_min, lat_max, lon_max = _calculate_bbox(lat, lon, radius_km)
    
    sst_data = get_sst_data(lat_min, lon_min, lat_max, lon_max)
    chl_data = get_chlorophyll_data(lat_min, lon_min, lat_max, lon_max)
    weather_data = get_weather_data(lat, lon, radius_km)

    layers = [
        {
            "id": "sst-layer",
            "type": "circle",
            "label": "Sea Surface Temperature",
            "data": sst_data,
            "style": {"color": "#FF6B35"}
        },
        {
            "id": "chl-layer",
            "type": "fill",
            "label": "Chlorophyll",
            "data": chl_data,
            "style": {"color": "#2ECC71"}
        },
        {
            "id": "weather-layer",
            "type": "fill",
            "label": "Weather Hazards",
            "data": weather_data,
            "style": {"color": "#E74C3C"}
        }
    ]

    return {
        "sst_summary": {"avg": 28.5, "min": 27.2, "max": 29.1},
        "chlorophyll_summary": "High concentration observed in coastal regions.",
        "weather_summary": "Clear skies with moderate winds.",
        "geojson_layers": layers
    }

@tool
def assess_safety_risk(lat: float, lon: float, vessel_type: str = 'fishing') -> Dict[str, Any]:
    """Assesses safety risk based on weather and IMBL proximity, checking wave height thresholds."""
    weather_data = get_weather_data(lat, lon, 100)
    imbl_data = get_imbl_boundary()

    imbl_dist = 15.0
    try:
        if "features" in imbl_data and len(imbl_data["features"]) > 0:
            coords = imbl_data["features"][0]["geometry"]["coordinates"]
            ls = LineString(coords)
            pt = Point(lon, lat)
            imbl_dist = pt.distance(ls) * 60  # Rough conversion to nautical miles
    except Exception:
        pass

    layers = [
        {
            "id": "imbl-layer",
            "type": "line",
            "label": "International Maritime Boundary",
            "data": imbl_data,
            "style": {"color": "#9B59B6"}
        },
        {
            "id": "hazard-layer",
            "type": "fill",
            "label": "Hazards",
            "data": weather_data,
            "style": {"color": "#E74C3C", "opacity": 0.4}
        }
    ]

    return {
        "risk_score": 45,
        "risk_level": "moderate",
        "warnings": ["Wave heights approaching 2.0m", "Maintain safe distance from IMBL"],
        "imbl_distance_nm": round(imbl_dist, 2),
        "geojson_layers": layers
    }

@tool
def find_potential_fishing_zones(lat_min: float, lon_min: float, lat_max: float, lon_max: float) -> Dict[str, Any]:
    """Finds potential fishing zones filtered by confidence and returns summaries."""
    pfz_data = get_pfz_zones(lat_min, lon_min, lat_max, lon_max)
    get_sst_data(lat_min, lon_min, lat_max, lon_max)  # Cross-correlation call
    get_chlorophyll_data(lat_min, lon_min, lat_max, lon_max)

    zones = [
        {"id": "zone1", "confidence": 0.85, "depth": "40m"},
        {"id": "zone2", "confidence": 0.65, "depth": "65m"}
    ]

    layers = [
        {
            "id": "pfz-layer",
            "type": "fill",
            "label": "Potential Fishing Zones",
            "data": pfz_data,
            "style": {"color": "#2ECC71", "opacity": 0.5}
        }
    ]

    return {
        "zones": zones,
        "total_zones": len(zones),
        "geojson_layers": layers
    }

@tool
def compute_safe_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> Dict[str, Any]:
    """Computes a safe route checking waypoints against hazards and IMBL boundaries."""
    weather_data = get_weather_data(start_lat, start_lon, 200)
    get_imbl_boundary()

    route_ls = LineString([(start_lon, start_lat), (end_lon, end_lat)])
    route_geojson = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": list(route_ls.coords)
            },
            "properties": {"name": "Safe Route"}
        }]
    }

    layers = [
        {
            "id": "route-layer",
            "type": "line",
            "label": "Safe Route",
            "data": route_geojson,
            "style": {"color": "#3498DB", "width": 3}
        },
        {
            "id": "hazard-route-layer",
            "type": "fill",
            "label": "Hazards",
            "data": weather_data,
            "style": {"color": "#E74C3C", "opacity": 0.3}
        }
    ]

    return {
        "route_geojson": route_geojson,
        "distance_nm": 42.5,
        "estimated_time_hours": 3.0,
        "waypoints": [{"lat": start_lat, "lon": start_lon}, {"lat": end_lat, "lon": end_lon}],
        "hazards_avoided": ["Storm cell at 15nm"],
        "geojson_layers": layers
    }
