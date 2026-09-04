import numpy as np

def get_pfz_zones(lat_min: float = 7.0, lon_min: float = 77.0, lat_max: float = 14.0, lon_max: float = 82.0) -> dict:
    rng = np.random.default_rng(seed=42)
    features = []
    
    locations = [
        ("Nagapattinam", 10.7, 79.8),
        ("Rameswaram", 9.3, 79.3),
        ("Cuddalore", 11.7, 79.9),
        ("Kanyakumari", 8.1, 77.5),
        ("Chennai_South", 12.8, 80.3)
    ]
    
    for i, (name, lat_c, lon_c) in enumerate(locations):
        lat_off = rng.uniform(0.1, 0.2)
        lon_off = rng.uniform(0.1, 0.2)
        
        polygon = [
            [lon_c - lon_off, lat_c - lat_off],
            [lon_c + lon_off, lat_c - lat_off],
            [lon_c + lon_off, lat_c + lat_off],
            [lon_c - lon_off, lat_c + lat_off],
            [lon_c - lon_off, lat_c - lat_off]
        ]
        
        conf = rng.uniform(0.6, 0.95)
        
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [polygon]
            },
            "properties": {
                "zone_id": f"PFZ_{name}_{i+1}",
                "confidence": round(conf, 2),
                "expected_species": ["Sardine", "Mackerel", "Tuna"] if conf > 0.8 else ["Sardine", "Mackerel"],
                "sst_range": "26.5 - 27.5 °C",
                "chl_a_level": "High (> 3 mg/m³)",
                "advisory": "Favorable conditions for pelagic fishing over the next 48 hours."
            }
        })
        
    return {
        "type": "FeatureCollection",
        "features": features
    }
