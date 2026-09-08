def get_imbl_boundary() -> dict:
    features = []

    # 1. India - Sri Lanka International Maritime Boundary Line (Palk Strait & Gulf of Mannar)
    imbl_sri_lanka = [
        [79.51, 10.50],
        [79.62, 10.30],
        [79.78, 10.10],
        [80.05, 9.90],
        [80.20, 9.70],
        [79.80, 9.40],
        [79.50, 9.10],
        [79.10, 8.80],
        [78.80, 8.40],
        [78.30, 7.80]
    ]
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": imbl_sri_lanka
        },
        "properties": {
            "boundary_type": "IMBL",
            "country_pair": "India - Sri Lanka",
            "sector": "Palk Strait & Gulf of Mannar",
            "description": "Indo-Sri Lanka International Maritime Boundary Line (Strict No-Crossing Zone)"
        }
    })

    # 2. India - Pakistan Maritime Boundary (Sir Creek / Kutch Sector)
    imbl_pakistan = [
        [68.10, 23.65],
        [67.80, 23.30],
        [67.30, 22.80],
        [66.80, 22.20],
        [66.20, 21.50]
    ]
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": imbl_pakistan
        },
        "properties": {
            "boundary_type": "IMBL",
            "country_pair": "India - Pakistan",
            "sector": "Gujarat / Sir Creek Offshore",
            "description": "Notified Maritime Boundary Line off Kutch coast"
        }
    })

    # 3. India - Bangladesh Maritime Boundary (Bay of Bengal / Sundarbans)
    imbl_bangladesh = [
        [89.15, 21.65],
        [89.25, 21.20],
        [89.40, 20.60],
        [89.60, 19.80],
        [89.85, 18.90]
    ]
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": imbl_bangladesh
        },
        "properties": {
            "boundary_type": "IMBL",
            "country_pair": "India - Bangladesh",
            "sector": "North Bay of Bengal",
            "description": "UNCLOS Delimited Indo-Bangladesh Maritime Boundary"
        }
    })

    # 4. Coastal 12 Nautical Mile Territorial Waters (Sample coastal envelope)
    tw_east = [
        [88.20, 21.40],
        [86.80, 20.20],
        [83.45, 17.60],
        [80.40, 13.10],
        [79.95, 10.70],
        [77.60, 8.00]
    ]
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": tw_east
        },
        "properties": {
            "boundary_type": "territorial_12nm",
            "description": "East Coast 12 Nautical Miles Sovereign Territorial Waters"
        }
    })

    tw_west = [
        [77.40, 8.05],
        [76.10, 9.90],
        [74.65, 12.85],
        [73.65, 15.35],
        [72.65, 18.90],
        [69.50, 21.60],
        [68.40, 23.20]
    ]
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": tw_west
        },
        "properties": {
            "boundary_type": "territorial_12nm",
            "description": "West Coast 12 Nautical Miles Sovereign Territorial Waters"
        }
    })

    return {
        "type": "FeatureCollection",
        "features": features
    }
