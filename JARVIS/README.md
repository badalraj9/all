# JARVIS: Autonomous Research & Execution System

> "Sir, I have initialized the system."

JARVIS is a **Universal Language Engine (ULE)** implementation designed to solve the "Stochastic Parrot" problem of modern LLMs. It separates **Cognition** (Thinking) from **Control** (Doing), ensuring safe, verifiable, and deterministic execution of complex tasks.

## 📚 Documentation
Detailed architectural documentation for thesis and development:

-   [**01 System Architecture**](docs/01_SYSTEM_ARCHITECTURE.md): The Neural Hub, ULE, and Control Planes.
-   [**02 Memory Galaxy**](docs/02_MEMORY_GALAXY.md): Truth Vectors, Context Web, and Hebbian Learning.
-   [**03 Cognitive Plugins**](docs/03_COGNITIVE_PLUGINS.md): ORE (Research) and MAREY (Saccadic Vision).
-   [**04 Installation & Usage**](docs/04_INSTALLATION_AND_USAGE.md): Setup guide.

## 🚀 Quick Start

1.  **Install**: `pip install -r requirements.txt`
2.  **Infrastructure**: `docker-compose up -d`
3.  **Run**: `python -m JARVIS.interfaces.tui.app`

## 🧠 Key Features
-   **Neural Hub**: A deterministic "Brain" that validates decisions against memory before execution.
-   **Context Web**: A graph-based memory system that learns relationships over time.
-   **Adaptive Vision**: Hardware-aware image processing that mimics human eye movement.
-   **Hybrid Realizer**: Intelligently switches between LLM generation and safe Templates.
