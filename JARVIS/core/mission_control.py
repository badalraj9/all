import networkx as nx
import asyncio
from typing import Dict, List, Any, Optional, Literal
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from JARVIS.core.event_bus import event_bus, Event
from JARVIS.intelligence.neural_hub import neural_hub, ProcessingContext, NeuralState
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

class DynamicGraphEngine:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.tasks: Dict[str, Task] = {}
        self._setup_subscribers()

        # Internal State
        self.neural_state = NeuralState(user_id="jarvis_admin", project_id="mission_1")

    def _setup_subscribers(self):
        event_bus.subscribe("mission.create", self.handle_mission_create)
        event_bus.subscribe("task.complete", self.handle_task_complete)
        event_bus.subscribe("task.fail", self.handle_task_fail)

    def add_task(self, description: str, action: str, payload: Dict[str, Any], depends_on: List[str] = []) -> str:
        task_id = str(uuid.uuid4())[:8]
        task = Task(id=task_id, description=description, action=action, payload=payload)

        self.tasks[task_id] = task
        self.graph.add_node(task_id, data=task)

        for dep_id in depends_on:
            if dep_id in self.tasks:
                self.graph.add_edge(dep_id, task_id)
            else:
                logger.warning(f"Dependency {dep_id} not found for task {task_id}")

        logger.info(f"Task added: {description} ({task_id})")
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
            if all(t.status == 'completed' for t in self.tasks.values()):
                logger.info("Mission Complete.")
            return

        for task in executable:
            await self.execute_task(task)

    async def execute_task(self, task: Task):
        logger.info(f"Executing: {task.description}")
        task.status = 'running'

        # 1. Consult Neural Hub (The "Think before Act" Step)
        should_proceed = self._consult_neural_hub(task)
        if not should_proceed:
            logger.warning(f"Neural Hub aborted task: {task.description}")
            task.status = 'failed' # Or 'held'
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

        # Self-Check: "Am I confident in this task?"
        # For now, we simulate a check. In a real scenario, this would check Memory for contradictions.
        return True

    async def handle_mission_create(self, event: Event):
        logger.info(f"New Mission: {event.data.get('goal')}")
        # In the future: Parse goal with LLM to generate initial graph
        # For now, we create a sample graph manually in the TUI or here.

    async def handle_task_complete(self, event: Event):
        # We need a way to map events back to tasks.
        # For now, simplistic mapping or assumption.
        pass

    async def handle_task_fail(self, event: Event):
        logger.error("Task failed.")

mission_control = DynamicGraphEngine()
