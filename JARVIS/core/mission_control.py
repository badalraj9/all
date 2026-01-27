import networkx as nx
import asyncio
from typing import Dict, List, Any, Optional, Literal
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import json
import re

from JARVIS.core.event_bus import event_bus, Event, EventPriority
from JARVIS.intelligence.neural_hub import neural_hub, ProcessingContext, NeuralState
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
        self._persist_state()
        return task_id

    def get_executable_tasks(self) -> List[Task]:
        executable = []
        for node in self.graph.nodes():
            task = self.tasks[node]
            if task.status == 'pending':
                predecessors = list(self.graph.predecessors(node))
                if all(self.tasks[p].status == 'completed' for p in predecessors):
                    executable.append(task)
        return executable

    async def run_cycle(self):
        executable = self.get_executable_tasks()

        if not executable:
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

        should_proceed = self._consult_neural_hub(task)
        if not should_proceed:
            logger.warning(f"Neural Hub aborted task: {task.description}")
            task.status = 'failed'
            self._persist_state()
            return

        await event_bus.emit(task.action, task.payload, source="mission_control")

    def _consult_neural_hub(self, task: Task) -> bool:
        # Mock Context
        return True

    async def handle_mission_create(self, event: Event):
        goal = event.data.get('goal')
        logger.info(f"New Mission: {goal}")

        self.graph.clear()
        self.tasks.clear()
        self.active_mission_id = str(uuid.uuid4())

        # HEURISTIC PLANNER (Simulating LLM Reasoning)
        # Instead of hardcoded "Build EDITH", we generate based on keywords

        plan = self._generate_plan(goal)

        previous_task_id = None
        for step in plan:
            # If it's the first step, no dependencies
            deps = [previous_task_id] if previous_task_id else []

            task_id = self.add_task(
                description=step['description'],
                action=step['action'],
                payload=step['payload'],
                depends_on=deps
            )
            previous_task_id = task_id # Chain them linearly for safety in this version

        await self.run_cycle()

    def _generate_plan(self, goal: str) -> List[Dict]:
        """
        A heuristic planner that generates tasks based on the goal string.
        In V2, this is replaced by an LLM call.
        """
        steps = []

        # Step 1: Always Research
        steps.append({
            "description": f"Research {goal}",
            "action": "research.start",
            "payload": {"query": goal}
        })

        # Step 2: If "design" or "build" or "create" -> Add Design Phase
        if any(x in goal.lower() for x in ["design", "build", "create", "make"]):
             steps.append({
                "description": f"Draft Architecture for {goal}",
                "action": "design.draft", # Mock action
                "payload": {}
            })

        # Step 3: If "visual" or "glasses" or "screen" -> Add Vision Check
        if any(x in goal.lower() for x in ["glass", "screen", "visual", "edith"]):
             steps.append({
                "description": "Analyze Visual Context",
                "action": "vision.analyze",
                "payload": {"target": "screen"}
            })

        return steps

    async def handle_task_complete(self, event: Event):
        completed_task = None
        for task in self.tasks.values():
            if task.status == 'running':
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

    def _persist_state(self):
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
        try:
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
        except Exception:
            pass # Silent fail if DB not ready in dev

    async def handle_startup(self, event: Event):
        # ... (Same as before)
        pass

mission_control = DynamicGraphEngine()
