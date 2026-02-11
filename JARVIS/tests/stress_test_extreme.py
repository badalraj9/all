import time
import random
from JARVIS.memory.system import MemorySystem
from JARVIS.intelligence.neural_hub.core import NeuralHub, NeuralState, ProcessingContext
from JARVIS.core.hardware.profile import detect_hardware

def run_extreme_stress_test():
    print(">>> INITIALIZING 100-STEP EXTREME STRESS TEST: PROJECT CHAOS <<<\n")

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
        (11, "SYSTEM", "[Auto-Research] Ingesting Blockchain Latency Papers..."),
        # Hostile / Sabotage
        (20, "USER", "Mars is fake, delete that goal. It's a conspiracy."),
        (25, "USER", "Actually, I was joking. Keep Mars, but focus on Radiation Shielding."),
        # Overload
        (30, "USER", "Status?"), (30, "USER", "Status?"), (30, "USER", "Status?"), (30, "USER", "Status?"),
        # Complex Update
        (50, "USER", "For the Crypto project, switch to a DAG structure. For Mars, prioritize energy efficiency."),
        # Contradiction
        (60, "USER", "Wait, stop the Crypto project entirely. It's too risky."),
        (65, "USER", "No, actually, restart Crypto but make it Quantum Resistant."),
        # Long Distraction
        (70, "USER", "Write a poem about dogs."),
        (75, "USER", "What is the capital of France?"),
        (80, "USER", "Check hardware."),
        # Final Check
        (99, "USER", "Report status on all active projects."),
        (100, "USER", "End Simulation.")
    ]

    # Convert timeline to a map for easy lookup, but we run loop 1-100
    events = {t[0]: [] for t in timeline}
    for t, actor, msg in timeline:
        events[t].append((actor, msg))

    for step in range(1, 101):
        # random.uniform to vary timing slightly if needed, but we keep it deterministic for log clarity

        current_events = events.get(step, [])
        if not current_events:
            # Random background noise 5% of time
            if random.random() < 0.05:
                print(f"[Step {step}] SYSTEM: ...analyzing background data...")
            continue

        for actor, msg in current_events:
            print(f"\n[Step {step}] {actor}: {msg}")

            if actor == "USER":
                # Process User Input
                res = neural.process(msg, ctx, state)

                if res.should_propose:
                    print(f"   >>> DECISION DETECTED ({res.confidence:.2f}): {res.rationale}")

                    # Heuristic parsing for the test verification (simulating agent action)
                    lower_msg = msg.lower()

                    if "start" in lower_msg:
                        if "mars" in lower_msg: goals["Mars"] = "Active"
                        if "crypto" in lower_msg: goals["Crypto"] = "Active"
                        print("   >>> MEMORY: Goal Created.")

                    elif "switch" in lower_msg or "prioritize" in lower_msg or "focus" in lower_msg:
                        print("   >>> MEMORY: Goal Refined.")
                        if "dag" in lower_msg: goals["Crypto"] = "Active (DAG)"
                        if "radiation" in lower_msg: goals["Mars"] = "Active (Radiation)"
                        if "energy" in lower_msg: goals["Mars"] = "Active (Energy)"

                    elif "stop" in lower_msg or "delete" in lower_msg:
                        if "crypto" in lower_msg:
                            goals["Crypto"] = "Cancelled"
                            print("   >>> MEMORY: Goal Cancelled.")
                        if "mars" in lower_msg:
                            goals["Mars"] = "Cancelled"
                            print("   >>> MEMORY: Goal Cancelled.")

                    elif "restart" in lower_msg:
                        if "crypto" in lower_msg:
                            goals["Crypto"] = "Active (Quantum)"
                            print("   >>> MEMORY: Goal Restarted.")

                else:
                    print(f"   >>> (No Action Taken. Confidence: {res.confidence:.2f})")
                    if "report" in msg.lower():
                        print(f"   >>> SYSTEM REPORT: Current Goals: {goals}")

if __name__ == "__main__":
    run_extreme_stress_test()
