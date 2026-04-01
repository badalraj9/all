# The Memory Galaxy: Context Web & Truth Vectors

## 1. Introduction
Traditional RAG (Retrieval-Augmented Generation) systems rely on vector databases that store "chunks" of text. This approach suffers from **Context Fragmentation**—the system retrieves relevant text but loses the *relationships* between facts.

JARVIS implements the **Context Web**, a directed graph structure (`networkx`) stored in PostgreSQL, augmented with a **Truth Vector** system for handling uncertainty.

---

## 2. The Context Web
**Location:** `JARVIS/memory/system.py`

### 2.1. Graph Structure
The memory is not a flat list of documents. It is a **DiGraph** (Directed Graph) where:
-   **Nodes**: Entities (People, Projects, Concepts) or Events.
-   **Edges**: Typed Relations (`depends_on`, `contradicts`, `relates_to`).

### 2.2. Spreading Activation
Retrieval is performed via **BFS Energy Propagation**:
1.  **Stimulus**: The user mentions "Project Alpha".
2.  **Activation**: The node "Project Alpha" receives `Energy = 1.0`.
3.  **Spread**: Energy flows to neighbors (`Component X`, `Timeline Y`) based on edge weights.
4.  **Decay**: Energy decays by factor `0.5` at each hop.
5.  **Result**: The context window is populated not just by keyword matches, but by *causally related* concepts.

### 2.3. Hebbian Learning
*"Cells that fire together, wire together."*
When the system successfully uses a relation to answer a query, `MemorySystem.hebbian_update()` increments the edge weight. Unused connections decay over time (implementation pending), ensuring relevant memories stay "fresh".

---

## 3. Truth Vectors
**Location:** `JARVIS/memory/core_models.py`

Every memory event contains a **TruthVector** `(c, a, f, r)`:

| Component | Symbol | Definition |
| :--- | :--- | :--- |
| **Confidence** | $c$ | Internal certainty (0.0 - 1.0) of the sensor/model. |
| **Authority** | $a$ | Reliability of the source (User > System > Web). |
| **Freshness** | $f$ | Time-decay factor. |
| **Corroboration** | $r$ | Number of independent sources confirming the fact. |

### 3.1. Conflict Resolution
When two memories contradict (e.g., "Sky is Blue" vs "Sky is Green"), the system calculates the scalar **Truth Score**:
$$ Score = 0.4c + 0.3a + 0.2f + 0.1r $$
The memory with the higher score overwrites the "current state" in the `entity_state` table, but the losing memory is preserved in the `events` log for auditability.

---

## 4. Storage Schema (PostgreSQL)
The graph is persisted in relational tables for robustness:
-   `events`: Immutable log of all updates.
-   `entities`: Unique objects.
-   `relations`: Adjacency list for the graph.
-   `entity_state`: The current "winner" of Truth Vector resolution for each entity.
