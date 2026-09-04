import numpy as np
from datetime import datetime, timezone

def get_sst_data(lat_min: float = 7.0, lon_min: float = 77.0, lat_max: float = 14.0, lon_max: float = 82.0) -> dict:
    rng = np.random.default_rng(seed=42)
    lats = np.arange(lat_min, lat_max + 0.5, 0.5)
    lons = np.arange(lon_min, lon_max + 0.5, 0.5)
    
    features = []
    timestamp = datetime.now(timezone.utc).isoformat()
    
    for lat in lats:
        for lon in lons:
            # Warmer near equator (lower lat), cooler further north. Base roughly 27 at equator.
            base_temp = 29.0 - (lat - 7.0) * 0.3
            noise = rng.normal(0, 0.5)
            temp = float(np.clip(base_temp + noise, 24.0, 30.0))
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(lon), float(lat)]
                },
                "properties": {
                    "sst_celsius": round(temp, 2),
                    "timestamp": timestamp
                }
            }
            features.append(feature)
            
    return {
        "type": "FeatureCollection",
        "features": features
    }
