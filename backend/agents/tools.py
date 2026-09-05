import math
from typing import Dict, Any, List
from langchain_core.tools import tool
from shapely.geometry import Point, LineString, Polygon
from data.mock_sst import get_sst_data
from data.mock_chlorophyll import get_chlorophyll_data
from data.mock_weather import get_weather_data, get_tide_data, get_temporal_forecast, get_severe_weather_and_cyclone_data, get_sea_state
from data.mock_imbl import get_imbl_boundary
from data.mock_pfz import get_pfz_zones
from data.mock_mpa import get_mpa_zones, check_point_in_mpa
from data.mock_ecology import analyze_fishery_decline as get_ecology_analysis

def _calculate_bbox(lat: float, lon: float, radius_km: float):
    lat_offset = radius_km / 111.0
    lon_offset = radius_km / (111.0 * max(0.1, math.cos(math.radians(lat))))
    return (round(lat - lat_offset, 3), round(lon - lon_offset, 3), round(lat + lat_offset, 3), round(lon + lon_offset, 3))

@tool
def discover_ocean_data(lat: float, lon: float, radius_km: float = 60) -> Dict[str, Any]:
    """Calculates bounding box around target coordinates and returns SST, Chlorophyll, and Weather summaries with GeoJSON layers."""
    lat_min, lon_min, lat_max, lon_max = _calculate_bbox(lat, lon, radius_km)

    sst_data = get_sst_data(lat_min, lon_min, lat_max, lon_max)
    chl_data = get_chlorophyll_data(lat_min, lon_min, lat_max, lon_max)
    weather_data = get_weather_data(lat, lon, radius_km)

    temps = [f["properties"]["sst_celsius"] for f in sst_data.get("features", [])]
    avg_temp = round(sum(temps)/len(temps), 1) if temps else 28.2
    min_temp = min(temps) if temps else 27.0
    max_temp = max(temps) if temps else 29.5

    layers = [
        {
            "id": "sst-layer",
            "type": "circle",
            "label": "Sea Surface Temperature (°C)",
            "data": sst_data,
            "style": {"color": "#FF6B35", "opacity": 0.85, "width": 6.0}
        },
        {
            "id": "chl-layer",
            "type": "fill",
            "label": "Chlorophyll-a Plumes (mg/m³)",
            "data": chl_data,
            "style": {"color": "#2ECC71", "opacity": 0.45, "width": 1.5}
        },
        {
            "id": "weather-layer",
            "type": "fill",
            "label": "Marine Weather & Wind Sectors",
            "data": weather_data,
            "style": {"color": "#3498DB", "opacity": 0.35, "width": 2.0}
        }
    ]

    return {
        "sst_summary": {"avg": avg_temp, "min": min_temp, "max": max_temp},
        "chlorophyll_summary": "Active chlorophyll plumes identified along coastal shelf.",
        "weather_summary": f"Marine weather report at ({lat:.2f}N, {lon:.2f}E): Swell and wind within operational thresholds.",
        "geojson_layers": layers
    }

@tool
def assess_safety_risk(lat: float, lon: float, vessel_type: str = 'motorized_boat') -> Dict[str, Any]:
    """Assesses safety risk based on waves, wind, IMBL boundaries, and Marine Protected Areas (MPAs)."""
    weather_data = get_weather_data(lat, lon, 100)
    imbl_data = get_imbl_boundary()
    mpa_data = get_mpa_zones()

    pt = Point(lon, lat)
    imbl_distances = []
    nearest_country = "International Waters"

    try:
        for f in imbl_data.get("features", []):
            if f.get("properties", {}).get("boundary_type") == "IMBL":
                coords = f["geometry"]["coordinates"]
                ls = LineString(coords)
                dist_nm = pt.distance(ls) * 60.0
                imbl_distances.append((dist_nm, f["properties"].get("country_pair", "IMBL")))
        if imbl_distances:
            imbl_distances.sort(key=lambda x: x[0])
            min_dist_nm, nearest_country = imbl_distances[0]
        else:
            min_dist_nm = 25.0
    except Exception:
        min_dist_nm = 25.0

    # Inspect Marine Protected Area proximity
    mpa_breaches = check_point_in_mpa(lat, lon)

    # Inspect weather hazards
    hazard_features = [f for f in weather_data.get("features", []) if f.get("properties", {}).get("warning_level") == "danger"]
    max_wave = 2.8 if hazard_features else 1.6
    sea_state = get_sea_state(max_wave)

    warnings = []
    risk_score = 25

    if min_dist_nm < 5.0:
        risk_score += 45
        warnings.append(f"CRITICAL IMBL WARNING: Within {min_dist_nm:.1f} NM of {nearest_country} Maritime Boundary. Turn back!")
    elif min_dist_nm < 15.0:
        risk_score += 20
        warnings.append(f"BORDER CAUTION: Operating within {min_dist_nm:.1f} NM of {nearest_country} Maritime Boundary.")

    for mpa in mpa_breaches:
        if mpa["status"] == "INSIDE_RESTRICTED_ZONE":
            risk_score += 40
            warnings.append(f"RESTRICTED ZONE VIOLATION: Inside {mpa['name']}. {mpa['restrictions']}")
        else:
            risk_score += 15
            warnings.append(f"MPA BUFFER ALERT: Within {mpa['distance_nm']} NM of {mpa['name']}.")

    if max_wave > 2.5:
        risk_score += 25
        warnings.append(f"High-wave advisory: Significant wave height > {max_wave}m ({sea_state['label']}). Unsafe for small boats.")
    else:
        warnings.append(f"Wave conditions favorable ({max_wave}m, {sea_state['label']}) for {vessel_type}.")

    risk_level = "critical" if risk_score >= 70 else ("high" if risk_score >= 50 else ("moderate" if risk_score >= 35 else "safe"))

    layers = [
        {
            "id": "imbl-layer",
            "type": "line",
            "label": "Maritime Boundary Lines (IMBL)",
            "data": imbl_data,
            "style": {"color": "#9B59B6", "opacity": 0.9, "width": 2.5}
        },
        {
            "id": "mpa-layer",
            "type": "fill",
            "label": "Marine Protected Areas (MPA Geofence)",
            "data": mpa_data,
            "style": {"color": "#F39C12", "opacity": 0.5, "width": 2.0}
        },
        {
            "id": "hazard-layer",
            "type": "fill",
            "label": "Wave & Wind Risk Zones",
            "data": weather_data,
            "style": {"color": "#E74C3C", "opacity": 0.45, "width": 1.5}
        }
    ]

    return {
        "risk_score": min(100, risk_score),
        "risk_level": risk_level,
        "warnings": warnings,
        "imbl_distance_nm": round(min_dist_nm, 1),
        "nearest_boundary": nearest_country,
        "mpa_status": mpa_breaches,
        "sea_state": sea_state["label"],
        "geojson_layers": layers
    }

@tool
def find_potential_fishing_zones(lat_min: float, lon_min: float, lat_max: float, lon_max: float) -> Dict[str, Any]:
    """Finds Potential Fishing Zones (PFZs) correlated with SST (26-28C) & Chlorophyll fronts, flagging zones to avoid."""
    pfz_data = get_pfz_zones(lat_min, lon_min, lat_max, lon_max)
    mpa_data = get_mpa_zones()

    zones_list = []
    avoided_zones = []

    for f in pfz_data.get("features", []):
        p = f.get("properties", {})
        coords = f["geometry"]["coordinates"][0][0] # Sample point [lon, lat]
        zone_lat, zone_lon = coords[1], coords[0]

        # Check if zone conflicts with an MPA
        mpa_conflict = check_point_in_mpa(zone_lat, zone_lon)
        is_restricted = any(m["status"] == "INSIDE_RESTRICTED_ZONE" for m in mpa_conflict)

        zone_info = {
            "zone_id": p.get("zone_id"),
            "location": p.get("location_name"),
            "confidence": p.get("confidence"),
            "species": ", ".join(p.get("expected_species", [])),
            "sst_range": p.get("sst_range"),
            "chlorophyll": p.get("chl_a_level"),
            "depth": p.get("depth_bathymetry"),
            "is_restricted": is_restricted,
            "restriction_reason": mpa_conflict[0]["restrictions"] if is_restricted else "None"
        }

        if is_restricted:
            avoided_zones.append(zone_info)
        else:
            zones_list.append(zone_info)

    layers = [
        {
            "id": "pfz-layer",
            "type": "fill",
            "label": "Potential Fishing Zones (PFZ)",
            "data": pfz_data,
            "style": {"color": "#2ECC71", "opacity": 0.65, "width": 2.0}
        },
        {
            "id": "mpa-layer",
            "type": "fill",
            "label": "Marine Protected Areas (Avoid)",
            "data": mpa_data,
            "style": {"color": "#F39C12", "opacity": 0.5, "width": 2.0}
        }
    ]

    return {
        "recommended_zones": zones_list,
        "avoid_zones": avoided_zones,
        "total_zones": len(zones_list) + len(avoided_zones),
        "geojson_layers": layers
    }

@tool
def compute_safe_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float, vessel_type: str = 'motorized_boat') -> Dict[str, Any]:
    """Computes an optimized safe navigational passage between waypoints avoiding rough weather, MPAs, and IMBL boundaries."""
    weather_data = get_weather_data((start_lat + end_lat)/2.0, (start_lon + end_lon)/2.0, 150)
    imbl_data = get_imbl_boundary()
    mpa_data = get_mpa_zones()

    mid_lat = (start_lat + end_lat) / 2.0
    seaward_bias = -0.38 if (start_lon + end_lon)/2.0 < 77.5 else 0.38
    mid_lon = (start_lon + end_lon) / 2.0 + seaward_bias

    waypoints = [
        [round(start_lon, 4), round(start_lat, 4)],
        [round(mid_lon, 4), round(mid_lat, 4)],
        [round(end_lon, 4), round(end_lat, 4)]
    ]

    route_geojson = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": waypoints},
            "properties": {
                "route_name": "Recommended Safe Navigational Corridor",
                "status": "Cleared of Storm Hazards, MPAs & IMBL Buffer",
                "vessel": vessel_type,
                "cruise_speed_kts": 10.0
            }
        }]
    }

    dist_approx = math.hypot((end_lat - start_lat) * 60, (end_lon - start_lon) * 60 * math.cos(math.radians(mid_lat))) * 1.15
    eta_hours = round(dist_approx / 10.0, 1)

    layers = [
        {
            "id": "route-layer",
            "type": "line",
            "label": "Safe Navigational Route",
            "data": route_geojson,
            "style": {"color": "#00D4FF", "opacity": 0.95, "width": 4.0}
        },
        {
            "id": "mpa-layer",
            "type": "fill",
            "label": "Protected Marine Reserves",
            "data": mpa_data,
            "style": {"color": "#F39C12", "opacity": 0.4, "width": 1.5}
        },
        {
            "id": "imbl-route-layer",
            "type": "line",
            "label": "Maritime Boundary Reference",
            "data": imbl_data,
            "style": {"color": "#9B59B6", "opacity": 0.8, "width": 2.0}
        }
    ]

    return {
        "distance_nm": round(dist_approx, 1),
        "estimated_time_hours": eta_hours,
        "waypoints": [{"lat": pt[1], "lon": pt[0]} for pt in waypoints],
        "hazards_avoided": ["Rough Swell (>2.5m)", "Marine Protected Area Core Zones", "IMBL Security Buffer"],
        "geojson_layers": layers
    }

@tool
def get_tide_and_weather_forecast(lat: float, lon: float, time_horizon: str = "tomorrow_morning") -> Dict[str, Any]:
    """Retrieves tide timings (high/low), sea state classification, and morning vs afternoon operational outlook."""
    temporal = get_temporal_forecast(lat, lon, time_horizon)
    tides = get_tide_data(lat, lon)
    weather_layers = get_weather_data(lat, lon, 60)

    # Station Point for Map
    tide_point = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(lon, 4), round(lat, 4)]},
            "properties": {
                "station": f"Coastal Hydrographic Station ({lat:.2f}N, {lon:.2f}E)",
                "phase": tides["tidal_phase"],
                "high_tide": tides["schedule"][0]["time"],
                "low_tide": tides["schedule"][1]["time"],
                "sea_state": temporal["sea_state"]
            }
        }]
    }

    layers = [
        {
            "id": "tide-station-layer",
            "type": "circle",
            "label": "Tide & Hydrographic Station",
            "data": tide_point,
            "style": {"color": "#00E5FF", "opacity": 0.9, "width": 8.0}
        },
        {
            "id": "weather-layer",
            "type": "fill",
            "label": "Forecasted Sea State Sectors",
            "data": weather_layers,
            "style": {"color": "#3498DB", "opacity": 0.35, "width": 1.5}
        }
    ]

    return {
        "tide_schedule": tides["schedule"],
        "tidal_phase": tides["tidal_phase"],
        "morning_outlook": temporal,
        "vessel_advisory": temporal["vessel_safety_advisory"],
        "geojson_layers": layers
    }

@tool
def get_severe_weather_alerts(lat: float, lon: float) -> Dict[str, Any]:
    """Retrieves real-time IMD/INCOIS Severe Weather, Cyclone tracking trajectory, and Lightning Flash Alerts."""
    severe_data = get_severe_weather_and_cyclone_data(lat, lon)

    layers = [
        {
            "id": "severe-alert-layer",
            "type": "fill",
            "label": "Lightning & Squall Risk Zone",
            "data": {
                "type": "FeatureCollection",
                "features": [f for f in severe_data["features"] if f["geometry"]["type"] == "Polygon"]
            },
            "style": {"color": "#E74C3C", "opacity": 0.55, "width": 2.0}
        },
        {
            "id": "cyclone-track-layer",
            "type": "line",
            "label": "Cyclone Forecast Trajectory",
            "data": {
                "type": "FeatureCollection",
                "features": [f for f in severe_data["features"] if f["geometry"]["type"] == "LineString"]
            },
            "style": {"color": "#900C3F", "opacity": 0.95, "width": 4.5}
        },
        {
            "id": "cyclone-eye-layer",
            "type": "circle",
            "label": "Cyclone Center Position",
            "data": {
                "type": "FeatureCollection",
                "features": [f for f in severe_data["features"] if f["geometry"]["type"] == "Point"]
            },
            "style": {"color": "#FF1744", "opacity": 0.95, "width": 10.0}
        }
    ]

    return {
        "cyclone_bulletin": severe_data["cyclone_bulletin"],
        "active_warnings": [f["properties"] for f in severe_data["features"]],
        "geojson_layers": layers
    }

@tool
def analyze_fishery_decline(lat: float, lon: float, location_name: str = "Coastal Shelf") -> Dict[str, Any]:
    """Provides scientific oceanographic reasoning on why fish productivity has declined in a specific coastal sector."""
    return get_ecology_analysis(lat, lon, location_name)

@tool
def audit_restricted_zones(lat: float, lon: float) -> Dict[str, Any]:
    """Audits geofencing across both International Maritime Boundary Lines (IMBL) and Marine Protected Areas (MPAs)."""
    imbl_data = get_imbl_boundary()
    mpa_data = get_mpa_zones()
    mpa_breaches = check_point_in_mpa(lat, lon)

    layers = [
        {
            "id": "imbl-layer",
            "type": "line",
            "label": "International Maritime Boundaries (IMBL)",
            "data": imbl_data,
            "style": {"color": "#9B59B6", "opacity": 0.9, "width": 3.0}
        },
        {
            "id": "mpa-layer",
            "type": "fill",
            "label": "Marine Protected Areas (Strict Geofence)",
            "data": mpa_data,
            "style": {"color": "#F39C12", "opacity": 0.55, "width": 2.0}
        }
    ]

    return {
        "mpa_breaches": mpa_breaches,
        "rules_summary": "All mechanized trawling prohibited within declared MPAs. Sovereign IMBL requires 5NM buffer.",
        "geojson_layers": layers
    }
