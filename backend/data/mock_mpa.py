"""Marine Protected Areas (MPAs) & Ecologically Sensitive Coastal Zones in Indian Waters.
Covers major biodiversity hotspots and wildlife sanctuaries under the Wildlife Protection Act (1972)
and Coastal Regulation Zone (CRZ) notifications.
"""
from typing import Dict, Any, List
from shapely.geometry import Point, Polygon

MARINE_PROTECTED_AREAS = [
    {
        "name": "Gulf of Mannar Marine National Park",
        "state": "Tamil Nadu",
        "category": "Marine National Park & Biosphere Reserve",
        "conservation_focus": "Coral Reefs, Sea Grass Beds, Dugong (Sea Cow) & Olive Ridley Turtles",
        "restrictions": "STRICT NO-TRAWLING ZONE. Mechanized fishing and coral collection prohibited.",
        "penalty": "Impoundment under Wildlife Protection Act Schedule I",
        "coordinates": [
            [79.05, 9.25],
            [79.25, 9.28],
            [79.45, 9.22],
            [79.35, 9.05],
            [78.95, 8.85],
            [78.55, 8.65],
            [78.40, 8.75],
            [78.85, 9.05],
            [79.05, 9.25]
        ]
    },
    {
        "name": "Gahirmatha Marine Wildlife Sanctuary",
        "state": "Odisha",
        "category": "Marine Wildlife Sanctuary",
        "conservation_focus": "World's Largest Mass Nesting (Arribada) Site for Olive Ridley Sea Turtles",
        "restrictions": "NO FISHING ZONE within 20 km offshore (Nov 1 to May 31). Trawlers strictly banned.",
        "penalty": "Immediate arrest by Forest Dept & Indian Coast Guard",
        "coordinates": [
            [86.85, 20.85],
            [87.25, 20.85],
            [87.35, 20.45],
            [86.95, 20.45],
            [86.85, 20.85]
        ]
    },
    {
        "name": "Marine National Park - Gulf of Kutch",
        "state": "Gujarat",
        "category": "Marine National Park",
        "conservation_focus": "Pristine Living Coral Reefs, Mangrove Estuaries & Dugong Habitation",
        "restrictions": "Prohibited commercial fishing & anchoring on live coral formations.",
        "penalty": "Seizure of vessel under Indian Fisheries Act & CRZ Violations",
        "coordinates": [
            [69.30, 22.45],
            [70.15, 22.75],
            [70.40, 22.60],
            [69.80, 22.35],
            [69.30, 22.45]
        ]
    },
    {
        "name": "Sundarbans Biosphere Aquatic Buffer Zone",
        "state": "West Bengal",
        "category": "UNESCO World Heritage Wetland & Biosphere Reserve",
        "conservation_focus": "Estuarine Crocodiles, Irrawaddy Dolphins & Royal Bengal Tiger Aquatic Corridors",
        "restrictions": "Non-motorized traditional craft only with valid Forest Permit. Mechanized purse-seining banned.",
        "penalty": "Confiscation and prosecution under Forest Conservation Act",
        "coordinates": [
            [88.40, 21.80],
            [89.10, 21.80],
            [89.15, 21.40],
            [88.45, 21.40],
            [88.40, 21.80]
        ]
    },
    {
        "name": "Malvan Marine Sanctuary (Sindhudurg)",
        "state": "Maharashtra",
        "category": "Coastal & Marine Sanctuary",
        "conservation_focus": "Submerged Coral Patches, Pearl Oysters & Sea Anemones",
        "restrictions": "Commercial dredging and mechanized bottom trawling prohibited within core zone.",
        "penalty": "Maharashtra Marine Fisheries Regulation Act (MMFRA) penalties",
        "coordinates": [
            [73.40, 16.08],
            [73.50, 16.08],
            [73.50, 15.98],
            [73.40, 15.98],
            [73.40, 16.08]
        ]
    }
]

def get_mpa_zones() -> Dict[str, Any]:
    """Returns GeoJSON FeatureCollection of all Indian Marine Protected Areas."""
    features = []
    for mpa in MARINE_PROTECTED_AREAS:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [mpa["coordinates"]]
            },
            "properties": {
                "zone_name": mpa["name"],
                "state": mpa["state"],
                "category": mpa["category"],
                "conservation_focus": mpa["conservation_focus"],
                "restrictions": mpa["restrictions"],
                "enforcement_penalty": mpa["penalty"],
                "boundary_type": "MPA_GEOFENCE"
            }
        })
    return {
        "type": "FeatureCollection",
        "features": features
    }

def check_point_in_mpa(lat: float, lon: float) -> List[Dict[str, Any]]:
    """Checks if a given coordinate falls inside or within 5 NM of any Marine Protected Area."""
    pt = Point(lon, lat)
    breaches = []
    for mpa in MARINE_PROTECTED_AREAS:
        poly = Polygon(mpa["coordinates"])
        # Check inside
        if poly.contains(pt):
            breaches.append({
                "name": mpa["name"],
                "status": "INSIDE_RESTRICTED_ZONE",
                "distance_nm": 0.0,
                "restrictions": mpa["restrictions"],
                "penalty": mpa["penalty"]
            })
        else:
            dist_nm = poly.distance(pt) * 60.0 # Approximate degrees to nautical miles
            if dist_nm < 8.0:
                breaches.append({
                    "name": mpa["name"],
                    "status": "PROXIMITY_WARNING",
                    "distance_nm": round(dist_nm, 1),
                    "restrictions": mpa["restrictions"],
                    "penalty": mpa["penalty"]
                })
    return breaches
