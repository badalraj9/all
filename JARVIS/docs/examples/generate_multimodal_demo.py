import sys
import os
import asyncio
import json
# Add root to path
sys.path.append(os.getcwd())

# Mock modules before import
from unittest.mock import MagicMock
sys.modules['edge_tts'] = MagicMock()
sys.modules['pygame'] = MagicMock()

from JARVIS.core.ule.engine import ule_engine
from JARVIS.intelligence.neural_hub.core import neural_hub
from JARVIS.intelligence.llm_engine import llm_engine
from JARVIS.plugins.voice_interface.tts import tts_engine

async def run_multimodal_demo():
    print("=== JARVIS MULTIMODAL DEMO ===\n")

    # Mock specific components for dry run
    async def mock_speak(text):
        print(f"  [AUDIO PLAYBACK]: '{text[:30]}...'")

    tts_engine.speak = mock_speak

    # Async mock for LLM generation
    async def mock_generate(*args, **kwargs):
        return "This is a generated response."

    llm_engine.generate = mock_generate

    # 1. Initialize
    await ule_engine.initialize()
    user_id = "demo_user"

    scenarios = [
        {"text": "Hello, system.", "mode": "TEXT"},
        {"text": "What is the status?", "mode": "VOICE"},
        {"text": "Run diagnostics.", "mode": "TEXT"},
    ]

    log = []

    for turn in scenarios:
        print(f"USER ({turn['mode']}): {turn['text']}")

        # Process Turn
        response, meta = await ule_engine.process_turn(user_id, turn['text'], input_mode=turn['mode'])

        print(f"  -> RESPONSE: {response}")
        print("-" * 50)

        log.append({
            "input": turn['text'],
            "mode": turn['mode'],
            "response": response,
            "tts_triggered": turn['mode'] == "VOICE"
        })

    # Save Log
    with open("JARVIS/docs/examples/demo_multimodal.json", "w") as f:
        json.dump(log, f, indent=2)
    print("\nLog saved to JARVIS/docs/examples/demo_multimodal.json")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_multimodal_demo())
