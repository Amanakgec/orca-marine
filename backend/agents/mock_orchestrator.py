import random
from models import ChatRequest, ChatResponse, AgentStep, GeoJSONLayer, LayerStyle, CoastalTelemetry
from agents.tools import (
    discover_ocean_data,
    assess_safety_risk,
    find_potential_fishing_zones,
    compute_safe_route,
    get_tide_and_weather_forecast,
    get_severe_weather_alerts,
    analyze_fishery_decline,
    audit_restricted_zones
)

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

COASTAL_LOCATIONS = {
    # Gujarat & Gulf of Kutch / Khambhat
    'porbandar': (21.64, 69.60),
    'veraval': (20.90, 70.36),
    'kandla': (23.00, 70.21),
    'kutch': (22.75, 69.80),
    'surat': (21.17, 72.83),
    'diu': (20.71, 70.98),
    'daman': (20.39, 72.83),

    # Maharashtra & Konkan Coast
    'mumbai': (18.92, 72.82),
    'bombay': (18.92, 72.82),
    'ratnagiri': (16.99, 73.28),
    'alibaug': (18.64, 72.87),
    'malvan': (16.06, 73.46),

    # Goa
    'goa': (15.29, 73.91),
    'panaji': (15.49, 73.82),
    'mormugao': (15.40, 73.80),

    # Karnataka
    'karwar': (14.80, 74.12),
    'mangalore': (12.91, 74.85),
    'mangaluru': (12.91, 74.85),
    'udupi': (13.34, 74.74),
    'malpe': (13.35, 74.70),

    # Kerala & Malabar Coast
    'kochi': (9.93, 76.26),
    'cochin': (9.93, 76.26),
    'kozhikode': (11.25, 75.78),
    'calicut': (11.25, 75.78),
    'kollam': (8.89, 76.61),
    'alappuzha': (9.49, 76.33),
    'alleppey': (9.49, 76.33),
    'thiruvananthapuram': (8.52, 76.93),
    'trivandrum': (8.52, 76.93),

    # Tamil Nadu & Coromandel Coast / Gulf of Mannar
    'kanyakumari': (8.08, 77.55),
    'cape comorin': (8.08, 77.55),
    'tuticorin': (8.76, 78.13),
    'thoothukudi': (8.76, 78.13),
    'rameswaram': (9.29, 79.31),
    'mannar': (9.15, 78.90),
    'nagapattinam': (10.77, 79.84),
    'cuddalore': (11.75, 79.77),
    'chennai': (13.08, 80.27),
    'madras': (13.08, 80.27),
    'puducherry': (11.94, 79.80),
    'pondicherry': (11.94, 79.80),

    # Andhra Pradesh
    'machilipatnam': (16.18, 81.13),
    'kakinada': (16.98, 82.24),
    'vizag': (17.68, 83.21),
    'visakhapatnam': (17.68, 83.21),
    'nellore': (14.44, 79.98),

    # Odisha
    'puri': (19.81, 85.83),
    'paradip': (20.31, 86.61),
    'gahirmatha': (20.72, 87.05),
    'chandipur': (21.47, 87.01),
    'gopalpur': (19.26, 84.90),

    # West Bengal & Sundarbans
    'kolkata': (22.57, 88.36),
    'calcutta': (22.57, 88.36),
    'digha': (21.62, 87.50),
    'haldia': (22.06, 88.06),
    'sundarbans': (21.80, 88.80),

    # Islands
    'port blair': (11.62, 92.72),
    'andaman': (11.62, 92.72),
    'kavaratti': (10.56, 72.64),
    'lakshadweep': (10.56, 72.64)
}

def _extract_location_from_history(history: list, current_msg: str) -> tuple:
    """Extract location from current message or fallback to conversational history for multi-turn context."""
    msg = current_msg.lower()
    for key, coords in COASTAL_LOCATIONS.items():
        if key in msg:
            return coords[0], coords[1], key.title()

    # Search backwards in history
    if history:
        for turn in reversed(history):
            content = turn.get("content", "").lower()
            for key, coords in COASTAL_LOCATIONS.items():
                if key in content:
                    return coords[0], coords[1], key.title()

    # Default if nowhere found
    return None, None, None

async def mock_orchestrate(request: ChatRequest) -> ChatResponse:
    msg = request.message.lower()

    # Step 1: Context Resolution (Current turn + multi-turn history)
    lat, lon, detected_loc = _extract_location_from_history(request.conversation_history or [], request.message)

    # Check explicit location override if given
    if request.location and request.location.lower() not in ('auto', 'default', ''):
        for key, coords in COASTAL_LOCATIONS.items():
            if key in request.location.lower():
                lat, lon = coords
                detected_loc = key.title()
                break

    vessel_type = request.vessel_type or "motorized_boat"
    basin = "Arabian Sea" if (lon is not None and lon < 77.5) else "Bay of Bengal"

    layers_raw: list[dict] = []
    steps: list[AgentStep] = []
    text_response = ""
    alert_level = "NORMAL"

    greeting = f"Maritime Swarm Intelligence reporting for **{detected_loc}** ({basin}):"

    # =========================================================================
    # CRITICAL GROUNDING PROTOCOL CHECKS (ISRO SIH26176)
    # =========================================================================

    # 1. Identity Inquiry: "Who are you?", "What are you?"
    is_identity_query = any(phrase in msg for phrase in [
        'who are you', 'what are you', 'who r u', 'what r u', 'who you are', 'what you are',
        'tell me who you are', 'what is your name', 'identify yourself'
    ])

    # 2. Capabilities Inquiry: "What can you do?", "How can you help?"
    is_capabilities_query = (
        any(phrase in msg for phrase in [
            'what can you do', 'how can you help', 'what do you do', 'what can this do', 'what does this do',
            'how do you help', 'how can i use you', 'what are your capabilities', 'what help can you provide'
        ]) and not any(k in msg for k in ['motto', 'mission', 'for the people', 'help the people', 'fishermen'])
    )

    # 3. Motto & Core Mission Inquiry: "What is the motto?", "What can you do for the people using this project?"
    is_motto_query = any(phrase in msg for phrase in [
        'motto', 'mission', 'for the people', 'help the people', 'what is orca', 'about orca',
        'about this project', 'purpose of this project', 'purpose of orca', 'why orca'
    ])

    # Check if the user is giving a friendly greeting without an operational question:
    greeting_tokens = ['hi', 'hello', 'hey', 'vanakkam', 'namaste', 'namaskar', 'pranam', 'kem cho', 'good morning', 'good afternoon', 'good evening']
    is_pure_greeting = (
        msg.strip() in greeting_tokens or 
        any(msg.strip().startswith(g + " ") or msg.strip().startswith(g + "!") or msg.strip().startswith(g + ",") for g in greeting_tokens)
    ) and not any(k in msg for k in ['fish', 'weather', 'cyclone', 'tide', 'route', 'safe', 'decline', 'mpa', 'zone', 'port', 'near', 'sea', 'water', 'wave', 'wind', 'alert', 'lightning', 'who', 'what', 'how'])

    # =========================================================================
    # Rule 0: Explicit Out-of-Scope (Temporal Trigger Override)
    # =========================================================================
    import re
    OUT_OF_SCOPE_KEYWORDS = [
        'eat', 'eating', 'food', 'diet', 'burger', 'pizza', 'sandwich', 'wear', 'wearing', 'clothes', 'clothing', 
        'shirt', 'pants', 'shoes', 'antigravity', 'physics', 'math', 'movie', 'song', 'music', 'dance', 
        'cricket', 'football', 'sports', 'politics', 'religion', 'joke', 'recipe', 'cook', 'cooking'
    ]
    is_explicitly_out_of_scope = any(re.search(r'\b' + kw + r'\b', msg) for kw in OUT_OF_SCOPE_KEYWORDS)

    # =========================================================================
    # Rule 1: Identity Response
    # =========================================================================
    if is_explicitly_out_of_scope:
        steps.append(AgentStep(
            agent_name="Planning & Router Agent",
            action="enforce_domain_boundary",
            result_summary="Identified out-of-scope subject. Rejected query under strict domain boundaries."
        ))
        text_response = "I am ORCA, an ISRO marine intelligence assistant. That topic is beyond my scope. I can only assist with coastal weather, sea states, tides, and marine routes."

    elif is_identity_query:
        steps.append(AgentStep(
            agent_name="Planning & Router Agent",
            action="identity_grounding",
            result_summary="Handled identity verification inquiry under ISRO SIH26176 Grounding Protocol"
        ))
        text_response = "I am the AI Assistant for ORCA Marine Intelligence, an intelligent platform developed for the ISRO SIH26176 project."

    # =========================================================================
    # Rule 1: Capabilities Response
    # =========================================================================
    elif is_capabilities_query:
        steps.append(AgentStep(
            agent_name="Planning & Router Agent",
            action="capabilities_grounding",
            result_summary="Reported platform navigation, telemetry, and marine ecosystem capabilities under Grounding Protocol"
        ))
        text_response = "I can help you navigate the ORCA platform, understand ocean swarm telemetry, and answer questions about marine ecosystems, our collaborative agents, and this website's features."

    # =========================================================================
    # Project Motto & Multi-Stakeholder Value Proposition
    # =========================================================================
    elif is_motto_query:
        # Load illustrative MPA, boundary, and Potential Fishing Zone layers for a rich visual overview
        res_mpa = audit_restricted_zones.invoke({"lat": 13.08, "lon": 80.27})
        res_pfz = find_potential_fishing_zones.invoke({"lat_min": 11.0, "lon_min": 79.0, "lat_max": 14.5, "lon_max": 81.5})
        layers_raw.extend(res_mpa.get("geojson_layers", []))
        layers_raw.extend(res_pfz.get("geojson_layers", []))

        steps.append(AgentStep(
            agent_name="Planning & Router Agent",
            action="evaluate_system_mission_and_scope",
            result_summary="Identified inquiry on ORCA mission, motto, and multi-stakeholder value architecture under ISRO SIH26176"
        ))
        steps.append(AgentStep(
            agent_name="Synthesis Agent",
            action="synthesize_stakeholder_impact_matrix",
            result_summary="Formulated explainable operational capabilities for artisanal fishers, trawler fleets, coastal disaster authorities, and marine scientists"
        ))

        text_response = (
            "🐋 **ORCA — Marine Ecosystem Reasoning with Collaborative Agents**\n"
            "*(ISRO Problem Statement SIH26176 · Indian Space Research Organisation)*\n\n"
            "🌟 **PROJECT MOTTO**:\n"
            "**\"Bridging Space Science and Coastal Livelihoods — Empowering India's Blue Economy with Collaborative Marine Intelligence.\"**\n\n"
            "🎯 **OUR CORE MISSION**:\n"
            "To bridge the gap between cutting-edge space technology and ground-level marine operations. We transform petabytes of complex Earth Observation satellite data (Oceansat-3, INSAT-3D, GIS) and oceanographic forecasts into **plain-language, life-saving, and economically empowering conversational decisions** for every marine stakeholder along India's 7,516 km coastline.\n\n"
            "👥 **WHAT ORCA DOES FOR THE PEOPLE USING THIS PLATFORM**:\n\n"
            "1. 🎣 **For Artisanal & Traditional Fishermen**:\n"
            "• **Pinpoint High-Yield Potential Fishing Zones (PFZs)**: Correlates 26°–28°C Sea Surface Temperature thermal breaks with optical chlorophyll plumes to reveal where fish congregate. Cuts offshore search time and **slashes vessel diesel expenses by 20%–30%**.\n"
            "• **Vessel-Calibrated Safety Windows**: Delivers hourly operational clearances tailored to small motorized fiber boats and traditional *Vallams*, factoring in localized chop, wind gusts, and sandbar-clearing tide cycles.\n\n"
            "2. 🛡️ **For Coastal Communities & Life Safety**:\n"
            "• **Early Cyclone & Severe Weather Directives**: Ingests IMD satellite cyclone trajectories, eye coordinates, gale wind radiuses, and lightning squall clusters to warn fishers well before severe weather strikes.\n\n"
            "3. ⚖️ **For Fishermen's Legal & Ecological Protection**:\n"
            "• **Real-Time Geofence Guardian**: Enforces active boundary alerts for **Marine Protected Areas (MPAs)** (Gulf of Mannar, Gahirmatha Olive Ridley turtle sanctuaries) and UNCLOS **International Maritime Boundary Lines (IMBL)** with 5 Nautical Mile safety buffers to prevent accidental border crossings and legal detentions.\n\n"
            "4. 🔬 **For Marine Scientists, Coastal Authorities & Port Managers**:\n"
            "• **Ecological Productivity Diagnostics**: Explains sudden fish catch decline by analyzing satellite SST marine heatwaves, Ekman transport upwelling deficits, and seasonal hypoxia.\n"
            "• **Safe Navigational Corridors**: Automatically generates waypoint routes dog-legging around rough sea states (>2.5m swells) and maritime hazard zones.\n\n"
            "5. 🗣️ **For Every Coastal Citizen (Total Inclusivity)**:\n"
            "• **Multilingual Voice & Chat in 11 Indian Languages** (Tamil, Telugu, Malayalam, Gujarati, Marathi, Bengali, Odia, Hindi, Kannada, etc.) with realistic regional neural speech, ensuring zero literacy barrier for grassroots fishers.\n\n"
            "💡 *You can ask me any question about your local waters, or click any of the 8 ISRO Problem Scenarios on the left to see live collaborative agent reasoning in action!*"
        )

    # =========================================================================
    # High-Priority: Pure Friendly Greeting
    # Example: "hi", "hello", "namaste", "vanakkam"
    # =========================================================================
    elif is_pure_greeting:
        loc_display = f"{detected_loc} sector" if detected_loc else "Indian Coastal Waters"
        steps.append(AgentStep(
            agent_name="Planning & Router Agent",
            action="initialize_session",
            result_summary=f"Welcome hand-shake established for {loc_display}. Initialized collaborative marine intelligence swarm."
        ))

        greeting_text = (
            f"👋 **Vanakkam & Greetings from ORCA!** 🐋\n"
            f"*(ISRO SIH26176 — Marine Ecosystem Reasoning with Collaborative Agents)*\n\n"
            f"🌟 **Project Motto**: *\"Bridging Space Science and Coastal Livelihoods — Empowering India's Blue Economy with Collaborative Marine Intelligence.\"*\n\n"
            f"I am your collaborative autonomous marine intelligence swarm. I synthesize Earth Observation satellite data (Oceansat-3, INSAT-3D) with ocean forecasts, tide harmonics, and maritime boundaries into explainable decisions for fishermen, vessel operators, and coastal authorities.\n\n"
            f"🧭 **What would you like to explore today?**\n"
            f"• 🎣 **'Where is the nearest Potential Fishing Zone today?'**\n"
            f"• 🌅 **'Is it safe to venture into the sea tomorrow morning?'**\n"
            f"• 🌊 **'What are the tide, weather, and sea conditions near my fishing location?'**\n"
            f"• ⚡ **'Are there any lightning or cyclone alerts in my area?'**\n"
            f"• 🗺️ **'What is the safest route for my vessel?'**\n"
            f"• 📉 **'Why has fish productivity declined in this coastal region?'**\n"
            f"• 🚫 **'Which zones should be avoided due to MPAs or geofencing?'**\n\n"
        )

        if detected_loc:
            res_data = discover_ocean_data.invoke({"lat": lat, "lon": lon, "radius_km": 60})
            layers_raw.extend(res_data.get("geojson_layers", []))
            text_response = greeting_text + f"📍 *Currently monitoring **{detected_loc}** ({basin}). You can speak or type in any of 11 Indian languages, or click a 1-click scenario chip on the left!*"
        else:
            text_response = greeting_text + f"📍 *To get started, please specify the coastal state or city you are interested in (e.g., Gujarat, Kerala, or Chennai).*"\
    
    # =========================================================================
    # Rule X: STRICT Location Clarification for Operational Data
    # =========================================================================
    elif lat is None or lon is None or detected_loc is None:
        steps.append(AgentStep(
            agent_name="Planning & Router Agent",
            action="request_location_context",
            result_summary="Location missing for operational query. Prompting user for coastal state or city."
        ))
        
        if "near me" in msg or "current location" in msg or "my location" in msg or "where i am" in msg:
            text_response = "I cannot automatically detect your location right now. Which coastal state or city are you currently in?"
        else:
            text_response = "To provide an accurate live ocean intelligence brief, please specify the state or coastal city you are interested in (e.g., Gujarat, Kerala, or Chennai)."

    # =========================================================================
    # Scenario 4: Lightning, Severe Weather & Cyclone Alerts
    # Example: "Are there any lightning or cyclone alerts in my area?"
    # =========================================================================
    elif any(w in msg for w in ['lightning', 'cyclone', 'storm', 'squall', 'thunderstorm', 'depression', 'gale']):
        res = get_severe_weather_alerts.invoke({"lat": lat, "lon": lon})
        layers_raw.extend(res.get("geojson_layers", []))
        alert_level = "SEVERE"

        steps.append(AgentStep(
            agent_name="Severe Weather Agent",
            action="imd_cyclone_track_ingest",
            result_summary=f"Tracked {res['cyclone_bulletin']['system']} located at {res['cyclone_bulletin']['current_location']}"
        ))
        steps.append(AgentStep(
            agent_name="Disaster Management Agent",
            action="convective_squall_audit",
            result_summary=f"Detected high lightning density (12-18 flashes/km²/hr). Issued {res['cyclone_bulletin']['alert_status']}"
        ))

        text_response = (
            f"⚡ **SEVERE WEATHER & CYCLONE ADVISORY — {detected_loc.upper()}**\n\n"
            f"🌀 **Tropical System**: **{res['cyclone_bulletin']['system']}**\n"
            f"• **Current Position**: {res['cyclone_bulletin']['current_location']} (~{res['cyclone_bulletin']['distance_from_port_km']} km offshore)\n"
            f"• **Alert Status**: **{res['cyclone_bulletin']['alert_status']}**\n"
            f"• **Gale Wind Warning**: Squall gusts up to 65-85 km/h over target waters.\n\n"
            f"⚡ **Lightning & Thunderstorm Hazard**:\n"
            f"• Intense convective cloud cells active within 30 NM of the coast.\n"
            f"• High lightning discharge hazard detected in red polygon.\n\n"
            f"🚨 **Emergency Action Directive**:\n"
            f"{res['cyclone_bulletin']['advisory']}\n"
            f"Small motorized boats and traditional craft must remain in harbor. Trawlers must return immediately."
        )

    # =========================================================================
    # Scenario 2: Tomorrow Morning Operational Safety
    # Example: "Is it safe to venture into the sea tomorrow morning?"
    # =========================================================================
    elif any(w in msg for w in ['tomorrow', 'morning', 'venture', 'safe to go', 'tomorrow morning']):
        res = get_tide_and_weather_forecast.invoke({"lat": lat, "lon": lon, "time_horizon": "tomorrow_morning"})
        layers_raw.extend(res.get("geojson_layers", []))

        morning = res["morning_outlook"]
        alert_level = "CAUTION" if morning["wave_height_m"] > 1.8 else "NORMAL"

        steps.append(AgentStep(
            agent_name="Weather Intelligence Agent",
            action="temporal_wave_wind_forecast",
            result_summary=f"Forecasted wave height {morning['wave_height_m']}m and wind {morning['wind_speed_kmh']} km/h ({morning['wind_direction']}) for morning window"
        ))
        steps.append(AgentStep(
            agent_name="Risk Assessment Agent",
            action="vessel_suitability_audit",
            result_summary=f"Evaluated suitability: {morning['sea_state']}. High tide at {morning['morning_high_tide']['time']} ({morning['morning_high_tide']['height_m']}m)"
        ))

        text_response = (
            f"🌅 **OPERATIONAL SAFETY FORECAST — {detected_loc.upper()} (TOMORROW MORNING)**\n\n"
            f"• **Operating Window**: **05:00 AM – 11:00 AM**\n"
            f"• **Sea State**: **{morning['sea_state']}**\n"
            f"• **Wave Height**: **{morning['wave_height_m']} meters** (Swell: {morning['wind_direction']})\n"
            f"• **Wind Speed**: **{morning['wind_speed_kmh']} km/h**\n"
            f"• **Morning Tide**: **{morning['morning_high_tide']['type']}** at **{morning['morning_high_tide']['time']}** (Depth: +{morning['morning_high_tide']['height_m']}m)\n\n"
            f"📋 **Vessel-Specific Safety Clearances**:\n"
            f"• **Small Motorized Craft**: {morning['vessel_safety_advisory']['motorized_fiber_boat']}\n"
            f"• **Traditional Vallam / Country Craft**: {morning['vessel_safety_advisory']['traditional_vallam_country_craft']}\n"
            f"• **Mechanized Trawlers**: {morning['vessel_safety_advisory']['mechanized_trawler']}\n\n"
            f"⚠️ *Note: Sea state shifts to {morning['afternoon_outlook']['sea_state']} in the afternoon. Return to harbor before noon.*"
        )

    # =========================================================================
    # Scenario 3: Tide, Weather & Sea Conditions
    # Example: "What are the tide, weather, and sea conditions near my fishing location?"
    # =========================================================================
    elif any(w in msg for w in ['tide', 'tides', 'sea condition', 'wave condition', 'water condition']):
        res = get_tide_and_weather_forecast.invoke({"lat": lat, "lon": lon})
        layers_raw.extend(res.get("geojson_layers", []))

        steps.append(AgentStep(
            agent_name="Hydrographic Agent",
            action="compute_tidal_harmonics",
            result_summary=f"Computed diurnal tide cycles for {detected_loc}: {res['tidal_phase']}"
        ))
        steps.append(AgentStep(
            agent_name="Weather Intelligence Agent",
            action="sea_state_telemetry",
            result_summary=f"Ingested wave & wind sensors: {res['morning_outlook']['sea_state']}"
        ))

        schedule_str = "\n".join([f"• **{item['time']}**: {item['type']} ({item['height_m']}m)" for item in res["tide_schedule"]])
        text_response = (
            f"🌊 **TIDE, WEATHER & SEA STATE REPORT — {detected_loc.upper()}**\n\n"
            f"📊 **Sea State Assessment**: **{res['morning_outlook']['sea_state']}**\n"
            f"• **Wave Height**: **{res['morning_outlook']['wave_height_m']} meters**\n"
            f"• **Wind Speed**: **{res['morning_outlook']['wind_speed_kmh']} km/h** ({res['morning_outlook']['wind_direction']})\n"
            f"• **Tidal Phase**: **{res['tidal_phase']}**\n\n"
            f"🕒 **24-Hour Tidal Schedule**:\n{schedule_str}\n\n"
            f"💡 *Optimal Harbor Departure*: Plan departures 45 minutes before High Tide to clear sandbar shallows."
        )

    # =========================================================================
    # Scenario 7: Why Has Fish Productivity Declined?
    # Example: "Why has fish productivity declined in a particular coastal region?"
    # =========================================================================
    elif any(w in msg for w in ['decline', 'declined', 'productivity', 'low catch', 'less fish', 'why no fish', 'catch dropped']):
        res = analyze_fishery_decline.invoke({"lat": lat, "lon": lon, "location_name": detected_loc})
        layers_raw.extend(res.get("geojson_layers", []))

        steps.append(AgentStep(
            agent_name="Ocean Analytics Agent",
            action="satellite_sst_anomaly_correlation",
            result_summary=f"Detected +{res['sst_anomaly_celsius']}°C SST anomaly (Marine Heatwave) off {detected_loc}"
        ))
        steps.append(AgentStep(
            agent_name="Marine Ecology Agent",
            action="diagnose_upwelling_and_hypoxia",
            result_summary=f"Ekman upwelling reduced by {res['upwelling_index_deficit_percent']}%; Dissolved oxygen: {res['dissolved_oxygen_mg_l']} mg/L"
        ))

        causes_str = "\n".join([f"• 🔬 {c}" for c in res["primary_causes"]])
        recs_str = "\n".join([f"• 🧭 {r}" for r in res["scientific_recommendations"]])

        text_response = (
            f"📉 **ECOLOGICAL DIAGNOSTIC: FISHERY PRODUCTIVITY DECLINE — {detected_loc.upper()}**\n\n"
            f"Satellite Earth Observation (Oceansat-3 & INSAT-3D) correlates 4 key drivers for the catch decline:\n\n"
            f"**Oceanographic Root Causes**:\n{causes_str}\n\n"
            f"📊 **Biochemical Indicators**:\n"
            f"• **SST Thermal Anomaly**: **+{res['sst_anomaly_celsius']}°C** above 10-year mean\n"
            f"• **Coastal Upwelling Deficit**: **{res['upwelling_index_deficit_percent']}%**\n"
            f"• **Chlorophyll-a Plume Deficit**: **{res['chlorophyll_deficit_percent']}%**\n"
            f"• **Dissolved Oxygen on Shelf**: **{res['dissolved_oxygen_mg_l']} mg/L**\n\n"
            f"💡 **Recommended Adaptive Strategies**:\n{recs_str}"
        )

    # =========================================================================
    # Scenario 8: Avoid Hazardous & Restricted Zones (MPA & Geofencing)
    # Example: "Which fishing zones should be avoided due to hazardous marine conditions or geofencing restrictions?"
    # =========================================================================
    elif any(w in msg for w in ['avoid', 'restricted', 'protected', 'mpa', 'sanctuary', 'turtle', 'reserve', 'forbidden', 'no fishing']):
        res = audit_restricted_zones.invoke({"lat": lat, "lon": lon})
        layers_raw.extend(res.get("geojson_layers", []))
        alert_level = "WARNING"

        steps.append(AgentStep(
            agent_name="Geofencing Agent",
            action="crosscheck_mpa_and_imbl_registers",
            result_summary="Cross-checked location against Indian Wildlife Sanctuaries and UNCLOS IMBL"
        ))
        steps.append(AgentStep(
            agent_name="Compliance Agent",
            action="generate_exclusion_zones",
            result_summary="Isolated 5 Marine Protected Areas and international boundary buffers"
        ))

        text_response = (
            f"🚫 **RESTRICTED & HAZARDOUS MARINE ZONES TO AVOID — {detected_loc.upper()}**\n\n"
            f"Fishermen are strictly advised to avoid the following designated sectors:\n\n"
            f"1. **Marine Protected Areas (MPAs — Amber Polygons)**:\n"
            f"• **Gulf of Mannar Marine National Park**: Strict no-trawling zone. Coral reef and Dugong sanctuary.\n"
            f"• **Gahirmatha Marine Sanctuary (Odisha)**: 20 km offshore fishing ban during Olive Ridley turtle mass nesting.\n"
            f"• **Marine National Park (Gulf of Kutch)**: Commercial fishing prohibited over live coral beds.\n"
            f"• **Sundarbans Aquatic Buffer**: Estuarine crocodile and dolphin reserve.\n\n"
            f"2. **International Maritime Boundaries (IMBL — Purple Lines)**:\n"
            f"• Maintain a **strict 5 Nautical Mile safety buffer** from Sri Lanka, Pakistan, and Bangladesh borders.\n\n"
            f"3. **Weather Hazard Sectors (Red Polygons)**:\n"
            f"• Offshore swell zones exceeding 2.5m wave height.\n\n"
            f"⚖️ *Legal Notice: Fishing within declared MPAs violates Schedule I of the Wildlife Protection Act.*"
        )

    # =========================================================================
    # Scenario 5: High Chlorophyll & Favourable SST
    # Example: "Which regions show high chlorophyll concentration and favourable sea surface temperature?"
    # =========================================================================
    elif any(w in msg for w in ['chlorophyll', 'favourable', 'favorable', 'temperature and chlorophyll', 'thermal front', 'bloom']):
        res = discover_ocean_data.invoke({"lat": lat, "lon": lon, "radius_km": 80})
        layers_raw.extend(res.get("geojson_layers", []))

        steps.append(AgentStep(
            agent_name="Satellite Earth Observation Agent",
            action="oceansat3_chlorophyll_extraction",
            result_summary=f"Extracted optical chlorophyll-a plumes (2.5 - 6.8 mg/m³) for {detected_loc}"
        ))
        steps.append(AgentStep(
            agent_name="Ocean Analytics Agent",
            action="thermal_gradient_matching",
            result_summary=f"Matched favorable 26.5°C - 28.0°C SST isotherms with high-density phytoplankton fronts"
        ))

        text_response = (
            f"🌿 **HIGH CHLOROPHYLL & OPTIMAL SST FRONTS — {detected_loc.upper()}**\n\n"
            f"Satellite Earth Observation (Oceansat-3 & MODIS-Aqua) has identified productive ocean color features:\n\n"
            f"• **Optimal Thermal Isotherms**: **26.8°C – 28.2°C** (Ideal pelagic feeding temperature)\n"
            f"• **Chlorophyll-a Concentration**: **3.4 – 7.1 mg/m³** (High primary productivity)\n"
            f"• **Thermal Gradient Boundary**: Strong temperature break (0.8°C/km) detected 18 NM offshore.\n"
            f"• **Target Species Attracted**: Indian Mackerel, Sardine, Skipjack Tuna, and Squid.\n\n"
            f"📍 *Visualization*: Orange circular markers indicate optimal SST sampling stations; green overlays mark chlorophyll plumes."
        )

    # =========================================================================
    # Scenario 6: Safest Navigational Route
    # Example: "What is the safest route for a fishing vessel considering weather and sea-state conditions?"
    # =========================================================================
    elif any(w in msg for w in ['route', 'navigate', 'path', 'journey', 'travel', 'waypoint', 'sail', 'course']):
        dest_lat, dest_lon = lat - 1.8, lon - 0.4
        dest_name = "Deep-Sea Fishing Ground"
        for key, coords in COASTAL_LOCATIONS.items():
            if key in msg and key != detected_loc.lower():
                dest_lat, dest_lon = coords
                dest_name = key.title()
                break

        res = compute_safe_route.invoke({
            "start_lat": lat, "start_lon": lon, "end_lat": dest_lat, "end_lon": dest_lon, "vessel_type": vessel_type
        })
        layers_raw.extend(res.get("geojson_layers", []))

        steps.append(AgentStep(
            agent_name="Geospatial Reasoning Agent",
            action="hazard_corridor_audit",
            result_summary=f"Audited passage between {detected_loc} and {dest_name} against MPAs, rough seas, and IMBL"
        ))
        steps.append(AgentStep(
            agent_name="Navigational Route Optimization Agent",
            action="generate_safe_waypoints",
            result_summary=f"Created safe passage ({res['distance_nm']} NM, {res['estimated_time_hours']} hrs ETA @ 10 kts)"
        ))

        text_response = (
            f"🗺️ **OPTIMIZED SAFE NAVIGATION ROUTE**\n\n"
            f"• **Departure Port**: **{detected_loc}** ({lat:.2f}°N, {lon:.2f}°E)\n"
            f"• **Destination Sector**: **{dest_name}** ({dest_lat:.2f}°N, {dest_lon:.2f}°E)\n"
            f"• **Vessel Type**: **{vessel_type.replace('_', ' ').title()}**\n"
            f"• **Total Transit Distance**: **{res['distance_nm']} Nautical Miles**\n"
            f"• **Estimated Time of Arrival (ETA)**: **{res['estimated_time_hours']} hours** at cruising speed (10 kts)\n\n"
            f"🛡️ **Corridor Clearances**:\n"
            f"• Successfully skirted {', '.join(res['hazards_avoided'])}\n"
            f"• Maintains a safe buffer from Marine Protected Areas and international boundaries.\n\n"
            f"🧭 *The cyan track line on your chart represents the safest recommended navigation lane.*"
        )

    # =========================================================================
    # Scenario 1: Nearest Potential Fishing Zone (PFZ) Today
    # Example: "Where is the nearest Potential Fishing Zone today?"
    # =========================================================================
    elif any(w in msg for w in ['fish', 'pfz', 'catch', 'tuna', 'sardine', 'mackerel', 'zone', 'fishing', 'nearest']):
        lat_min, lon_min, lat_max, lon_max = lat - 1.2, lon - 1.2, lat + 1.2, lon + 1.2
        res = find_potential_fishing_zones.invoke({
            "lat_min": lat_min, "lon_min": lon_min, "lat_max": lat_max, "lon_max": lon_max
        })
        layers_raw.extend(res.get("geojson_layers", []))

        steps.append(AgentStep(
            agent_name="Data Discovery Agent",
            action="satellite_chlorophyll_sst_ingest",
            result_summary=f"Ingested Oceansat-3 SST & Chlorophyll-a layers for {detected_loc} shelf"
        ))
        steps.append(AgentStep(
            agent_name="PFZ Reasoning Agent",
            action="thermal_front_correlation",
            result_summary=f"Correlated 26.5-28.0°C thermal fronts. Verified {len(res['recommended_zones'])} compliant PFZ zones"
        ))

        top_zone = res["recommended_zones"][0] if res["recommended_zones"] else None
        if top_zone:
            text_response = (
                f"🎣 **NEAREST POTENTIAL FISHING ZONE (PFZ) TODAY — {detected_loc.upper()}**\n\n"
                f"• **Primary Hotspot**: **{top_zone.get('location')}**\n"
                f"• **Confidence Score**: **{top_zone.get('confidence', 0.85)*100:.0f}%** (High Yield Probability)\n"
                f"• **Target Pelagic Species**: **{top_zone.get('species')}**\n"
                f"• **Thermal & Optical Signature**: SST {top_zone.get('sst_range')} | Chlorophyll {top_zone.get('chlorophyll')}\n"
                f"• **Bathymetric Depth**: {top_zone.get('depth')}\n\n"
                f"💡 **Operational Advice**:\n"
                f"• Verified clear of Marine Protected Areas (MPAs).\n"
                f"• Recommended fishing time: Early morning hours (05:30 - 09:30 AM).\n"
                f"• Green polygons on your map mark the productive harvest perimeter."
            )
        else:
            text_response = f"Identified productive fishing grounds within your coordinates. Check the green polygons on your chart."

    # =========================================================================
    # Fallback: In-Domain Marine Queries vs. Out-of-Scope Fallback
    # =========================================================================
    else:
        # Check if the query is strictly within the marine/ocean domain or mentions coastal waters/locations
        MARINE_DOMAIN_TERMS = [
            'orca', 'isro', 'sih', 'ocean', 'sea', 'water', 'marine', 'coastal', 'coast', 'shelf', 'basin',
            'sst', 'temperature', 'chlorophyll', 'plume', 'thermal', 'upwelling', 'current', 'salinity',
            'bathymetry', 'depth', 'heatwave', 'hypoxia', 'algae', 'bloom', 'coral', 'reef', 'mangrove',
            'fish', 'fishing', 'pfz', 'catch', 'species', 'tuna', 'sardine', 'mackerel', 'pelagic',
            'trawler', 'vallam', 'boat', 'vessel', 'craft', 'ship', 'weather', 'wind', 'wave', 'swell',
            'chop', 'tide', 'cyclone', 'storm', 'squall', 'lightning', 'monsoon', 'douglas', 'sea state',
            'safety', 'safe', 'hazard', 'route', 'corridor', 'navic', 'ais', 'imbl', 'boundary', 'mpa',
            'sanctuary', 'geofence', 'geofencing', 'port', 'harbor', 'island', 'archipelago',
            'arabian sea', 'bay of bengal', 'andaman sea', 'indian ocean', 'andaman', 'nicobar', 'lakshadweep'
        ]
        is_in_domain = any(t in msg for t in MARINE_DOMAIN_TERMS) or any(loc in msg for loc in COASTAL_LOCATIONS.keys())

        if is_in_domain:
            res_data = discover_ocean_data.invoke({"lat": lat, "lon": lon, "radius_km": 70})
            res_safe = assess_safety_risk.invoke({"lat": lat, "lon": lon, "vessel_type": vessel_type})

            layers_raw.extend(res_data.get("geojson_layers", []))
            layers_raw.extend(res_safe.get("geojson_layers", []))

            steps.append(AgentStep(
                agent_name="Data Discovery Agent",
                action="gather_coastal_telemetry",
                result_summary=f"Retrieved SST ({res_data['sst_summary']['avg']}°C), Chlorophyll, and Weather for {detected_loc}"
            ))
            steps.append(AgentStep(
                agent_name="Synthesis Agent",
                action="generate_personalized_brief",
                result_summary=f"Compiled multi-source marine brief. Safety index: {res_safe['risk_level'].upper()}"
            ))

            text_response = (
                f"🌊 **LIVE OCEAN INTELLIGENCE BRIEF — {detected_loc.upper()}**\n\n"
                f"• **Sea Surface Temperature**: Average **{res_data['sst_summary']['avg']}°C** (Range: {res_data['sst_summary']['min']}°C - {res_data['sst_summary']['max']}°C)\n"
                f"• **Productivity**: {res_data['chlorophyll_summary']}\n"
                f"• **Safety Assessment**: **{res_safe['risk_level'].upper()}** ({res_safe['sea_state']})\n"
                f"• **Maritime Boundary Proximity**: {res_safe['imbl_distance_nm']} NM from {res_safe['nearest_boundary']}\n\n"
                f"💬 *Try asking about:*\n"
                f"• 'Where is the nearest Potential Fishing Zone today?'\n"
                f"• 'Is it safe to venture into the sea tomorrow morning?'\n"
                f"• 'What are the tide, weather, and sea conditions near my fishing location?'\n"
                f"• 'Are there any lightning or cyclone alerts in my area?'\n"
                f"• 'Why has fish productivity declined in this coastal region?'"
            )
        else:
            # Enforce Grounding Protocol Rule 2 & 3:
            # Strictly reject out-of-scope, irrelevant, nonsensical queries, general knowledge, etc.
            # Do NOT hallucinate, generate random map coordinates, or return arbitrary locations.
            steps.append(AgentStep(
                agent_name="Planning & Router Agent",
                action="enforce_grounding_protocol",
                result_summary="Query out of domain scope. Refused out-of-domain inquiry under ISRO SIH26176 grounding protocol."
            ))
            text_response = "I am ORCA, an ISRO marine intelligence assistant. That topic is beyond my scope. I can only assist with coastal weather, sea states, tides, and marine routes."
            layers_raw = []

    # Deduplicate layers by ID to avoid overlapping layers
    unique_raw = list({l["id"]: l for l in layers_raw}.values())

    # Build live coastal telemetry
    is_out_of_scope = "That topic is beyond my scope" in text_response

    if is_out_of_scope:
        telemetry_loc = "ORCA Platform (Standby)"
        telemetry_tide = "Monitoring Coastal Waters"
    elif is_identity_query or is_capabilities_query:
        telemetry_loc = "Indian Coastal Waters"
        telemetry_tide = "All Coastal Stations Active"
    elif is_motto_query:
        telemetry_loc = "Indian Coastal Shelf"
        telemetry_tide = "All Coastal Stations Active"
    elif lat is None or lon is None or detected_loc is None:
        telemetry_loc = "ORCA Platform (Standby)"
        telemetry_tide = "Awaiting Location Input"
    else:
        telemetry_loc = detected_loc
        telemetry_tide = "High Tide at 06:15 AM (2.8m)"

    telemetry = CoastalTelemetry(
        location=telemetry_loc,
        sea_state="State 3 (Slight/Moderate)" if alert_level == "NORMAL" else ("State 4 (Rough)" if alert_level == "CAUTION" else "State 5 (Very Rough)"),
        wave_height_m=1.4 if alert_level == "NORMAL" else (2.4 if alert_level == "CAUTION" else 3.8),
        wind_speed_kmh=18.5 if alert_level == "NORMAL" else (32.0 if alert_level == "CAUTION" else 55.0),
        tide_summary=telemetry_tide,
        alert_level=alert_level
    )

    return ChatResponse(
        text_response=text_response,
        agent_reasoning=steps,
        geojson_layers=_to_geojson_layers(unique_raw),
        telemetry=telemetry
    )
