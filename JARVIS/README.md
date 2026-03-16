# JARVIS (Project WARHORSE)

> *"Sir, I have initialized the system."*

**JARVIS** (Just A Rather Very Intelligent System) is an **Autonomous Research & Execution System** designed to autonomously research, plan, and execute complex tasks through a deterministic cognitive architecture. It combines neural decision-making, truth-aware memory, and pluggable skill systems.

---

## Overview

JARVIS is an AI assistant that:
- **Understands** natural language commands via the ULE (Universal Language Engine)
- **Decides** when to act using the SENTRY Neural Hub
- **Remembers** everything in a PostgreSQL-backed truth-aware memory system
- **Researches** autonomously using ORE (Omniscient Research Engine)
- **Perceives** visual context through MAREY (Machine Adaptive REception Yield)
- **Extends** via a robust plugin architecture (CAPSULE)

---

## System Specification

### Core Capabilities

| Component | Description |
|-----------|-------------|
| **ULE Engine** | Universal Language Engine - Processes user input, extracts semantic anchors, generates hypotheses, and selects optimal conversational moves (ACK, CLARIFY, PROPOSE, REFUSE, etc.) |
| **SENTRY Neural Hub** | Deterministic decision brain - Aggregates linguistic, structural, contextual, and temporal signals to determine when to propose actions |
| **MemoryThread** | Truth-aware memory engine - Stores events, entity states, and beliefs with confidence vectors in PostgreSQL |
| **ORE Plugin** | LLM-free research engine - Fetches real ArXiv papers, extracts entities, and identifies linguistic patterns |
| **MAREY Plugin** | Vision system - Captures screenshots, performs OCR/anomaly detection (sandboxed for headless operation) |
| **Mission Control** | Dynamic task planner - Generates task graphs, manages dependencies, handles failures with self-healing replanning |
| **Event Bus** | Asynchronous pub/sub message broker with priority queuing and pattern matching |

### Input/Output

- **Input**: Natural language commands via TUI (e.g., "Build EDITH", "Research quantum computing")
- **Output**: Executed tasks, research findings, UI log messages, stored memories

### Data Flow

1. User enters command in TUI
2. ULE Engine processes input → extracts anchors → generates hypotheses → selects move
3. If move is PROPOSE → Mission Control creates task graph
4. Tasks execute via Event Bus → Plugins respond
5. Results stored in MemoryThread
6. UI updates with progress

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              INTERFACES                                     │
│  ┌─────────────────────────────────┐    ┌─────────────────────────────────┐ │
│  │        TUI (Text UI)            │    │      WATCHDOG (Future API)      │ │
│  │   python -m JARVIS.interfaces. │    │      FastAPI + WebSocket       │ │
│  │            tui.app              │    │                                 │ │
│  └─────────────────────────────────┘    └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                CORE                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │  EVENT BUS  │  │   MISSION   │  │    PLUGIN   │  │      ULE        │  │
│  │  (Pub/Sub)  │  │  CONTROL    │  │    LOADER   │  │    ENGINE       │  │
│  │             │  │ (Task Graph)│  │             │  │ (Cognitive Plane)│ │
│  └─────────────┘  └─────────────┘  └──────────────┘  └─────────────────┘  │
│         │                │                │                  │          │
│         │    ┌───────────┴────────┐        │                  │          │
│         │    │       CONFIG       │        │                  │          │
│         │    │  (Settings/.env)   │        │                  │          │
│         │    └────────────────────┘        │                  │          │
└─────────┼─────────────────────────┼────────┼──────────────────┼──────────┘
          │                         │        │                  │
          ▼                         ▼        ▼                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              INTELLIGENCE                                   │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        SENTRY NEURAL HUB                             │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌──────────────┐ ┌─────────────┐   │   │
│  │  │  Linguistic│ │ Structural │ │ Contextual   │ │  Temporal  │   │   │
│  │  │   Sensor   │ │   Sensor   │ │   Sensor     │ │   Sensor   │   │   │
│  │  └─────────────┘ └─────────────┘ └──────────────┘ └─────────────┘   │   │
│  │                              │                                        │   │
│  │                    ┌─────────┴────────┐                               │   │
│  │                    │   SYNAPTIC      │                               │   │
│  │                    │   PROCESSOR      │                               │   │
│  │                    │ (Aggregate+Activ8)│                              │   │
│  │                    └──────────────────┘                               │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────────────┐    │
│  │  Math Utils     │  │   Text Utils     │  │      Constants          │    │
│  │ (sigmoid, beta) │  │ (tokenize, jaccard)│ │   (weights, patterns)  │    │
│  └─────────────────┘  └──────────────────┘  └─────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                MEMORY                                       │
│  ┌─────────────────────┐              ┌────────────────────────────────┐   │
│  │    MEMORY BRIDGE    │──────────────▶│      POSTGRESQL CLIENT        │   │
│  │   (Event Handler)  │              │  (Truth-Aware Storage)         │   │
│  └─────────────────────┘              └────────────────────────────────┘   │
│                                              │                             │
│                                     ┌────────┴────────┐                   │
│                                     │   QDRANT       │                   │
│                                     │ (Vector Store)  │                   │
│                                     │ (Future Use)    │                   │
│                                     └─────────────────┘                   │
└─────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                               PLUGINS                                       │
│  ┌────────────────────────┐              ┌────────────────────────────┐    │
│  │     ORE PLUGIN        │              │       MAREY PLUGIN         │    │
│  │  ─────────────────    │              │  ──────────────────────    │    │
│  │ • ArXiv Fetch        │              │  • Screenshot Capture      │    │
│  │ • Entity Extraction  │              │  • OCR / Anomaly Detect    │    │
│  │ • Pattern Learning   │              │  • Visual Context Analyze  │    │
│  └────────────────────────┘              └────────────────────────────┘    │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    CAPSULE (Plugin Architecture)                     │   │
│  │  • manifest.json Discovery  • Async Initialize/Cleanup               │   │
│  │  • Event Subscription        • BasePlugin Abstract Class              │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Workflow

```
┌──────────────┐
│   USER       │
│  "Build X"   │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           1. ULE PROCESSING                                 │
│                                                                             │
│  ┌─────────────┐    ┌─────────────────┐    ┌──────────────────┐           │
│  │   INPUT     │───▶│ ANCHOR EXTRACTOR │───▶│   HYPOTHESIS    │           │
│  │ "Build X"   │    │ (spaCy NER/Dep)  │    │   GENERATOR     │           │
│  └─────────────┘    └─────────────────┘    │  (Intent + Risk) │           │
│                                            └────────┬─────────┘           │
│                                                     │                      │
│                                                     ▼                      │
│                                            ┌──────────────────┐           │
│                                            │  MOVE SELECTOR   │           │
│                                            │ (ACK/CLARIFY/    │           │
│                                            │  PROPOSE/REFUSE) │           │
│                                            └────────┬─────────┘           │
│                                                     │                      │
│                    ┌───────────────────────────────┘                      │
│                    │                                                       │
│                    ▼                                                       │
│           ┌─────────────────┐                                              │
│           │   REALIZER      │                                              │
│           │ (NLG Response)  │                                              │
│           └────────┬────────┘                                              │
└────────────────────┼───────────────────────────────────────────────────────┘
                     │
         ┌──────────┴──────────┐
         │                     │
         ▼                     ▼
┌─────────────────────┐  ┌──────────────────────────┐
│      MOVE:          │  │       MOVE:              │
│    CLARIFY          │  │      PROPOSE            │
│                     │  │                          │
│ "Did you mean...?"  │  │ "I'll build X.           │
│                     │  │  Starting mission..."    │
└─────────────────────┘  └───────────┬──────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        2. MISSION CONTROL                                   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      TASK GRAPH GENERATION                           │   │
│  │                                                                      │   │
│  │   ┌──────────┐      ┌──────────────┐      ┌──────────────────┐      │   │
│  │   │Research │─────▶│Design Draft  │─────▶│ Visual Analysis  │      │   │
│  │   │   #1    │      │     #2       │      │        #3        │      │   │
│  │   └──────────┘      └──────────────┘      └──────────────────┘      │   │
│  │       │                                                        │      │   │
│  │       │           (Dependency Graph)                           │      │   │
│  └───────┼────────────────────────────────────────────────────────┘────┘   │
│          │                                                                   │
│          ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     TASK EXECUTION LOOP                               │   │
│  │                                                                      │   │
│  │   1. Get executable tasks (dependencies met)                        │   │
│  │   2. Consult Neural Hub (should we proceed?)                        │   │
│  │   3. Emit event: "research.start", "vision.analyze", etc.           │   │
│  │   4. Wait for completion event                                       │   │
│  │   5. On success → Next task                                         │   │
│  │   6. On failure → REPLAN (self-healing)                            │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         3. PLUGIN EXECUTION                                 │
│                                                                             │
│  ┌───────────────────────┐    ┌───────────────────────────┐                │
│  │   ORE RESEARCH       │    │      MAREY VISION         │                │
│  │                       │    │                           │                │
│  │ 1. Fetch ArXiv       │    │ 1. Capture Screenshot     │                │
│  │ 2. Parse XML         │    │ 2. Run OCR (simulated)    │                │
│  │ 3. Extract Entities │    │ 3. Detect Anomalies       │                │
│  │ 4. Pattern Learning │    │ 4. Return Analysis        │                │
│  │                       │    │                           │                │
│  │  Emit:                │    │  Emit:                     │                │
│  │  • research.complete │    │  • vision.complete         │                │
│  │  • memory.ingest    │    │                            │                │
│  └───────────────────────┘    └───────────────────────────┘                │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          4. MEMORY INGESTION                                │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                       │   │
│  │   ┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐   │   │
│  │   │   EVENT     │───▶│   POSTGRESQL    │    │    QDRANT       │   │   │
│  │   │   LOG       │    │   (Facts/Events)│    │   (Vectors)     │   │   │
│  │   │             │    │                 │    │                 │   │   │
│  │   │ • actor     │    │ INSERT events   │    │ Future: Semantic│   │   │
│  │   │ • action    │    │ UPSERT entity   │    │    Search       │   │   │
│  │   │ • object_id │    │                 │    │                 │   │   │
│  │   │ • payload   │    │                  │    │                 │   │   │
│  │   │ • truth_vec│    │                  │    │                 │   │   │
│  │   └─────────────┘    └─────────────────┘    └─────────────────┘   │   │
│  │                                                                       │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              5. UI FEEDBACK                                  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                       │   │
│  │   • Brain Monitor: Trust Score, Ambiguity, Current Move            │   │
│  │   • Mission Monitor: Pending Tasks, Status                        │   │
│  │   • Log View: Real-time Event Stream                               │   │
│  │                                                                       │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Setup

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| **Python** | 3.10+ | Required for async/await support |
| **Docker** | Latest | For PostgreSQL & Qdrant |
| **Docker Compose** | Latest | For orchestrating containers |
| **spaCy Model** | en_core_web_sm | Run: `python -m spacy download en_core_web_sm` |

### Installation Steps

#### 1. Clone the Repository

```bash
git clone https://github.com/your-org/JARVIS.git
cd JARVIS
```

#### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Download spaCy Models

```bash
python -m spacy download en_core_web_sm
```

#### 5. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=jarvis_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Vector Store
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Optional: Skip DB (for development without Docker)
# JARVIS_SKIP_DB=true
```

#### 6. Start Infrastructure (Docker)

```bash
docker-compose up -d
```

This starts:
- **PostgreSQL** (port 5432) - Truth-aware memory storage
- **Qdrant** (port 6333) - Vector similarity search (reserved for future use)

#### 7. Run JARVIS

```bash
python -m JARVIS.interfaces.tui.app
```

---

## Usage

### Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `Build <Project>` | Research and design a project | `Build EDITH` |
| `Research <Topic>` | Search ArXiv for papers | `Research quantum computing` |
| `Vision` | Analyze current screen | `Vision` |
| `Status` | Show system status | `Status` |
| `Help` | Show available commands | `Help` |

### TUI Controls

- **Enter**: Submit command
- **Ctrl+C**: Exit application

### Example Session

```
┌──────────────────────────────────────────────────────────────────────┐
│ 🧠 ULE BRAIN: ONLINE      │ 🛡️ MISSION CONTROL: READY                │
│ Trust: 0.50               │ Tasks Pending: 0                         │
│ Ambiguity: ---           │                                           │
│ Move: IDLE               │                                           │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  10:30:15 | INFO | JARVIS SYSTEM INITIALIZING (ULE KERNEL)...       │
│  10:30:16 | INFO | Plugins Loaded.                                  │
│  10:30:16 | INFO | Connected to PostgreSQL                          │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│ Enter command...                                                      │
│ > Build EDITH                                                        │
│                                                                      │
│  10:30:25 | INFO | USER: Build EDITH                                 │
│  10:30:25 | INFO | JARVIS: Proceeding with: User wants to build     │
│                              Project EDITH                           │
│  10:30:25 | INFO | Initiating Mission from ULE: Build EDITH         │
│  10:30:25 | INFO | Task added: Research Build EDITH (a1b2c3d4)     │
│  10:30:25 | INFO | Task added: Draft Architecture for Build EDITH   │
│                                                                      │
│  10:30:26 | INFO | Executing: Research Build EDITH                 │
│  10:30:26 | INFO | ORE: Fetching real ArXiv papers for 'Build...'  │
│  10:30:28 | INFO | ORE: Extracted 5 linguistic patterns             │
│                                                                      │
│  10:30:28 | INFO | Task Complete: Research Build EDITH              │
│  10:30:28 | INFO | Executing: Draft Architecture for Build EDITH     │
│                                                                      │
│  10:30:30 | INFO | Task Complete: Draft Architecture for Build...  │
│  10:30:30 | INFO | Mission Complete.                                │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PROJECT_NAME` | JARVIS | System name |
| `MAX_EVENT_HISTORY` | 1000 | Event bus history size |
| `POSTGRES_*` | (see `.env`) | Database connection |
| `QDRANT_*` | (see `.env`) | Vector store connection |
| `JARVIS_SKIP_DB` | false | Skip DB connection (dev mode) |

### Plugin Configuration

Plugins are auto-discovered from the `plugins/` directory. Each plugin must have:

```
plugins/
└── <plugin_name>/
    ├── manifest.json      # Plugin metadata
    └── plugin.py          # Implementation
```

**manifest.json schema:**

```json
{
    "plugin_id": "unique_plugin_id",
    "name": "Human Readable Name",
    "version": "1.0.0",
    "description": "What this plugin does",
    "entry_point": "module.ClassName",
    "capabilities": ["capability1", "capability2"]
}
```

---

## Project Structure

```
JARVIS/
├── core/                      # Core system components
│   ├── config.py              # Settings & configuration
│   ├── event_bus.py           # Async pub/sub message broker
│   ├── mission_control.py     # Task graph execution engine
│   ├── plugin_loader.py       # Dynamic plugin discovery
│   └── ule/                   # Universal Language Engine
│       ├── cognitive.py       # Anchor extraction & hypothesis generation
│       ├── control.py         # Move selection logic
│       ├── dynamics.py        # State update rules
│       ├── engine.py          # Main ULE loop
│       ├── realizer.py       # Natural language generation
│       └── types.py          # Data types & enums
│
├── intelligence/              # Neural decision system
│   ├── constants.py          # Weights & patterns
│   ├── math_utils.py         # Sigmoid, beta distribution
│   ├── neural_hub.py         # Signal aggregation & decision
│   └── text_utils.py         # Tokenization & similarity
│
├── memory/                    # Truth-aware storage
│   ├── bridge.py             # Event → DB ingestion
│   ├── postgres_client.py    # PostgreSQL connection
│   └── schema.sql            # Database schema
│
├── plugins/                   # Extensible skills
│   ├── base_plugin.py        # Abstract base class
│   ├── research_ore/          # ArXiv research plugin
│   └── vision_marey/        # Screen capture plugin
│
├── interfaces/                # User interfaces
│   ├── tui/                  # Text-based UI
│   │   └── app.py           # Main TUI application
│   └── watchdog.py          # Future API interface
│
├── docker-compose.yml        # Infrastructure containers
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `OSError: en_core_web_sm not found` | spaCy model not installed | Run: `python -m spacy download en_core_web_sm` |
| `Connection refused to localhost:5432` | PostgreSQL not running | Run: `docker-compose up -d` |
| `Plugin not loading` | Missing `manifest.json` | Check plugin directory structure |
| `No DISPLAY detected` | Headless server | MAREY runs in mock mode automatically |

### Development Mode

To run without Docker (in-memory state only):

```bash
export JARVIS_SKIP_DB=true
python -m JARVIS.interfaces.tui.app
```

---

## License

MIT License - See LICENSE file for details.

---

## Credits

Built with:
- **spaCy** - NLP processing
- **Textual** - TUI framework
- **PostgreSQL** - Relational storage
- **Qdrant** - Vector search
- **NetworkX** - Task graph management
- **Loguru** - Logging

---

> *"I'm not going to fail, sir. I'm going to succeed."* — JARVIS
