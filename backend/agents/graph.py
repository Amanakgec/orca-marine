import json
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from models import ChatRequest, ChatResponse, AgentStep, GeoJSONLayer, LayerStyle
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
from agents.prompts import SYSTEM_PROMPT
from agents.mock_orchestrator import mock_orchestrate

# Tool name -> friendly agent name mapping
TOOL_AGENT_MAP = {
    "discover_ocean_data": "Data Discovery Agent",
    "assess_safety_risk": "Safety & Risk Agent",
    "find_potential_fishing_zones": "PFZ Reasoning Agent",
    "compute_safe_route": "Route Optimization Agent",
    "get_tide_and_weather_forecast": "Weather & Tide Agent",
    "get_severe_weather_alerts": "Severe Weather Agent",
    "analyze_fishery_decline": "Ecological Analytics Agent",
    "audit_restricted_zones": "Geofencing & Compliance Agent"
}

# Combine all 8 specialized domain tools
tools = [
    discover_ocean_data,
    assess_safety_risk,
    find_potential_fishing_zones,
    compute_safe_route,
    get_tide_and_weather_forecast,
    get_severe_weather_alerts,
    analyze_fishery_decline,
    audit_restricted_zones
]

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

def _build_graph():
    """Build and compile the LangGraph StateGraph."""
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    llm_with_tools = llm.bind_tools(tools)

    def agent_node(state: MessagesState):
        messages = state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    workflow = StateGraph(MessagesState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(tools))

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")

    return workflow.compile()

_graph = None

def _get_graph():
    global _graph
    if _graph is None:
        _graph = _build_graph()
    return _graph

async def run_agent(request: ChatRequest) -> ChatResponse:
    """Run the LLM-powered LangGraph multi-agent swarm with multi-turn history. Falls back to mock on failure."""
    try:
        graph = _get_graph()

        messages = [SystemMessage(content=SYSTEM_PROMPT)]

        # Inject multi-turn conversation history
        if request.conversation_history:
            for turn in request.conversation_history[-6:]:  # Keep last 6 turns for context
                role = turn.get("role")
                content = turn.get("content", "")
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))

        # Add current human message with vessel context
        current_msg = request.message
        if request.vessel_type and request.vessel_type != "motorized_boat":
            current_msg += f" (Operating vessel type: {request.vessel_type})"
        messages.append(HumanMessage(content=current_msg))

        final_state = await graph.ainvoke({"messages": messages})

        # Extract text response from final AI message
        final_message = final_state["messages"][-1]
        text_response = final_message.content or "I have synthesized marine intelligence for your query. See map overlays."

        # Extract agent reasoning steps and GeoJSON layers from tool messages
        steps: list[AgentStep] = []
        layers_raw: list[dict] = []

        for msg in final_state["messages"]:
            if isinstance(msg, ToolMessage):
                agent_name = TOOL_AGENT_MAP.get(msg.name, msg.name)
                summary = "Tool executed successfully"
                try:
                    res = json.loads(msg.content) if isinstance(msg.content, str) else msg.content
                    if isinstance(res, dict):
                        if "geojson_layers" in res:
                            layers_raw.extend(res["geojson_layers"])
                        summary_parts = []
                        for k, v in res.items():
                            if k != "geojson_layers":
                                summary_parts.append(f"{k}: {str(v)[:80]}")
                        if summary_parts:
                            summary = "; ".join(summary_parts[:3])
                except Exception:
                    pass

                steps.append(AgentStep(
                    agent_name=agent_name,
                    action=msg.name,
                    result_summary=summary,
                ))

        # Add synthesis step
        steps.append(AgentStep(
            agent_name="Synthesis Agent",
            action="multisource_reasoning_synthesis",
            result_summary="Correlated Earth observation, meteorology, and boundary layers into final recommendation",
        ))

        # Deduplicate layers by ID
        unique_raw = list({l["id"]: l for l in layers_raw}.values())

        return ChatResponse(
            text_response=text_response,
            agent_reasoning=steps,
            geojson_layers=_to_geojson_layers(unique_raw),
        )

    except Exception as e:
        print(f"[LangGraph Agent Error, falling back to Mock Orchestrator]: {e}")
        return await mock_orchestrate(request)
