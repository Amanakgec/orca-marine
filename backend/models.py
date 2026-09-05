from typing import Literal, List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ChatMessageHistory(BaseModel):
    role: Literal['user', 'assistant', 'system']
    content: str

class ChatRequest(BaseModel):
    message: str
    location: str = "Chennai"
    language: str = "en"
    vessel_type: Optional[str] = "motorized_boat"  # country_craft, motorized_boat, mechanized_trawler
    time_horizon: Optional[str] = "current"        # current, tomorrow_morning, 24h
    conversation_history: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

class AgentStep(BaseModel):
    agent_name: str
    action: str
    result_summary: str

class LayerStyle(BaseModel):
    color: str
    opacity: float = 0.6
    width: float = 2.0

class GeoJSONLayer(BaseModel):
    id: str
    type: Literal['fill', 'line', 'circle', 'heatmap']
    label: str
    data: Dict[str, Any]  # GeoJSON FeatureCollection
    style: LayerStyle

class CoastalTelemetry(BaseModel):
    location: str
    sea_state: str
    wave_height_m: float
    wind_speed_kmh: float
    tide_summary: str
    alert_level: str  # NORMAL, CAUTION, WARNING, SEVERE

class ChatResponse(BaseModel):
    text_response: str
    agent_reasoning: List[AgentStep]
    geojson_layers: List[GeoJSONLayer]
    telemetry: Optional[CoastalTelemetry] = None
