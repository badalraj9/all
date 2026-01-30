from JARVIS.intelligence.neural_hub.core import NeuralHub, NeuralState, ProcessingContext
from JARVIS.core.ule.realizer import ule_realizer
from JARVIS.memory.system import MemorySystem

def run_final_wiring_test():
    print(">>> FINAL WIRING TEST: INTENT -> TONE -> OUTPUT <<<\n")

    neural = NeuralHub()
    memory = MemorySystem()
    state = NeuralState(user_id="admin", project_id="wiring_test")
    ctx = ProcessingContext()

    scenarios = [
        ("Open the pod bay doors.", "COMMAND"),
        ("How far is Mars?", "QUERY"),
        ("I feel tired today.", "CHAT")
    ]

    for user_input, expected_intent in scenarios:
        print(f"\n[USER] {user_input}")

        # 1. NeuralHub Classification
        res = neural.process(user_input, ctx, state, memory)
        print(f"[NEURAL HUB] Intent: {res.intent_type.name} (Expected: {expected_intent})")

        # 2. ULE Realization (Hybrid)
        # Mocking context nodes
        context_nodes = [{"payload": {"user_input": user_input}}]

        output = ule_realizer.generate_report(
            context_nodes,
            intent=f"Respond to '{user_input}'",
            intent_type=res.intent_type.name,
            use_llm=True
        )

        print(f"[JARVIS] {output}")

if __name__ == "__main__":
    run_final_wiring_test()
