import json
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from models import ChatRequest, ChatResponse, AgentStep, GeoJSONLayer, LayerStyle
from agents.tools import discover_ocean_data, assess_safety_risk, find_potential_fishing_zones, compute_safe_route
from agents.prompts import SYSTEM_PROMPT
from agents.mock_orchestrator import mock_orchestrate

# Tool name -> friendly agent name mapping
TOOL_AGENT_MAP = {
    "discover_ocean_data": "Data Agent",
    "assess_safety_risk": "Safety Agent",
    "find_potential_fishing_zones": "PFZ Agent",
    "compute_safe_route": "Routing Agent",
}

# Combine all tools
tools = [discover_ocean_data, assess_safety_risk, find_potential_fishing_zones, compute_safe_route]

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
    """Build and compile the LangGraph StateGraph. Deferred to avoid import-time LLM init failures."""
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

# Lazy-init to avoid crash on import when no API key is set
_graph = None

def _get_graph():
    global _graph
    if _graph is None:
        _graph = _build_graph()
    return _graph


async def run_agent(request: ChatRequest) -> ChatResponse:
    """Run the LLM-powered LangGraph agent. Falls back to mock on failure."""
    try:
        graph = _get_graph()

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=request.message),
        ]

        final_state = await graph.ainvoke({"messages": messages})

        # Extract text response from final AI message
        final_message = final_state["messages"][-1]
        text_response = final_message.content or "I've processed your request. Please see the map for results."

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
                        # Build a more informative summary
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
            agent_name="Synthesis",
            action="generate_response",
            result_summary="Combined tool outputs into final answer",
        ))

        # Deduplicate layers
        unique_raw = list({l["id"]: l for l in layers_raw}.values())

        return ChatResponse(
            text_response=text_response,
            agent_reasoning=steps,
            geojson_layers=_to_geojson_layers(unique_raw),
        )
    except Exception as e:
        print(f"LLM Orchestrator failed: {e}. Falling back to mock orchestrator.")
        return await mock_orchestrate(request)
