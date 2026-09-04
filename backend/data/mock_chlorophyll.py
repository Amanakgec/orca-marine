import numpy as np

def get_chlorophyll_data(lat_min: float = 7.0, lon_min: float = 68.0, lat_max: float = 24.0, lon_max: float = 90.0) -> dict:
    rng = np.random.default_rng(seed=int(abs(lat_min * 50 + lon_min * 20)) % 10000 + 101)
    features = []

    # Generate 5-8 chlorophyll concentration plumes within the requested coastal bounding box
    center_lat = (lat_min + lat_max) / 2.0
    center_lon = (lon_min + lon_max) / 2.0

    num_patches = rng.integers(4, 7)
    for i in range(num_patches):
        c_lat = rng.uniform(lat_min + 0.1, lat_max - 0.1) if (lat_max - lat_min > 0.3) else center_lat + rng.uniform(-0.2, 0.2)
        c_lon = rng.uniform(lon_min + 0.1, lon_max - 0.1) if (lon_max - lon_min > 0.3) else center_lon + rng.uniform(-0.2, 0.2)

        val = round(rng.uniform(1.2, 7.8), 2)
        level = "high" if val > 3.0 else ("medium" if val >= 1.5 else "low")

        lat_offset = rng.uniform(0.12, 0.3)
        lon_offset = rng.uniform(0.12, 0.3)

        polygon = [
            [round(c_lon - lon_offset, 4), round(c_lat - lat_offset, 4)],
            [round(c_lon + lon_offset, 4), round(c_lat - lat_offset, 4)],
            [round(c_lon + lon_offset, 4), round(c_lat + lat_offset, 4)],
            [round(c_lon - lon_offset, 4), round(c_lat + lat_offset, 4)],
            [round(c_lon - lon_offset, 4), round(c_lat - lat_offset, 4)]
        ]

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [polygon]
            },
            "properties": {
                "chl_a_mg_m3": val,
                "concentration_level": level,
                "phytoplankton_index": round(val * 1.3, 2),
                "notes": f"{level.capitalize()} chlorophyll-a density zone favorable for marine food web."
            }
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }
