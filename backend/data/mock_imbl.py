def get_imbl_boundary() -> dict:
    features = []
    
    # Approximate IMBL
    imbl_coords = [
        [79.5, 10.5],
        [79.6, 10.3],
        [79.8, 10.1],
        [80.0, 9.9],
        [80.2, 9.7],
        [79.5, 9.0],
        [79.0, 8.5]
    ]
    
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": imbl_coords
        },
        "properties": {
            "boundary_type": "IMBL",
            "description": "India-Sri Lanka Maritime Boundary Line"
        }
    })
    
    # 12nm line (approximate)
    tw_12nm_coords = [
        [80.4, 13.5],
        [80.0, 11.5],
        [79.9, 10.5],
        [79.0, 9.0],
        [77.7, 8.0]
    ]
    
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": tw_12nm_coords
        },
        "properties": {
            "boundary_type": "territorial_12nm",
            "description": "12 Nautical Miles Territorial Waters Line"
        }
    })
    
    # 2nm line (approximate)
    tw_2nm_coords = [
        [80.3, 13.5],
        [79.9, 11.5],
        [79.8, 10.5],
        [79.1, 9.0],
        [77.6, 8.0]
    ]
    
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": tw_2nm_coords
        },
        "properties": {
            "boundary_type": "territorial_2nm",
            "description": "2 Nautical Miles Waters Line"
        }
    })
    
    return {
        "type": "FeatureCollection",
        "features": features
    }
