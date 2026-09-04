import numpy as np

def get_chlorophyll_data(lat_min: float = 7.0, lon_min: float = 77.0, lat_max: float = 14.0, lon_max: float = 82.0) -> dict:
    rng = np.random.default_rng(seed=42)
    
    # Pre-defined centers, mostly near coast and river mouths
    centers = [
        (10.3, 79.8),  # Cauvery delta
        (11.7, 79.9),  # Cuddalore
        (9.3, 79.3),   # Rameswaram
        (8.1, 77.5),   # Kanyakumari
        (13.0, 80.3),  # Chennai
        (8.8, 78.2),   # Tuticorin
        (10.7, 79.8),  # Nagapattinam
        (12.5, 80.2),  # Kalpakkam
    ]
    
    features = []
    
    for i, (lat_c, lon_c) in enumerate(centers):
        # Determine concentration
        val = rng.uniform(0.2, 8.0)
        # Force higher concentration near Cauvery delta
        if (lat_c, lon_c) == (10.3, 79.8):
            val = rng.uniform(5.0, 8.0)
            
        if val < 1:
            level = "low"
        elif val <= 3:
            level = "medium"
        else:
            level = "high"
            
        # Create a simple polygon around the center
        lat_offset = rng.uniform(0.1, 0.25)
        lon_offset = rng.uniform(0.1, 0.25)
        
        polygon = [
            [lon_c - lon_offset, lat_c - lat_offset],
            [lon_c + lon_offset, lat_c - lat_offset],
            [lon_c + lon_offset, lat_c + lat_offset],
            [lon_c - lon_offset, lat_c + lat_offset],
            [lon_c - lon_offset, lat_c - lat_offset] # close the polygon
        ]
        
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [polygon]
            },
            "properties": {
                "chl_a_mg_m3": round(val, 2),
                "concentration_level": level
            }
        }
        features.append(feature)
        
    return {
        "type": "FeatureCollection",
        "features": features
    }
