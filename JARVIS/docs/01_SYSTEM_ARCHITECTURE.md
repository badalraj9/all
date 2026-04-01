# System Architecture: The Universal Language Engine (ULE)

## 1. Overview
The JARVIS system implements a novel **Universal Language Engine (ULE)** architecture, designed to separate **Control** (Deterministic, Safe) from **Cognition** (Probabilistic, Creative). This separation addresses the fundamental instability of Large Language Models (LLMs) in mission-critical environments.

The architecture is composed of four primary planes:
1.  **The Neural Hub (Control Plane)**: A deterministic decision engine.
2.  **The Memory Galaxy (Context Plane)**: A graph-based truth maintenance system.
3.  **The Cognitive Plane**: LLM-based generation and reasoning (AirLLM).
4.  **The Realizer Plane**: A hybrid output system maximizing safety and speed.

---

## 2. The Neural Hub (Control Plane)
**Location:** `JARVIS/intelligence/neural_hub/core.py`

The Neural Hub serves as the "Prefrontal Cortex" of the system. Unlike standard agents that feed user input directly to an LLM, JARVIS first passes input through a **Deterministic Signal Processor**.

### 2.1. Signal Extraction
The system uses `LinguisticSensor` and `StructuralSensor` to extract `Signals` from raw text.
-   **Linguistic Signals**: Regex-based patterns detecting intent (e.g., "start", "stop", "create", "why").
-   **Structural Signals**: Metadata analysis (e.g., thread depth, user authority).

Each signal has a `baseWeight` and a dynamic `value`.

### 2.2. Synaptic Processing
Signals are aggregated using a **Variable Activation Mode**:
-   **Standard (Sigmoid)**: Balanced decision making.
-   **Strict (Steep Sigmoid)**: High confidence required (used for destructive commands).
-   **Exploratory (Softplus)**: Encourages proposal generation (used for brainstorming).

### 2.3. The Contemplation Loop
Before finalizing a decision, the Neural Hub queries the **Memory System** to validate assumptions.
-   **Contradiction Check**: If the user asks to "Delete Project Alpha", the Hub checks if "Project Alpha" has incoming dependencies (`depends_on` edges) in the graph. If dependencies exist, the confidence score is penalized, effectively vetoing the destructive action without LLM intervention.

---

## 3. The Realizer Plane
**Location:** `JARVIS/core/ule/realizer.py`

The **ULERealizer** implements the **Hybrid Output Principle**. It dynamically switches between generation methods based on intent and resource availability.

### 3.1. Template Mode (Deterministic)
-   **Trigger**: High-confidence routine queries (e.g., "Status Report", "Thesis Abstract") or LLM failure.
-   **Mechanism**: fills pre-defined safe templates with structured data from the Memory Graph.
-   **Benefit**: Zero hallucination, <10ms latency.

### 3.2. Cognitive Mode (LLM)
-   **Trigger**: Complex queries (`CHAT`, `QUERY`) requiring synthesis.
-   **Mechanism**: Passes the "Context Web" (flattened graph nodes) to the `LLMEngine`.
-   **Implementation**: Uses `AirLLM` for layer-wise inference, allowing large models (Llama-2 70B) to run on consumer hardware (24GB RAM) by swapping layers to CPU RAM.

---

## 4. Hardware Adaptation (MAREY Assimilation)
**Location:** `JARVIS/core/hardware/profile.py`

The system is self-aware of its host hardware.
-   **Detection**: Uses `psutil` to score CPU, RAM, and Storage.
-   **Adaptation**: The `AdaptiveVisionPipeline` scales image resolution and processing depth based on the `HardwareProfile.overall_score`. Low-spec machines get faster, lower-res scans; high-spec machines get full foveal analysis.
