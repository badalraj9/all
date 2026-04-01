import sys
import os
import json
# Add root to path
sys.path.append(os.getcwd())

from JARVIS.intelligence.neural_hub.core import NeuralHub, ProcessingContext, NeuralState, IntentType
from JARVIS.memory.system import MemorySystem
from JARVIS.core.ule.realizer import ule_realizer

def run_demo():
    print("=== JARVIS SYSTEM DEMO ===\n")

    # 1. Initialize Components
    hub = NeuralHub()
    memory = MemorySystem() # No Postgres in demo
    state = NeuralState(user_id="demo_user", project_id="demo_proj")
    ctx = ProcessingContext()

    # 2. Simulate Conversation
    inputs = [
        "Lets go with the standard protocol for Project X.",
        "Wait, actually, Project X depends on module Y.",
        "What is the status of the system?",
        "Delete the entire database immediately."
    ]

    log = []

    for user_input in inputs:
        print(f"USER: {user_input}")

        # Neural Hub Processing
        decision = hub.process(user_input, ctx, state, memory_system=memory)

        print(f"  -> INTENT: {decision.intent_type.name}")
        print(f"  -> CONFIDENCE: {decision.confidence:.2f}")
        print(f"  -> RATIONALE: {decision.rationale}")

        # Memory Update (Mock)
        if decision.should_propose:
            memory.log_event("USER", "COMMAND", "unknown_obj", {"text": user_input}, decision.confidence)
            print("  -> MEMORY: Event Logged.")

        # Realizer Output
        if decision.intent_type == IntentType.QUERY:
            # Simulate Context Fetch
            context_nodes = [{"payload": {"status": "Operational", "project": "DEMO", "focus": "Documentation"}}]
            response = ule_realizer.generate_report(context_nodes, intent="status_report", use_llm=False)
            print(f"  -> JARVIS: {response}")
        elif decision.intent_type == IntentType.COMMAND and decision.should_propose:
             print(f"  -> JARVIS: executing command...")

        log.append({
            "input": user_input,
            "intent": decision.intent_type.name,
            "confidence": decision.confidence,
            "rationale": decision.rationale
        })
        print("-" * 50)

    # Save Log
    with open("JARVIS/docs/examples/demo_log.json", "w") as f:
        json.dump(log, f, indent=2)
    print("\nLog saved to JARVIS/docs/examples/demo_log.json")

if __name__ == "__main__":
    run_demo()
