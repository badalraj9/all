import networkx as nx
import asyncio
from typing import Dict, List, Any, Optional, Literal
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import json

from JARVIS.core.event_bus import event_bus, Event, EventPriority
from JARVIS.intelligence.neural_hub import neural_hub, ProcessingContext, NeuralState
from JARVIS.memory.bridge import memory_bridge
from JARVIS.memory.postgres_client import db
from loguru import logger

@dataclass
class Task:
    id: str
    description: str
    status: Literal['pending', 'running', 'completed', 'failed', 'blocked'] = 'pending'
    action: str = "" # e.g. "research.start"
    payload: Dict[str, Any] = field(default_factory=dict)
    result: Any = None
    created_at: datetime = field(default_factory=datetime.now)
    dependencies: List[str] = field(default_factory=list)

class DynamicGraphEngine:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.tasks: Dict[str, Task] = {}
        self.active_mission_id: Optional[str] = None

        self._setup_subscribers()

        # Internal State
        self.neural_state = NeuralState(user_id="jarvis_admin", project_id="mission_1")

    def _setup_subscribers(self):
        event_bus.subscribe("mission.create", self.handle_mission_create)
        event_bus.subscribe("task.complete", self.handle_task_complete)
        event_bus.subscribe("task.fail", self.handle_task_fail)
        event_bus.subscribe("system.startup", self.handle_startup)

    def add_task(self, description: str, action: str, payload: Dict[str, Any], depends_on: List[str] = []) -> str:
        task_id = str(uuid.uuid4())[:8]
        task = Task(id=task_id, description=description, action=action, payload=payload, dependencies=depends_on)

        self.tasks[task_id] = task
        self.graph.add_node(task_id, data=task)

        for dep_id in depends_on:
            if dep_id in self.tasks:
                self.graph.add_edge(dep_id, task_id)
            else:
                logger.warning(f"Dependency {dep_id} not found for task {task_id}")

        logger.info(f"Task added: {description} ({task_id})")
        self._persist_state() # Save state on change
        return task_id

    def get_executable_tasks(self) -> List[Task]:
        """Get tasks that are pending and have all dependencies met."""
        executable = []
        for node in self.graph.nodes():
            task = self.tasks[node]
            if task.status == 'pending':
                # Check dependencies
                predecessors = list(self.graph.predecessors(node))
                if all(self.tasks[p].status == 'completed' for p in predecessors):
                    executable.append(task)
        return executable

    async def run_cycle(self):
        """Main execution loop."""
        executable = self.get_executable_tasks()

        if not executable:
            # Check if all done
            if self.tasks and all(t.status == 'completed' for t in self.tasks.values()):
                logger.info("Mission Complete.")
                self.active_mission_id = None
                self._persist_state()
            return

        for task in executable:
            await self.execute_task(task)

    async def execute_task(self, task: Task):
        logger.info(f"Executing: {task.description}")
        task.status = 'running'
        self._persist_state()

        # 1. Consult Neural Hub
        should_proceed = self._consult_neural_hub(task)
        if not should_proceed:
            logger.warning(f"Neural Hub aborted task: {task.description}")
            task.status = 'failed'
            self._persist_state()
            return

        # 2. Emit Action Event
        await event_bus.emit(task.action, task.payload, source="mission_control")

    def _consult_neural_hub(self, task: Task) -> bool:
        # Mocking a context for the Neural Hub
        ctx = ProcessingContext(
            chat_type="mission",
            is_author_maintainer=True,
            participant_count=1,
            thread_depth=1,
            reaction_count=0,
            reply_count=0,
            recent_msg_rate=0,
            avg_msg_rate=0,
            active_intent=task.description,
            message_timestamp=datetime.now(),
            discussion_start_time=datetime.now()
        )
        return True

    async def handle_mission_create(self, event: Event):
        goal = event.data.get('goal')
        logger.info(f"New Mission: {goal}")

        # Reset current graph for new mission (simplification)
        self.graph.clear()
        self.tasks.clear()
        self.active_mission_id = str(uuid.uuid4())

        # Simple LLM-simulation: Manually create tasks for now
        # In real JARVIS, this is where we'd ask ORE/LLM to generate the plan
        t1 = self.add_task(f"Research {goal}", "research.start", {"query": goal})
        self.add_task(f"Design {goal}", "design.draft", {}, depends_on=[t1])

        await self.run_cycle()

    async def handle_task_complete(self, event: Event):
        # Infer task ID from event or context
        # For this prototype, we assume single-threaded execution or clear mapping
        # We need a way to link result back to task.
        # Simplification: We look for running tasks with matching action type
        # In prod, we'd pass correlation_id

        completed_task = None
        for task in self.tasks.values():
            if task.status == 'running':
                # Heuristic match
                completed_task = task
                break

        if completed_task:
            completed_task.status = 'completed'
            completed_task.result = event.data
            logger.info(f"Task Complete: {completed_task.description}")
            self._persist_state()
            await self.run_cycle()

    async def handle_task_fail(self, event: Event):
        logger.error("Task failed.")

    # =========================================================================
    # PERSISTENCE & RESUME
    # =========================================================================

    def _persist_state(self):
        """Save current graph state to Postgres."""
        if not self.active_mission_id:
            return

        state_payload = {
            "tasks": [
                {
                    "id": t.id,
                    "description": t.description,
                    "status": t.status,
                    "action": t.action,
                    "payload": t.payload,
                    "dependencies": t.dependencies
                }
                for t in self.tasks.values()
            ]
        }

        # We use MemoryBridge to save this as a "System State" entity
        try:
             # Using raw SQL via db client for direct access
            db.execute(
                """
                INSERT INTO entity_state (entity_id, namespace, current_value, truth_vector, last_event_id, updated_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
                ON CONFLICT (entity_id) DO UPDATE SET
                    current_value = EXCLUDED.current_value,
                    updated_at = NOW()
                """,
                (
                    self.active_mission_id,
                    "system_state",
                    json.dumps(state_payload),
                    json.dumps({"confidence": 1.0}),
                    str(uuid.uuid4())
                )
            )
        except Exception as e:
            logger.warning(f"Failed to persist mission state: {e}")

    async def handle_startup(self, event: Event):
        """Called when JARVIS boots up."""
        logger.info("Checking for interrupted missions...")
        try:
            # Query for the most recent active system state
            row = db.fetch_one(
                """
                SELECT entity_id, current_value
                FROM entity_state
                WHERE namespace = 'system_state'
                ORDER BY updated_at DESC
                LIMIT 1
                """
            )

            if row:
                data = row.get('current_value')
                if isinstance(data, str):
                    data = json.loads(data)

                # Check if tasks are still pending
                tasks_data = data.get('tasks', [])
                has_pending = any(t['status'] in ['pending', 'running'] for t in tasks_data)

                if has_pending:
                    logger.info("Resuming previous mission...")
                    self.active_mission_id = str(row['entity_id'])
                    self.graph.clear()
                    self.tasks.clear()

                    # Rebuild Graph
                    for t_data in tasks_data:
                        task = Task(
                            id=t_data['id'],
                            description=t_data['description'],
                            status=t_data['status'],
                            action=t_data['action'],
                            payload=t_data['payload'],
                            dependencies=t_data['dependencies']
                        )
                        self.tasks[task.id] = task
                        self.graph.add_node(task.id, data=task)

                    # Rebuild Edges
                    for t in self.tasks.values():
                        for dep in t.dependencies:
                            if dep in self.tasks:
                                self.graph.add_edge(dep, t.id)

                    # Resume execution
                    logger.info(f"Restored {len(self.tasks)} tasks.")
                    await self.run_cycle()
                else:
                    logger.info("No active missions to resume.")
            else:
                logger.info("No mission history found.")

        except Exception as e:
            logger.error(f"Startup resume failed: {e}")

mission_control = DynamicGraphEngine()
