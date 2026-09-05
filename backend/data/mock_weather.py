import numpy as np
from datetime import datetime, timedelta, timezone

def get_sea_state(wave_height_m: float) -> dict:
    """Returns WMO / Douglas Sea State classification."""
    if wave_height_m < 0.5:
        return {"code": 1, "label": "Calm (Rippled)", "safe_for_small_craft": True}
    elif wave_height_m < 1.25:
        return {"code": 2, "label": "Smooth", "safe_for_small_craft": True}
    elif wave_height_m < 2.0:
        return {"code": 3, "label": "Slight / Moderate", "safe_for_small_craft": True}
    elif wave_height_m < 3.0:
        return {"code": 4, "label": "Rough", "safe_for_small_craft": False}
    elif wave_height_m < 4.0:
        return {"code": 5, "label": "Very Rough", "safe_for_small_craft": False}
    else:
        return {"code": 6, "label": "High / Dangerous", "safe_for_small_craft": False}

def get_tide_data(lat: float = 13.0, lon: float = 80.2) -> dict:
    """Computes realistic diurnal/semi-diurnal tide cycles for Indian coastal harbors."""
    rng = np.random.default_rng(seed=int(abs(lat * 100 + lon * 10)) % 10000 + 11)

    base_tide = round(rng.uniform(1.8, 3.8), 2)
    min_tide = round(base_tide * 0.22, 2)
    phase = "Spring Tide (High Amplitude)" if base_tide > 2.8 else "Neap Tide (Moderate Amplitude)"

    # Realistic timings
    h1_hour = int(rng.integers(4, 7))
    h1_min = int(rng.integers(10, 55))
    l1_hour = h1_hour + 6
    l1_min = (h1_min + 15) % 60
    h2_hour = (h1_hour + 12) % 24
    h2_min = (h1_min + 30) % 60
    l2_hour = (h2_hour + 6) % 24
    l2_min = (h2_min + 20) % 60

    return {
        "tidal_phase": phase,
        "max_high_tide_m": base_tide,
        "min_low_tide_m": min_tide,
        "current_tidal_state": "Flooding (Rising Tide)" if rng.random() > 0.5 else "Ebbing (Falling Tide)",
        "tidal_stream_velocity_knots": round(rng.uniform(0.8, 2.4), 1),
        "schedule": [
            {"type": "High Tide", "time": f"{h1_hour:02d}:{h1_min:02d} AM", "height_m": base_tide},
            {"type": "Low Tide", "time": f"{l1_hour:02d}:{l1_min:02d} PM", "height_m": min_tide},
            {"type": "High Tide", "time": f"{h2_hour:02d}:{h2_min:02d} PM", "height_m": round(base_tide * 0.94, 2)},
            {"type": "Low Tide", "time": f"{l2_hour:02d}:{l2_min:02d} AM (Next Day)", "height_m": round(min_tide * 1.1, 2)}
        ]
    }

def get_temporal_forecast(lat: float, lon: float, time_horizon: str = "tomorrow_morning") -> dict:
    """Computes dedicated morning vs afternoon operational weather outlook."""
    rng = np.random.default_rng(seed=int(abs(lat * 100 + lon * 10)) % 10000 + 44)

    morning_wave = round(rng.uniform(0.9, 1.8), 2)
    morning_wind = round(rng.uniform(12, 22), 1)
    afternoon_wave = round(morning_wave + rng.uniform(0.6, 1.3), 2)
    afternoon_wind = round(morning_wind + rng.uniform(8, 16), 1)

    sea_state_morning = get_sea_state(morning_wave)
    sea_state_afternoon = get_sea_state(afternoon_wave)

    tides = get_tide_data(lat, lon)

    # Vessel suitability
    small_craft_safe = morning_wave < 1.8 and morning_wind < 28
    trawler_safe = morning_wave < 2.8 and morning_wind < 38

    return {
        "time_window": "Tomorrow Morning (05:00 AM - 11:00 AM)",
        "wave_height_m": morning_wave,
        "wind_speed_kmh": morning_wind,
        "wind_direction": "NE" if lon > 77.5 else "NW",
        "sea_state": f"Sea State {sea_state_morning['code']} ({sea_state_morning['label']})",
        "morning_high_tide": tides["schedule"][0],
        "afternoon_outlook": {
            "time_window": "Tomorrow Afternoon (12:00 PM - 06:00 PM)",
            "wave_height_m": afternoon_wave,
            "wind_speed_kmh": afternoon_wind,
            "sea_state": f"Sea State {sea_state_afternoon['code']} ({sea_state_afternoon['label']})"
        },
        "vessel_safety_advisory": {
            "traditional_vallam_country_craft": "SAFE for inshore waters" if morning_wave < 1.3 else "CAUTION: Nearshore chop expected",
            "motorized_fiber_boat": "RECOMMENDED: Favorable morning conditions" if small_craft_safe else "CAUTION: Return before 11 AM as afternoon swell increases",
            "mechanized_trawler": "EXCELLENT: Full clearance for continental shelf operations" if trawler_safe else "CAUTION"
        }
    }

def get_severe_weather_and_cyclone_data(lat: float, lon: float) -> dict:
    """Generates IMD/INCOIS Severe Weather, Cyclone tracking paths, and Lightning Risk Polygons."""
    rng = np.random.default_rng(seed=int(abs(lat * 100 + lon * 10)) % 10000 + 88)
    sea_basin = "Arabian Sea" if lon < 77.5 else "Bay of Bengal"
    features = []

    # 1. Convective Thunderstorm & Lightning Flash Risk Zone
    lightning_center_lat = lat + 0.35
    lightning_center_lon = lon + 0.45
    radius_deg = 0.35
    lightning_poly = [
        [round(lightning_center_lon - radius_deg, 4), round(lightning_center_lat - radius_deg, 4)],
        [round(lightning_center_lon + radius_deg, 4), round(lightning_center_lat - radius_deg, 4)],
        [round(lightning_center_lon + radius_deg, 4), round(lightning_center_lat + radius_deg, 4)],
        [round(lightning_center_lon - radius_deg, 4), round(lightning_center_lat + radius_deg, 4)],
        [round(lightning_center_lon - radius_deg, 4), round(lightning_center_lat - radius_deg, 4)]
    ]

    features.append({
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [lightning_poly]
        },
        "properties": {
            "alert_type": "LIGHTNING_AND_SQUALL_ALERT",
            "severity": "HIGH",
            "lightning_flash_density": "12-18 flashes/sq.km/hr",
            "squall_gusts_kmh": round(rng.uniform(45, 65), 1),
            "valid_period": "Next 6 Hours",
            "action": "Fishermen in small boats advised to suspend line fishing and seek sheltered harbor immediately."
        }
    })

    # 2. Regional Tropical Disturbance / Cyclone Trajectory & Cone of Uncertainty
    # Simulate track moving towards coast
    cyclone_name = "Deep Depression (AS-02)" if lon < 77.5 else "Cyclonic Storm 'MIDHILI' (BOB-04)"
    track_pts = [
        [round(lon + 1.8, 4), round(lat - 1.2, 4)],
        [round(lon + 1.2, 4), round(lat - 0.6, 4)],
        [round(lon + 0.6, 4), round(lat, 4)],
        [round(lon - 0.2, 4), round(lat + 0.8, 4)]
    ]

    features.append({
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": track_pts
        },
        "properties": {
            "alert_type": "CYCLONE_TRACK",
            "system_name": cyclone_name,
            "max_sustained_wind_kts": 55,
            "central_pressure_hpa": 988,
            "basin": sea_basin,
            "movement_speed": "14 km/h northwestwards"
        }
    })

    # Cyclone Eye current position
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": track_pts[2]
        },
        "properties": {
            "alert_type": "CYCLONE_EYE",
            "system_name": cyclone_name,
            "category": "Cyclonic Storm (IMD Scale)",
            "warning": "Gale wind speed reaching 65-75 kmph gusting to 85 kmph over surrounding waters."
        }
    })

    return {
        "type": "FeatureCollection",
        "features": features,
        "cyclone_bulletin": {
            "system": cyclone_name,
            "current_location": f"{track_pts[2][1]}°N, {track_pts[2][0]}°E",
            "distance_from_port_km": round(rng.uniform(85, 140), 1),
            "alert_status": "Orange Warning (Be Prepared)",
            "advisory": "Total suspension of fishing operations in the affected deep-sea sector. Small craft should not venture into sea."
        }
    }

def get_weather_data(lat: float = 13.0, lon: float = 80.2, radius_km: float = 100) -> dict:
    """Returns general multi-zone marine weather polygon layers."""
    rng = np.random.default_rng(seed=int(abs(lat * 100 + lon * 10)) % 10000 + 7)
    features = []

    sea_basin = "Arabian Sea" if lon < 77.5 else "Bay of Bengal"
    # Seaward direction: West for Arabian Sea (negative lon), East for Bay of Bengal (positive lon)
    seaward_sign = -1.0 if lon < 77.5 else 1.0

    # Ensure all offshore weather polygons are placed strictly in maritime waters (never inland on subcontinent)
    offsets = [
        (0.0, seaward_sign * 0.45),
        (-0.5, seaward_sign * 0.85),
        (0.5, seaward_sign * 0.70),
        (-0.9, seaward_sign * 1.20)
    ]

    for i, (d_lat, d_lon) in enumerate(offsets):
        c_lat = lat + d_lat
        c_lon = lon + d_lon

        wind = round(rng.uniform(12, 38), 1)
        wave = round(rng.uniform(0.8, 3.2), 1)
        vis = round(rng.uniform(6, 18), 1)

        if i == 1:
            wave = round(rng.uniform(2.4, 3.6), 1)
            wind = round(rng.uniform(30, 44), 1)

        sea_state = get_sea_state(wave)
        warning = 'danger' if (wave > 2.5 or wind > 35) else ('caution' if (wave > 1.8 or wind > 24) else 'safe')

        lat_off = 0.40
        lon_off = 0.40

        polygon = [
            [round(c_lon - lon_off, 4), round(c_lat - lat_off, 4)],
            [round(c_lon + lon_off, 4), round(c_lat - lat_off, 4)],
            [round(c_lon + lon_off, 4), round(c_lat + lat_off, 4)],
            [round(c_lon - lon_off, 4), round(c_lat + lat_off, 4)],
            [round(c_lon - lon_off, 4), round(c_lat - lat_off, 4)]
        ]

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [polygon]
            },
            "properties": {
                "zone_label": f"{sea_basin} Sector {chr(65+i)}",
                "wind_speed_kmh": wind,
                "wave_height_m": wave,
                "sea_state": f"State {sea_state['code']} ({sea_state['label']})",
                "visibility_km": vis,
                "warning_level": warning,
                "swell_direction": "SW" if lon < 77.5 else "NE"
            }
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }
