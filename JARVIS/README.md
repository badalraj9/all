# JARVIS (Project WARHORSE)

> "Sir, I have initialized the system."

JARVIS is an **Autonomous Research & Execution System** that combines:
1.  **SENTRY Neural Hub**: A deterministic "Brain" for decision making.
2.  **MemoryThread**: A "Truth-Aware" memory engine with Cognitive Galaxy Schema.
3.  **ORE**: An LLM-free research engine.
4.  **MAREY**: An adaptive vision system.
5.  **CAPSULE**: A robust plugin architecture.

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Docker & Docker Compose

### Installation

1.  **Clone & Setup**:
    ```bash
    cd JARVIS
    pip install -r requirements.txt
    ```

2.  **Start Infrastructure** (Database & Vector Store):
    ```bash
    docker-compose up -d
    ```

3.  **Run the Console**:
    ```bash
    python -m JARVIS.interfaces.tui.app
    ```

## 🧠 Architecture

-   **`core/`**: The spinal cord (Event Bus, Plugin Loader, Mission Control).
-   **`intelligence/`**: The Brain (Neural Hub, Signals).
-   **`memory/`**: The Memory (PostgreSQL + Truth Maintenance).
-   **`plugins/`**: The Skills (Research, Vision, etc.).

## 🕹️ Usage

In the TUI Command Bar:
-   `Build <Project Name>`: Starts a research & design mission.
    -   *Example:* `Build EDITH`

## 🛠️ Configuration

Edit `.env` or `core/config.py` to change database settings.
