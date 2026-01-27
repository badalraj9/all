import json
from datetime import datetime
from typing import Dict, Any, List
import uuid

from JARVIS.core.event_bus import event_bus, Event, EventPriority
from JARVIS.memory.postgres_client import db
from loguru import logger

class MemoryBridge:
    def __init__(self):
        self._setup_subscribers()

    def _setup_subscribers(self):
        event_bus.subscribe("memory.ingest", self.handle_ingest, priority=EventPriority.HIGH)
        event_bus.subscribe("memory.query.*", self.handle_query)

    async def handle_ingest(self, event: Event):
        """
        Handle incoming memory ingestion events.
        Expected data: {
            "actor": "ORE",
            "action": "OBSERVE",
            "object_id": "uuid",
            "payload": {...},
            "truth_vector": {...}
        }
        """
        data = event.data
        try:
            event_id = str(uuid.uuid4())
            object_id = data.get("object_id")

            # 1. Write Event Log
            db.execute(
                """
                INSERT INTO events (id, actor, action, object_id, payload, truth_vector)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    event_id,
                    data.get("actor", "SYSTEM"),
                    data.get("action", "OBSERVE"),
                    object_id,
                    json.dumps(data.get("payload", {})),
                    json.dumps(data.get("truth_vector", {}))
                )
            )

            # 2. Update Entity State (Upsert)
            # Simplistic Last-Write-Wins for now, but supports Galaxy expansion later
            db.execute(
                """
                INSERT INTO entity_state (entity_id, namespace, current_value, truth_vector, last_event_id)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (entity_id) DO UPDATE SET
                    current_value = EXCLUDED.current_value,
                    truth_vector = EXCLUDED.truth_vector,
                    last_event_id = EXCLUDED.last_event_id,
                    updated_at = NOW(),
                    version = entity_state.version + 1
                """,
                (
                    object_id,
                    "default", # Namespace
                    json.dumps(data.get("payload", {})),
                    json.dumps(data.get("truth_vector", {})),
                    event_id
                )
            )

            logger.info(f"Memory Ingested: {object_id} by {data.get('actor')}")

        except Exception as e:
            logger.error(f"Memory Ingestion Failed: {e}")

    async def handle_query(self, event: Event):
        # Placeholder for query handling logic
        pass

    def get_galaxy_belief(self, entity_id: str, agent_id: str) -> Dict[str, Any]:
        """Query the Cognitive Galaxy for a specific agent's belief."""
        return db.fetch_one(
            "SELECT * FROM beliefs WHERE entity_id = %s AND agent_id = %s",
            (entity_id, agent_id)
        )

# Initialize
memory_bridge = MemoryBridge()
