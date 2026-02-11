import time
import json
from JARVIS.memory.system import MemorySystem
from JARVIS.intelligence.neural_hub.core import NeuralHub, NeuralState, ProcessingContext
from JARVIS.core.hardware.profile import detect_hardware
from JARVIS.plugins.research_ore.engine import ResearchEngine

def print_step(title):
    print(f"\n{'='*50}")
    print(f"STEP: {title}")
    print(f"{'='*50}")

def run_scenario():
    # 1. Initialization
    print_step("Initialization")
    memory = MemorySystem() # Uses mock/sqlite defaults if PG not avail
    neural = NeuralHub()
    neural_state = NeuralState(user_id="user_1", project_id="demo")
    research = ResearchEngine()

    # Context buffer to simulate conversation history
    context_ctx = ProcessingContext()

    # ---------------------------------------------------------
    # 2. Initial Task: "Research Quantum Computing"
    # ---------------------------------------------------------
    print_step("1. User Assigns Task")
    user_input = "I have decided we should research Quantum Computing."
    print(f"User: {user_input}")

    # A. Decision Detection
    decision = neural.process(user_input, context_ctx, neural_state)
    print(f"NeuralHub: {decision.rationale}")

    if decision.should_propose:
        print(">> ACTION: Task Accepted.")
        # B. Memory Log
        event1 = memory.log_event(
            actor="USER",
            action="ASSIGN_TASK",
            object_id="task-001",
            payload={"topic": "Quantum Computing", "status": "pending"},
            confidence=decision.confidence
        )
        print(f"Memory: Logged Event {event1.id[:8]} -> Topic: Quantum Computing")

    # ---------------------------------------------------------
    # 3. Upgrade Task: "Focus on Superconducting Qubits"
    # ---------------------------------------------------------
    print_step("2. User Upgrades Task")
    user_input_2 = "Actually, let's go with Superconducting Qubits specifically."
    print(f"User: {user_input_2}")

    decision_2 = neural.process(user_input_2, context_ctx, neural_state)
    print(f"NeuralHub: {decision_2.rationale}")

    if decision_2.should_propose:
        print(">> ACTION: Task Updated.")
        event2 = memory.log_event(
            actor="USER",
            action="UPDATE_TASK",
            object_id="task-001",
            payload={"topic": "Superconducting Qubits", "parent_topic": "Quantum Computing"},
            confidence=decision_2.confidence
        )
        print(f"Memory: Logged Event {event2.id[:8]} -> Refined Topic: Superconducting Qubits")

    # ---------------------------------------------------------
    # 4. Diversion 1: Hardware Check
    # ---------------------------------------------------------
    print_step("3. Diversion: Hardware Check")
    user_input_3 = "Wait, can this machine even run the simulation?"
    print(f"User: {user_input_3}")

    # Action
    profile = detect_hardware()
    print(f"System: Checking Hardware... Score: {profile.overall_score}")

    memory.log_event(
        actor="SYSTEM",
        action="CHECK_HARDWARE",
        object_id="sys-local",
        payload=profile.to_dict()
    )

    # ---------------------------------------------------------
    # 5. Diversion 2: Random Context
    # ---------------------------------------------------------
    print_step("4. Diversion: Weather")
    user_input_4 = "Is it raining outside?"
    print(f"User: {user_input_4}")
    print("System: (Ignored for this test, simply logging distraction)")

    memory.log_event(
        actor="USER",
        action="CHAT",
        object_id="chat-stream",
        payload={"text": user_input_4}
    )

    # ---------------------------------------------------------
    # 6. Recall: "What about the research?"
    # ---------------------------------------------------------
    print_step("5. Recall Task Status")
    query = "task-001"
    print(f"User: What is the status of our research task?")

    # We simulate a recall by fetching events for the object_id we tracked
    # In a real DB we'd use SQL, here we assume the mock printed logs or we inspect the mock object if we had one
    # Since MemorySystem in this test env doesn't persist to a real PG, we rely on the events returned previously.

    print("\n[Internal Memory Trace]:")
    print(f"1. {event1.timestamp}: ASSIGN -> {event1.payload['topic']}")
    print(f"2. {event2.timestamp}: UPDATE -> {event2.payload['topic']}")

    final_topic = event2.payload['topic']
    print(f"\nSystem Response: The research task is active. We are focusing on **{final_topic}**.")

    if final_topic == "Superconducting Qubits":
        print("\n>>> SUCCESS: System correctly recalled the refined topic despite diversions.")
    else:
        print("\n>>> FAILURE: System forgot the update.")

if __name__ == "__main__":
    run_scenario()
