import json
import uuid
import time
from typing import List, Optional, Dict
from .core_models import MemoryEvent, TruthVector, MemoryType, Relation, RelationType

class MemorySystem:
    """
    Main entry point for JARVIS Memory (Truth Engine).
    Assimilated from MemoryThread, mapped to the schema.
    Enhanced with Context Web (Graph) capabilities.
    """
    def __init__(self, postgres_client=None):
        self.postgres = postgres_client
        self.graph = {} # In-memory graph cache: source_id -> [Relation]

    def log_event(self, actor: str, action: str, object_id: str, payload: Dict, confidence: float = 1.0) -> MemoryEvent:
        """
        Log an event to the immutable ledger.
        """
        authority = 1.0 if actor == "SYSTEM" else 0.5
        event = MemoryEvent.create(actor, action, object_id, payload, confidence, authority)

        if self.postgres:
            self._persist_event(event)

        return event

    def add_relation(self, source_id: str, target_id: str, relation_type: str, weight: float = 1.0):
        """
        Add a semantic edge to the Context Web.
        """
        try:
            rtype = RelationType(relation_type)
        except ValueError:
            print(f"Invalid relation type: {relation_type}")
            return

        relation = Relation(source_id, target_id, rtype, weight)

        # Update Cache
        if source_id not in self.graph:
            self.graph[source_id] = []
        self.graph[source_id].append(relation)

        # Persist (Mocked for now, but would use `relations` table)
        if self.postgres and hasattr(self.postgres, "execute"):
             query = """
             INSERT INTO relations (source_entity_id, target_entity_id, relation_type, confidence)
             VALUES (%s, %s, %s, %s)
             ON CONFLICT DO NOTHING
             """
             try:
                 self.postgres.execute(query, (source_id, target_id, relation_type, weight))
             except: pass

        # TRIGGER: Hebbian Update (Strengthen connection)
        self.hebbian_update(source_id, target_id)

    def get_related_entities(self, entity_id: str, relation_type: Optional[str] = None) -> List[Dict]:
        """
        Traverse the Context Web.
        """
        results = []
        if entity_id in self.graph:
            for rel in self.graph[entity_id]:
                if relation_type is None or rel.relation_type.value == relation_type:
                    results.append({
                        "target_id": rel.target_id,
                        "type": rel.relation_type.value,
                        "weight": rel.weight
                    })
        return results

    def spread_activation(self, start_node_id: str, initial_energy: float = 1.0, decay: float = 0.5) -> Dict[str, float]:
        """
        Simulates 'Thinking' by spreading energy through the Context Web.

        LOGIC:
        1. Start at `start_node_id` with `initial_energy`.
        2. Propagate to neighbors: Energy = Current * EdgeWeight * Decay.
        3. Stop when Energy < threshold (e.g., 0.1).

        Returns:
            Dict of {node_id: activation_level} - The "Context" for the current thought.
        """
        # Logic Placeholder
        activated_nodes = {start_node_id: initial_energy}
        # queue = [(start_node_id, initial_energy)]
        # while queue:
        #    curr, energy = queue.pop(0)
        #    for neighbor in self.graph[curr]:
        #        new_energy = energy * neighbor.weight * decay
        #        if new_energy > 0.1:
        #            activated_nodes[neighbor.id] = new_energy
        #            queue.append((neighbor.id, new_energy))
        return activated_nodes

    def hebbian_update(self, node_a: str, node_b: str):
        """
        'Neurons that fire together, wire together.'

        LOGIC:
        1. Check if Edge(A, B) exists.
        2. If yes, increase weight slightly (e.g., += 0.05).
        3. Cap weight at 1.0.
        4. If no edge, create a weak 'ASSOCIATED_WITH' edge (0.1).
        """
        # Logic Placeholder
        pass

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
                # In a real system we would log this better
                print(f"Memory Persistence Error: {e}")

    def get_latest_state(self, object_id: str) -> Optional[Dict]:
        """
        Get the current consensus state of an entity.
        """
        if self.postgres and hasattr(self.postgres, "fetch_one"):
             sql = "SELECT current_value, truth_vector FROM entity_state WHERE entity_id = %s"
             row = self.postgres.fetch_one(sql, (object_id,))
             if row:
                 return {
                     "value": row[0], # JSONB automatically deserialized by most drivers
                     "truth": row[1]
                 }
        return None

    def get_conversation_context(self) -> Dict:
        """
        Retrieve the current ULE Conversation State.
        """
        # Placeholder: This would likely query a specific "Conversation" entity in a real flow
        return {
            "topic": None,
            "entity": None,
            "goals": []
        }
