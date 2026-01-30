# Cognitive Plugins: ORE & MAREY

## 1. The Plugin Architecture
JARVIS uses a modular plugin system (`JARVIS/plugins/`) where capabilities are encapsulated. The two most advanced plugins are **ORE** (Research) and **MAREY** (Vision).

---

## 2. ORE: Open Research Engine
**Location:** `JARVIS/plugins/research_ore/` (Assimilated)

ORE provides the system with the ability to perform **Scientific Reasoning** without hallucinations.

### 2.1. Workflow
1.  **Search**: Queries ArXiv/Google Scholar APIs (via `requests`).
2.  **Ingest**: Downloads PDFs and parses text (via `pymupdf`).
3.  **NLP Analysis**: Uses `spacy` or `transformers` to extract:
    -   **Problem Statement**
    -   **Methodology**
    -   **Results**
4.  **Synthesis**: Generates a JSON summary.

### 2.2. Assimilation Status
The core logic of ORE has been integrated into `JARVIS/plugins/research_ore`. It feeds directly into the Memory Galaxy, creating nodes for `Paper`, `Author`, and `Concept`.

---

## 3. MAREY: Adaptive Vision
**Location:** `JARVIS/plugins/vision_marey/plugin.py`

MAREY implements **Saccadic Vision**, mimicking the human eye's movement to optimize processing.

### 3.1. The Saccadic Pipeline
Processing a 4K image with a large multimodal model (like GPT-4V or LLaVA) is slow and expensive. MAREY solves this:

1.  **Low-Res Scan (Peripheral Vision)**:
    -   Downscales image to 360x360.
    -   Converts to Grayscale.
    -   Applies `ImageFilter.FIND_EDGES` (Sobel/Canny).
    -   Calculates **Variance** (Information Density) in 4 quadrants.

2.  **Attention Filter (Foveation)**:
    -   Selects the quadrant with the highest variance.
    -   Crops this Region of Interest (ROI) from the *original* high-res image.

3.  **Foveal Zoom (Deep Processing)**:
    -   Passes *only the crop* to the heavy VLM (Vision Language Model).
    -   This reduces token count/processing pixels by 75% while maintaining detail where it matters.

### 3.2. Hardware Awareness
The pipeline is hardware-adaptive. On a weak CPU (low `HardwareProfile` score), it skips the Foveal Zoom and relies solely on the Low-Res scan for basic object detection.
