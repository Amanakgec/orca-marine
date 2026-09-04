from models import ChatRequest, ChatResponse, AgentStep, GeoJSONLayer, LayerStyle
from agents.tools import discover_ocean_data, assess_safety_risk, find_potential_fishing_zones, compute_safe_route

def _to_geojson_layers(raw_layers: list) -> list[GeoJSONLayer]:
    """Convert raw dict layers from tools into validated GeoJSONLayer Pydantic objects."""
    result = []
    for l in raw_layers:
        style = l.get("style", {})
        result.append(GeoJSONLayer(
            id=l["id"],
            type=l["type"],
            label=l["label"],
            data=l["data"],
            style=LayerStyle(
                color=style.get("color", "#00d4ff"),
                opacity=style.get("opacity", 0.6),
                width=style.get("width", 2.0),
            )
        ))
    return result

async def mock_orchestrate(request: ChatRequest) -> ChatResponse:
    msg = request.message.lower()

    # EXPANDED LOCATION PARSING (All Coastal Regions)
    loc_map = {
        'mumbai': (18.92, 72.82),
        'goa': (15.29, 73.91),
        'mangalore': (12.91, 74.85),
        'kochi': (9.93, 76.26),
        'kanyakumari': (8.08, 77.55),
        'tuticorin': (8.76, 78.13),
        'rameswaram': (9.29, 79.31),
        'nagapattinam': (10.77, 79.84),
        'chennai': (13.08, 80.27),
        'vizag': (17.68, 83.21),
        'puri': (19.81, 85.83),
        'kolkata': (22.57, 88.36)
    }

    lat, lon = loc_map['mumbai'] # Default to Mumbai
    detected_loc = "your location"

    # Check explicit location field first
    if request.location and request.location.lower() not in ('auto', ''):
        req_loc = request.location.lower()
        for key, coords in loc_map.items():
            if key in req_loc:
                lat, lon = coords
                detected_loc = key.capitalize()
                break

    # Then check the message text
    for key, coords in loc_map.items():
        if key in msg:
            lat, lon = coords
            detected_loc = key.capitalize()
            break

    layers_raw: list[dict] = []
    steps: list[AgentStep] = []
    text_response = ""

    # PERSONALIZED GREETINGS
    import random
    greetings = [
        f"Ahoy Captain! Checking the waters around {detected_loc}.",
        f"Greetings! I've analyzed the latest maritime data for {detected_loc}.",
        f"Hello there. Here is your personalized marine report for {detected_loc}.",
    ]
    greet = random.choice(greetings)

    # INTENT DETECTION
    if any(w in msg for w in ['weather', 'wave', 'wind', 'storm', 'cyclone']):
        res1 = discover_ocean_data.invoke({"lat": lat, "lon": lon, "radius_km": 100})
        res2 = assess_safety_risk.invoke({"lat": lat, "lon": lon})

        layers_raw.extend(res1.get("geojson_layers", []))
        layers_raw.extend(res2.get("geojson_layers", []))

        steps.append(AgentStep(agent_name="Data Agent", action="discover_ocean_data", result_summary=f"Retrieved SST ({res1['sst_summary']['min']}–{res1['sst_summary']['max']}°C), chlorophyll, and weather data"))
        steps.append(AgentStep(agent_name="Safety Agent", action="assess_safety_risk", result_summary=f"Risk level: {res2['risk_level']} — IMBL distance: {res2['imbl_distance_nm']} NM"))

        text_response = (
            f"{greet} The sea surface temperature ranges from "
            f"{res1['sst_summary']['min']}°C to {res1['sst_summary']['max']}°C. "
            f"{res2['warnings'][0]}. Risk level is assessed as **{res2['risk_level'].upper()}**."
        )

    elif any(w in msg for w in ['safe', 'risk', 'danger', 'warning', 'boundary', 'imbl']):
        res = assess_safety_risk.invoke({"lat": lat, "lon": lon})
        layers_raw.extend(res.get("geojson_layers", []))

        steps.append(AgentStep(agent_name="Safety Agent", action="assess_safety_risk", result_summary=f"Risk score: {res['risk_score']}/100 — {len(res['warnings'])} warnings"))

        text_response = (
            f"{greet} The current safety risk is classified as **{res['risk_level'].upper()}** (score: {res['risk_score']}/100). "
            f"You are approximately {res['imbl_distance_nm']} nautical miles from the International Maritime Boundary. "
            f"Active warnings: {', '.join(res['warnings'])}."
        )

    elif any(w in msg for w in ['fish', 'pfz', 'catch', 'fishing zone']):
        res = find_potential_fishing_zones.invoke({"lat_min": lat - 1.5, "lon_min": lon - 1.5, "lat_max": lat + 1.5, "lon_max": lon + 1.5})
        layers_raw.extend(res.get("geojson_layers", []))

        steps.append(AgentStep(agent_name="Data Agent", action="fetch_sst_chlorophyll", result_summary="Cross-correlated SST and Chlorophyll-a data"))
        steps.append(AgentStep(agent_name="PFZ Agent", action="find_potential_fishing_zones", result_summary=f"Identified {res.get('total_zones', 0)} fishing zones"))

        text_response = (
            f"{greet} I've identified **{res.get('total_zones', 0)} potential fishing zones** nearby. "
            f"The best zone shows a {(res['zones'][0]['confidence'] * 100):.0f}% probability of high yield based on optimal SST and Chlorophyll levels. "
            f"Check the green polygons on the map for coordinates."
        )

    elif any(w in msg for w in ['route', 'navigate', 'path', 'journey', 'travel']):
        end_lat, end_lon = 8.08, 77.55  # Default destination: Kanyakumari
        for key, coords in loc_map.items():
            if key in msg and coords != (lat, lon):
                end_lat, end_lon = coords
                break

        res = compute_safe_route.invoke({"start_lat": lat, "start_lon": lon, "end_lat": end_lat, "end_lon": end_lon})
        layers_raw.extend(res.get("geojson_layers", []))

        steps.append(AgentStep(agent_name="Safety Agent", action="check_hazards", result_summary=f"Scanned route corridor for hazards — {len(res['hazards_avoided'])} avoided"))
        steps.append(AgentStep(agent_name="Routing Agent", action="compute_safe_route", result_summary=f"Route: {res['distance_nm']} NM, ETA: {res['estimated_time_hours']}h"))

        text_response = (
            f"{greet} I have charted a safe course for you. Total distance is **{res['distance_nm']} nautical miles** "
            f"with an ETA of **{res['estimated_time_hours']} hours**. "
            f"Hazards avoided: {', '.join(res['hazards_avoided'])}. "
            f"The blue line on the map indicates the recommended path."
        )

    else:
        res = discover_ocean_data.invoke({"lat": lat, "lon": lon, "radius_km": 100})
        layers_raw.extend(res.get("geojson_layers", []))

        steps.append(AgentStep(agent_name="Data Agent", action="discover_ocean_data", result_summary="Retrieved general ocean overview"))
        steps.append(AgentStep(agent_name="Synthesis", action="summarize", result_summary="Compiled SST, chlorophyll, and weather data"))

        text_response = (
            f"{greet} Sea surface temperature is currently {res['sst_summary']['avg']}°C on average. "
            f"{res['chlorophyll_summary']} {res['weather_summary']} "
            f"Let me know if you need specific fishing zones, hazard maps, or safe routing!"
        )

    # Deduplicate layers by ID, convert to validated Pydantic models
    unique_raw = list({l["id"]: l for l in layers_raw}.values())

    return ChatResponse(
        text_response=text_response,
        agent_reasoning=steps,
        geojson_layers=_to_geojson_layers(unique_raw),
    )
