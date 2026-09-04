import numpy as np
from datetime import datetime, timedelta, timezone

def get_weather_data(lat: float = 13.0, lon: float = 80.2, radius_km: float = 100) -> dict:
    rng = np.random.default_rng(seed=42)
    features = []
    
    # 3-4 weather zones (Polygons)
    centers = [
        (lat, lon), 
        (lat - 1.5, lon - 0.5), 
        (lat + 2.0, lon + 1.0),
        (lat - 3.0, lon + 0.5)
    ]
    
    for i, (c_lat, c_lon) in enumerate(centers):
        wind = rng.uniform(5, 45)
        wave = rng.uniform(0.3, 4.5)
        vis = rng.uniform(2, 20)
        
        # Make one zone explicitly dangerous
        if i == 1:
            wave = rng.uniform(3.0, 4.5)
            wind = rng.uniform(35, 45)
            
        if wave > 2.5 or wind > 35:
            warning = 'danger'
        elif wave > 1.5 or wind > 20:
            warning = 'caution'
        else:
            warning = 'safe'
            
        lat_off = 0.5
        lon_off = 0.5
        
        polygon = [
            [c_lon - lon_off, c_lat - lat_off],
            [c_lon + lon_off, c_lat - lat_off],
            [c_lon + lon_off, c_lat + lat_off],
            [c_lon - lon_off, c_lat + lat_off],
            [c_lon - lon_off, c_lat - lat_off]
        ]
        
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [polygon]
            },
            "properties": {
                "wind_speed_kmh": round(wind, 1),
                "wave_height_m": round(wave, 1),
                "visibility_km": round(vis, 1),
                "warning_level": warning
            }
        })
        
    # Specific alerts (Points)
    now = datetime.now(timezone.utc)
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [lon + 0.2, lat - 0.2] # Arbitrary offset
        },
        "properties": {
            "alert_type": "Cyclone Warning",
            "severity": "High",
            "description": "Cyclonic storm forming over Bay of Bengal.",
            "valid_until": (now + timedelta(hours=48)).isoformat()
        }
    })
    
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [lon - 0.5, lat + 1.0]
        },
        "properties": {
            "alert_type": "Lightning",
            "severity": "Medium",
            "description": "Intense lightning observed in this region.",
            "valid_until": (now + timedelta(hours=6)).isoformat()
        }
    })
        
    return {
        "type": "FeatureCollection",
        "features": features
    }
