import json
import uuid
import time
from typing import List, Optional, Dict
import networkx as nx
from .core_models import MemoryEvent, TruthVector, MemoryType, Relation, RelationType

class MemorySystem:
    """
    Main entry point for JARVIS Memory (Truth Engine).
    Enhanced with REAL NetworkX Graph Dynamics.
    """
    def __init__(self, postgres_client=None):
        self.postgres = postgres_client
        self.graph = nx.DiGraph() # Real Graph

    def log_event(self, actor: str, action: str, object_id: str, payload: Dict, confidence: float = 1.0) -> MemoryEvent:
        authority = 1.0 if actor == "SYSTEM" else 0.5
        event = MemoryEvent.create(actor, action, object_id, payload, confidence, authority)

        # Auto-add node to graph
        if not self.graph.has_node(object_id):
            self.graph.add_node(object_id, type="entity", payload=payload)

        if self.postgres:
            self._persist_event(event)

        return event

    def add_relation(self, source_id: str, target_id: str, relation_type: str, weight: float = 1.0):
        try:
            rtype = RelationType(relation_type)
        except ValueError:
            return

        # NetworkX Edge
        self.graph.add_edge(source_id, target_id, type=rtype, weight=weight)

        # Hebbian Update (Strengthen)
        self.hebbian_update(source_id, target_id)

    def get_related_entities(self, entity_id: str, relation_type: Optional[str] = None) -> List[Dict]:
        results = []
        if self.graph.has_node(entity_id):
            # Outgoing edges
            for neighbor in self.graph.successors(entity_id):
                edge_data = self.graph.get_edge_data(entity_id, neighbor)
                if relation_type is None or edge_data["type"].value == relation_type:
                    results.append({
                        "target_id": neighbor,
                        "type": edge_data["type"].value,
                        "weight": edge_data["weight"]
                    })
        return results

    def spread_activation(self, start_node_id: str, initial_energy: float = 1.0, decay: float = 0.5) -> Dict[str, float]:
        """
        Real BFS Activation Spreading.
        """
        if not self.graph.has_node(start_node_id):
            return {}

        activated = {}
        queue = [(start_node_id, initial_energy)]
        visited = set()

        while queue:
            curr, energy = queue.pop(0)

            if curr in visited: continue
            visited.add(curr)

            activated[curr] = energy

            # Stop if energy too low
            if energy < 0.1: continue

            # Spread to neighbors
            for neighbor in self.graph.successors(curr):
                edge_weight = self.graph[curr][neighbor]["weight"]
                new_energy = energy * edge_weight * decay
                queue.append((neighbor, new_energy))

        return activated

    def hebbian_update(self, node_a: str, node_b: str):
        """
        Real Hebbian Learning: Increment weight.
        """
        if self.graph.has_edge(node_a, node_b):
            curr_weight = self.graph[node_a][node_b]["weight"]
            new_weight = min(curr_weight + 0.05, 2.0) # Cap at 2.0
            self.graph[node_a][node_b]["weight"] = new_weight

    def _persist_event(self, event: MemoryEvent):
        """
        Persist the event to PostgreSQL `events` table.
        """
        query = """
        INSERT INTO events (id, actor, action, object_id, payload, truth_vector, timestamp, antecedents)
        VALUES (%s, %s, %s, %s, %s, %s, to_timestamp(%s), %s)
        """
        if hasattr(self.postgres, "execute"):
            try:
                self.postgres.execute(query, (
                    event.id,
                    event.actor,
                    event.action,
                    event.object_id,
                    json.dumps(event.payload),
                    json.dumps(event.truth_vector.to_json()),
                    event.timestamp,
                    event.antecedents
                ))
            except Exception as e:
                pass

    def get_latest_state(self, object_id: str) -> Optional[Dict]:
        if self.postgres and hasattr(self.postgres, "fetch_one"):
             sql = "SELECT current_value, truth_vector FROM entity_state WHERE entity_id = %s"
             row = self.postgres.fetch_one(sql, (object_id,))
             if row:
                 return {"value": row[0], "truth": row[1]}
        return None

    def get_conversation_context(self) -> Dict:
        return {"topic": None, "entity": None, "goals": []}
