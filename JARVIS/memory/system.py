import json
import uuid
import time
from typing import List, Optional, Dict
from .core_models import MemoryEvent, TruthVector, MemoryType

class MemorySystem:
    """
    Main entry point for JARVIS Memory (Truth Engine).
    Assimilated from MemoryThread, mapped to the schema.
    """
    def __init__(self, postgres_client=None):
        self.postgres = postgres_client

    def log_event(self, actor: str, action: str, object_id: str, payload: Dict, confidence: float = 1.0) -> MemoryEvent:
        """
        Log an event to the immutable ledger.
        """
        authority = 1.0 if actor == "SYSTEM" else 0.5
        event = MemoryEvent.create(actor, action, object_id, payload, confidence, authority)

        if self.postgres:
            self._persist_event(event)

        return event

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
