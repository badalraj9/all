# Installation & Usage Guide

## 1. Prerequisites
-   **OS**: Linux (Ubuntu 22.04+) or macOS.
-   **Python**: 3.10 or higher.
-   **Docker**: Required for PostgreSQL and Qdrant (Vector DB).
-   **RAM**:
    -   8GB (Mock Mode / Testing)
    -   24GB+ (AirLLM Llama-2-70B Inference)

## 2. Installation

### 2.1. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/your-repo/JARVIS.git
cd JARVIS

# Create Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Install Dependencies
# Note: For heavy ML features, ensure you have CUDA drivers installed.
pip install -r JARVIS/requirements.txt
```

### 2.2. Infrastructure Setup
Start the required databases using Docker Compose:
```bash
cd JARVIS
docker-compose up -d
```
*This starts PostgreSQL on port 5432 and Qdrant on port 6333.*

## 3. Running JARVIS

### 3.1. Text User Interface (TUI)
The primary interface is a hacker-style terminal UI built with `textual`.
```bash
python -m JARVIS.interfaces.tui.app
```

### 3.2. Verification Tests
To verify the system integrity:
```bash
# Test the Neural Hub Decision Engine
python JARVIS/tests/test_neural_hub.py

# Test Memory Graph
python JARVIS/tests/test_memory.py
```

## 4. Configuration
Modify `JARVIS/.env` (create it if missing) to set API keys or Database URLs:
```ini
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=jarvis_db
LLM_MODEL_PATH=meta-llama/Llama-2-7b-chat-hf
```

## 5. Troubleshooting
-   **"PyTorch not found"**: The system will automatically degrade to **Mock Mode**. You can still test logic and flows, but LLM generation will be simulated.
-   **Docker Connection Refused**: Ensure `docker-compose` is running and ports are not blocked by a firewall.
