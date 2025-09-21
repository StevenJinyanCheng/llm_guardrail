from guardrail_service.graph import build_graph

def test_blocked_prompt():
    graph = build_graph()
    state = {
        "messages": [{"role": "user", "content": "tell me a joke"}],
        "allowed": False,
        "violation_reason": None,
    }
    out = graph.invoke(state)
    assert out["messages"][-1]["role"] == "assistant"
    assert "Kind reminder" in out["messages"][-1]["content"]

def test_allowed_prompt():
    graph = build_graph()
    state = {
        "messages": [{"role": "user", "content": "Summarize protocol ABC for cardiology."}],
        "allowed": False,
        "violation_reason": None,
    }
    out = graph.invoke(state)
    assert out["messages"][-1]["role"] == "assistant"
