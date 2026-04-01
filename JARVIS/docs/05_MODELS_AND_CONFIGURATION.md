# Models & Configuration: Multimodal Routing

## 1. Overview
JARVIS supports **Multimodal Input/Output Routing** to ensure fluid interaction across different mediums. The system strictly adheres to the "Voice for Voice, Text for Text" principle:

-   **Voice Input**: User speaks $\rightarrow$ STT $\rightarrow$ System Process $\rightarrow$ **Voice Output (TTS)** + Text Log
-   **Text Input**: User types $\rightarrow$ System Process $\rightarrow$ **Text Output** (Silent)

This ensures the user is not bombarded with audio when working silently in a terminal, but receives fluid conversation when speaking.

---

## 2. Model Configuration

### 2.1. Cognitive Plane (Text Generation)
The system uses **AirLLM** (via `JARVIS/intelligence/llm_engine`) for reasoning and content generation.

**Configuration (`.env`):**
```ini
# Path to the Hugging Face model (local or ID)
LLM_MODEL_PATH=meta-llama/Llama-2-7b-chat-hf

# Execution Device (cuda:0, cpu, mps)
LLM_DEVICE=cuda:0
```
*Note: Large models (70B+) require 24GB+ RAM. Smaller models (7B) run on 8GB+.*

### 2.2. Verbal Plane (Speech Synthesis)
The system uses **Edge-TTS** (Microsoft Edge Online Neural Voices) for high-quality, zero-cost speech synthesis.

**Configuration (`.env`):**
```ini
# Voice Selection (run `edge-tts --list-voices` to see options)
TTS_VOICE=en-GB-RyanNeural
```

---

## 3. Routing Logic
The routing is handled by the **Universal Language Engine (ULE)** in `JARVIS/core/ule/engine.py`.

### 3.1. Workflow
1.  **Ingestion**:
    -   **Text Mode**: Terminal TUI sends raw text with `input_mode="TEXT"`.
    -   **Voice Mode**: Microphone capture (via `vosk` or similar) converts audio to text, then sends it with `input_mode="VOICE"`.

2.  **Processing**:
    -   The `process_turn` function calculates the response content using the Cognitive Plane (LLM).
    -   **IF input_mode == "VOICE"**:
        -   The system lowers the `Explicitness` variable ($E_t$) to generate shorter, more conversational responses.
        -   The system triggers `tts_engine.speak(response)`.
    -   **IF input_mode == "TEXT"**:
        -   The system maintains standard `Explicitness`.
        -   TTS is **skipped**.

3.  **Output**:
    -   In both cases, the text response is returned to the UI for display.
    -   Audio is played asynchronously only for Voice turns.

---

## 4. Hardware Requirements
-   **Voice Mode**: Requires a working audio output device (`pygame` compatible) and internet connection (for Edge-TTS).
-   **Text Mode**: Fully offline capable (if LLM is local).
