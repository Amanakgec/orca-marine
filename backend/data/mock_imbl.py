import json
import os

def get_imbl_boundary() -> dict:
    file_path = os.path.join(os.path.dirname(__file__), '../../frontend/public/data/india-imbl.geojson')
    if not os.path.exists(file_path):
        return {"type": "FeatureCollection", "features": []}
        
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Inject boundary_type property expected by backend validation
    for feature in data.get('features', []):
        props = feature.get('properties', {})
        props['boundary_type'] = "IMBL"
        props['country_pair'] = props.get('LINE_NAME', 'International Maritime Boundary')
        props['description'] = f"Boundary between {props.get('TERRITORY1', '')} and {props.get('TERRITORY2', '')}"
        feature['properties'] = props
        
    return data
