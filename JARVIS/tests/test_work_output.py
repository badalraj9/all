import time
from JARVIS.memory.system import MemorySystem
from JARVIS.intelligence.neural_hub.core import NeuralHub, NeuralState, ProcessingContext, ActivationMode

def run_work_output_test():
    print(">>> INITIALIZING WORK OUTPUT TEST: PROJECT 'CODEGEN' <<<\n")

    memory = MemorySystem()
    neural = NeuralHub()
    state = NeuralState(user_id="dev_1", project_id="codegen_v1")
    ctx = ProcessingContext()

    # ---------------------------------------------------------
    # PHASE 1: EXPLORATORY (Brainstorming)
    # ---------------------------------------------------------
    print("\n--- PHASE 1: EXPLORATORY MODE (Brainstorming) ---")
    state.activation_mode = ActivationMode.EXPLORATORY

    # Input with weak signals ("maybe", "option")
    inputs = [
        "Maybe we could use Python for the backend?",
        "Or perhaps Node.js is an option.",
        "We could try a microservices architecture."
    ]

    for msg in inputs:
        print(f"USER: {msg}")
        res = neural.process(msg, ctx, state)
        print(f"   >>> {res.rationale}")
        if res.should_propose:
            memory.log_event("USER", "BRAINSTORM", "idea-001", {"content": msg})

    # ---------------------------------------------------------
    # PHASE 2: STRICT (Decision Making)
    # ---------------------------------------------------------
    print("\n--- PHASE 2: STRICT MODE (Commitment) ---")
    state.activation_mode = ActivationMode.STRICT

    # Input with medium signals (should fail in Strict)
    print("USER: I think Python is okay.")
    res = neural.process("I think Python is okay.", ctx, state)
    print(f"   >>> {res.rationale} (Expected: Fail)")

    # Input with Strong signals (should pass)
    print("USER: We have decided to use Python.")
    res = neural.process("We have decided to use Python.", ctx, state)
    print(f"   >>> {res.rationale} (Expected: Pass)")

    if res.should_propose:
        memory.log_event("USER", "DECIDE_ARCH", "arch-001", {"language": "Python"})

    # ---------------------------------------------------------
    # PHASE 3: STANDARD (Execution & Output)
    # ---------------------------------------------------------
    print("\n--- PHASE 3: STANDARD MODE (Execution) ---")
    state.activation_mode = ActivationMode.STANDARD

    print("USER: Generate the `main.py` file now.")
    res = neural.process("Generate the main.py file now.", ctx, state)
    print(f"   >>> {res.rationale}")

    if res.should_propose:
        # Simulate Work Output
        print("\n>>> SYSTEM ACTION: GENERATING ARTIFACT <<<")
        code_artifact = """
def main():
    print("Hello from JARVIS Generated Code")
    # Architecture: Python (decided in Phase 2)

if __name__ == "__main__":
    main()
"""
        print(f"FILE: main.py\n{code_artifact}")
        memory.log_event("SYSTEM", "CREATE_FILE", "file-main.py", {"code": code_artifact})
        print(">>> ARTIFACT STORED IN MEMORY <<<")

if __name__ == "__main__":
    run_work_output_test()
