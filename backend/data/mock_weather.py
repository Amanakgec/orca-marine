import numpy as np
from datetime import datetime, timedelta, timezone

def get_weather_data(lat: float = 13.0, lon: float = 80.2, radius_km: float = 100) -> dict:
    rng = np.random.default_rng(seed=int(abs(lat * 100 + lon * 10)) % 10000 + 7)
    features = []

    sea_basin = "Arabian Sea" if lon < 77.5 else "Bay of Bengal"

    # 4 dynamic weather polygon zones around target coordinates
    offsets = [
        (0.0, 0.0),
        (-0.8, -0.6),
        (0.8, 0.7),
        (-1.2, 0.5)
    ]

    for i, (d_lat, d_lon) in enumerate(offsets):
        c_lat = lat + d_lat
        c_lon = lon + d_lon

        wind = round(rng.uniform(12, 42), 1)
        wave = round(rng.uniform(0.8, 3.4), 1)
        vis = round(rng.uniform(4, 18), 1)

        # Make outer zone caution/danger
        if i == 1:
            wave = round(rng.uniform(2.6, 3.8), 1)
            wind = round(rng.uniform(32, 46), 1)

        if wave > 2.5 or wind > 35:
            warning = 'danger'
        elif wave > 1.8 or wind > 24:
            warning = 'caution'
        else:
            warning = 'safe'

        lat_off = 0.45
        lon_off = 0.45

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
                "visibility_km": vis,
                "warning_level": warning,
                "swell_direction": "SW" if lon < 77.5 else "NE"
            }
        })

    # Alert point
    now = datetime.now(timezone.utc)
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [round(lon + 0.35, 4), round(lat - 0.25, 4)]
        },
        "properties": {
            "alert_type": "High Wave Advisory (>2.5m)",
            "severity": "Moderate-High",
            "sea_area": sea_basin,
            "description": f"Rough sea state observed in offshore {sea_basin}. Fishermen advised to exercise caution.",
            "valid_until": (now + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M UTC")
        }
    })

    return {
        "type": "FeatureCollection",
        "features": features
    }
