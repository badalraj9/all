# JARVIS Assimilated Architecture (Project WARHORSE)

> "The system is not just a chatbot. It is a deterministic cognitive engine."

This document outlines the advanced architecture of JARVIS, assimilated from the specialized components of **MemoryThread**, **SENTRY**, **MAREY**, **ORE**, and **CAPSULE**.

---

## 1. The Brain: NeuralHub (Assimilated from SENTRY)

The **NeuralHub** (`JARVIS/intelligence/neural_hub`) is the central decision-making engine. Unlike LLMs which are probabilistic (and hallucinate), NeuralHub is **deterministic**. It uses AI-inspired mathematics to calculate "Activation Energy" for decisions.

### 1.1 Sensor Array
The brain receives signals from multiple sensors:
*   **Linguistic Sensor:** Scans for 100+ intent patterns (Commands, Agreements, Refusals, Pivots).
*   **Structural Sensor:** Analyzes thread depth and user authority (e.g., Maintainer status).
*   **Contextual Sensor:** (Planned) Analyzes chat types (Direct vs Group).

### 1.2 Variable Activation Modes (Cognitive Gearbox)
The brain operates in different modes depending on the task:
*   **STANDARD (`sigmoid`):** Balanced execution. Used for general tasks.
*   **STRICT (`steep_sigmoid`):** High threshold (0.85). Ignores weak signals ("okay"). Used for critical actions (Delete, Deploy).
*   **EXPLORATORY (`softplus`):** Low threshold (0.20). Amplifies weak signals. Used for brainstorming and creative tasks.

---

## 2. The Memory: Context Web (Assimilated from MemoryThread)

JARVIS does not just "log" chats. It builds a **Context Web** (`JARVIS/memory`)—a semantic graph of goals, facts, and constraints.

### 2.1 Truth Vectors
Every piece of information has a 4-dimensional score:
*   **Confidence:** How sure are we?
*   **Authority:** Who said it? (System > Admin > User).
*   **Freshness:** Does it decay over time?
*   **Corroboration:** Do other sources agree?

### 2.2 The Graph (Context Web)
Entities are linked by **Relations**:
*   **Major Relations:** `DEPENDS_ON`, `CONTRADICTS`, `CONTAINS`. (Hard Constraints).
*   **Partial Relations:** `RELATES_TO`, `PREFERS`. (Soft Influences).

*Example:* "Mars Project" --(depends_on)--> "Radiation Shielding".

---

## 3. The Loop: Contemplation & Reasoning

JARVIS implements a **Cognitive Loop** to ensure safety and reasoning.

### 3.1 Fast Path (Reflex)
`Input -> NeuralHub -> Activation -> Decision`
*   Used for simple commands ("Open calculator").

### 3.2 Slow Path (Contemplation)
`Input -> NeuralHub -> Proposal -> **Memory Check** -> Decision`
*   Before finalizing a decision, NeuralHub queries the **Context Web**.
*   **Contradiction Check:** If the decision contradicts a Major Relation in memory (e.g., "Delete Crypto" when "Project Chaos depends on Crypto"), the confidence score is **penalized**.
*   This allows JARVIS to "think" about consequences before acting.

---

## 4. The Eyes: Adaptive Vision (Assimilated from MAREY)

To process visual data efficiently without supercomputers, JARVIS uses **Adaptive Processing**.

### 4.1 Hardware Intelligence
The `HardwareProfiler` (`JARVIS/core/hardware`) detects system capabilities (CPU/GPU/RAM).
*   **Low-End Device:** Runs lightweight algorithms (MobileNet).
*   **High-End Server:** Runs heavy simulations.

### 4.2 Visual Attention Strategy (Planned)
1.  **Low-Res Scan:** Capture screen at 360p. Identify "Regions of Interest" (ROI).
2.  **Attention Filter:** Crop only the relevant chart/text.
3.  **High-Res Compute:** Send only the crop to the OCR/Vision model.
*   *Result:* 95% reduction in compute load, enabling "Real-Time" vision.

---

## 5. The Research: ORE (Open Research Engine)

The **Research Engine** (`JARVIS/plugins/research_ore`) is an autonomous agent that feeds the Brain.
*   **Ingestion:** Fetches ArXiv papers, PDFs, and (planned) Web Content.
*   **Extraction:** Pulls raw text and summarizes it.
*   **Integration:** Converts findings into "Beliefs" stored in the **Context Web**.

---

## Summary of Flow

1.  **User Input** -> **NeuralHub** (Sensors activate).
2.  **NeuralHub** calculates Confidence based on **Mode** (Strict/Exploratory).
3.  **Contemplation Loop** checks **Memory Graph** for contradictions.
4.  **Decision** is made.
5.  **Action** is executed (Research, Code, or Reply).
6.  **Result** is stored back into **Memory** as a new Fact.
