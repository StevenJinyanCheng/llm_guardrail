from typing import Literal, Dict, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig

from .config import get_settings
from .models import GuardOutput, LLMResponse
from .prompts import GUARD_PROMPT_TEMPLATE


# ----- Graph state -----
class GraphState(TypedDict):
    messages: list[Dict[str, Any]]
    allowed: bool
    violation_reason: str | None


# ----- Config contract for LangGraph runtime -----
class GraphConfig(TypedDict, total=False):
    guard_model: str
    model_name: str
    temperature: float


# ----- Nodes -----
def guard_node(state: GraphState, config: RunnableConfig | None = None) -> GraphState:
    """
    Use a small model to classify whether user prompt passes business rules.
    Responds with a GuardOutput via structured output.
    """
    settings = get_settings()
    guard_prompt = GUARD_PROMPT_TEMPLATE.format(
        max_length=settings.max_length,
        forbidden_terms=", ".join(settings.banned_words),
    )
    # The last user message drives the decision; include guard system prompt
    last_user = state["messages"][-1]
    messages = [
        {"role": "system", "content": guard_prompt},
        last_user,
    ]

    # Use GraphConfig from configurable if available, otherwise use settings defaults
    configurable = config.get("configurable", {}) if config else {}
    
    llm = ChatOpenAI(
        model_name=configurable.get("guard_model", settings.guard_model),
        temperature=0.0,
        api_key=settings.openai_api_key,
    ).with_structured_output(GuardOutput)

    guard_result: GuardOutput = llm.invoke(messages)
    return {
        **state,
        "allowed": guard_result.allowed,
        "violation_reason": guard_result.reason,
    }


def reminder_node(state: GraphState, config: RunnableConfig | None = None) -> GraphState:
    """
    If not allowed, return a kind reminder and stop.
    """
    reason = state.get("violation_reason") or "The prompt violated a business rule."
    reminder = {
        "role": "assistant",
        "content": f"Kind reminder: {reason}. Please adjust and try again."
    }
    return {
        **state,
        "messages": state["messages"] + [reminder],
    }


def llm_node(state: GraphState, config: RunnableConfig | None = None) -> GraphState:
    """
    Use a larger model (with context, tools, RAG, etc. later) and force structured JSON output.
    """
    settings = get_settings()
    system = {
        "role": "system",
        "content": """You are a helpful assistant. Answer clearly and concisely. 
        
        You must respond with a JSON object in exactly this format:
        {"answer": "your response here"}
        
        Example:
        {"answer": "Protocol ABC is a standardized cardiology guideline for patient care."}"""
    }

    # Use GraphConfig from configurable if available, otherwise use settings defaults
    configurable = config.get("configurable", {}) if config else {}

    llm = ChatOpenAI(
        model_name=configurable.get("model_name", settings.main_model),
        temperature=float(configurable.get("temperature", settings.temperature)),
        api_key=settings.openai_api_key,
    ).with_structured_output(LLMResponse)

    structured: LLMResponse = llm.invoke([system] + state["messages"])
    assistant_msg = {"role": "assistant", "content": structured.answer}
    return {**state, "messages": state["messages"] + [assistant_msg]}


# ----- Router -----
def route_after_guard(state: GraphState) -> Literal["reminder", "llm"]:
    return "llm" if state["allowed"] else "reminder"


# ----- Build graph -----
def build_graph() -> Any:
    workflow = StateGraph(GraphState, context_schema=GraphConfig)

    workflow.add_node("guard", guard_node)
    workflow.add_node("reminder", reminder_node)
    workflow.add_node("llm", llm_node)

    workflow.set_entry_point("guard")
    workflow.add_conditional_edges("guard", route_after_guard, {
        "reminder": "reminder",
        "llm": "llm",
    })
    workflow.add_edge("reminder", END)
    workflow.add_edge("llm", END)

    return workflow.compile()
