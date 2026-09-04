from typing import Literal, List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str
    location: str = "Chennai"
    language: str = "en"

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

class ChatResponse(BaseModel):
    text_response: str
    agent_reasoning: List[AgentStep]
    geojson_layers: List[GeoJSONLayer]
