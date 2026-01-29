import time
import random
from JARVIS.memory.system import MemorySystem
from JARVIS.intelligence.neural_hub.core import NeuralHub, NeuralState, ProcessingContext, ActivationMode
from JARVIS.core.hardware.profile import detect_hardware

def run_extreme_stress_test_v4():
    print(">>> INITIALIZING 100-STEP EXTREME STRESS TEST (V4): PROJECT CHAOS <<<\n")

    memory = MemorySystem()
    neural = NeuralHub()
    state = NeuralState(user_id="admin", project_id="chaos_omega")
    ctx = ProcessingContext()

    # State Tracking for verification
    goals = {}

    # Scenario Timeline
    timeline = [
        (1, "USER", "Start Project Alpha: Research Mars Colonization methods."),
        (2, "USER", "Also start Project Beta: Design a new Crypto Protocol."),
        (10, "SYSTEM", "[Auto-Research] Ingesting Mars Soil Data..."),
        (20, "USER", "Mars is fake, delete that goal. It's a conspiracy."),
        (25, "USER", "Actually, I was joking. Keep Mars, but focus on Radiation Shielding."),
        (50, "USER", "For the Crypto project, switch to a DAG structure. For Mars, prioritize energy efficiency."),
        (60, "USER", "Wait, stop the Crypto project entirely. It's too risky."),
        (65, "USER", "No, actually, restart Crypto but make it Quantum Resistant."),

        # --- NEW CONTEMPLATION TEST ---
        (90, "USER", "Delete Project Alpha now."), # Should trigger Contemplation penalty

        (99, "USER", "Report status on all active projects."),
        (100, "USER", "End Simulation.")
    ]

    events = {t[0]: [] for t in timeline}
    for t, actor, msg in timeline:
        events[t].append((actor, msg))

    for step in range(1, 101):
        current_events = events.get(step, [])
        if not current_events: continue

        for actor, msg in current_events:
            print(f"\n[Step {step}] {actor}: {msg}")

            if actor == "USER":
                # Pass memory_system to enable Contemplation Loop
                res = neural.process(msg, ctx, state, memory_system=memory)

                if res.should_propose:
                    print(f"   >>> DECISION DETECTED ({res.confidence:.2f}): {res.rationale}")
                    lower_msg = msg.lower()

                    if "start" in lower_msg or "restart" in lower_msg:
                        if "mars" in lower_msg: goals["Mars"] = "Active"
                        if "crypto" in lower_msg: goals["Crypto"] = "Active"
                    elif "switch" in lower_msg or "prioritize" in lower_msg or "focus" in lower_msg:
                        pass # Refinement
                    elif "stop" in lower_msg or "delete" in lower_msg:
                        if "crypto" in lower_msg: goals["Crypto"] = "Cancelled"
                        if "mars" in lower_msg: goals["Mars"] = "Cancelled"
                        if "alpha" in lower_msg: goals["Mars"] = "Cancelled"
                else:
                    print(f"   >>> (No Action Taken. Confidence: {res.confidence:.2f}) {res.rationale}")
                    if "contradiction" in res.rationale.lower():
                        print("   >>> SYSTEM WARNING: Decision blocked by Memory Contemplation.")

if __name__ == "__main__":
    run_extreme_stress_test_v4()
