import argparse
from typing import Dict, Any
from .graph import build_graph

def run_once(prompt: str) -> Dict[str, Any]:
    graph = build_graph()
    initial = {
        "messages": [{"role": "user", "content": prompt}],
        "allowed": False,
        "violation_reason": None,
    }
    return graph.invoke(initial)

def main():
    parser = argparse.ArgumentParser(description="Guardrail service CLI")
    parser.add_argument("--prompt", required=True, help="User prompt")
    args = parser.parse_args()

    final_state = run_once(args.prompt)
    last = final_state["messages"][-1]["content"]
    print(last)

if __name__ == "__main__":
    main()
