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
    action: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    result: Any = None
    created_at: datetime = field(default_factory=datetime.now)
    dependencies: List[str] = field(default_factory=list)
    retry_count: int = 0

class DynamicGraphEngine:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.tasks: Dict[str, Task] = {}
        self.active_mission_id: Optional[str] = None

        self._setup_subscribers()
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
        return True

    async def handle_mission_create(self, event: Event):
        goal = event.data.get('goal')
        logger.info(f"New Mission: {goal}")
        self.graph.clear()
        self.tasks.clear()
        self.active_mission_id = str(uuid.uuid4())

        plan = self._generate_plan(goal)
        previous_task_id = None
        for step in plan:
            deps = [previous_task_id] if previous_task_id else []
            task_id = self.add_task(step['description'], step['action'], step['payload'], deps)
            previous_task_id = task_id

        await self.run_cycle()

    def _generate_plan(self, goal: str) -> List[Dict]:
        steps = []
        steps.append({"description": f"Research {goal}", "action": "research.start", "payload": {"query": goal}})
        if any(x in goal.lower() for x in ["design", "build", "create", "make"]):
             steps.append({"description": f"Draft Architecture for {goal}", "action": "design.draft", "payload": {}})
        if any(x in goal.lower() for x in ["glass", "screen", "visual", "edith"]):
             steps.append({"description": "Analyze Visual Context", "action": "vision.analyze", "payload": {"target": "screen"}})
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
        # 1. Identify Failed Task
        task_id = event.data.get("task_id")
        reason = event.data.get("reason", "Unknown")

        failed_task = self.tasks.get(task_id)

        # If task_id not explicitly sent (e.g. from plugin generic error), try to find running
        if not failed_task:
             for task in self.tasks.values():
                if task.status == 'running':
                    failed_task = task
                    break

        if failed_task:
            failed_task.status = 'failed'
            logger.error(f"❌ TASK FAILED: {failed_task.description} | Reason: {reason}")

            # 2. TRIGGER RE-PLANNING (Self-Healing)
            await self._trigger_replan(failed_task, reason)

            self._persist_state()

    async def _trigger_replan(self, failed_task: Task, reason: str):
        """The 'Warhorse' Logic: Don't quit, find another way."""

        logger.info("🔄 INITIATING RE-PLAN...")

        # Heuristic Adaptation Logic
        if "research" in failed_task.action:
            if failed_task.retry_count < 1:
                # Strategy A: Retry
                logger.info(f"Strategy: Retry task {failed_task.description}")
                failed_task.status = 'pending'
                failed_task.retry_count += 1
                await self.run_cycle()
            else:
                # Strategy B: Alternative Method
                logger.info("Strategy: Pivoting to fallback method.")

                # Add a Fallback Task
                fallback_description = f"Fallback Research: {failed_task.payload.get('query')} (General Search)"
                fallback_id = self.add_task(
                    description=fallback_description,
                    action="research.start", # In real V2, this would be research.google vs research.arxiv
                    payload={"query": failed_task.payload.get("query"), "method": "general"},
                    depends_on=[] # Root level fallback
                )

                # Re-route dependencies of the failed task to the new fallback
                successors = list(self.graph.successors(failed_task.id))
                for succ in successors:
                    self.graph.remove_edge(failed_task.id, succ)
                    self.graph.add_edge(fallback_id, succ)
                    logger.info(f"Re-routed dependency for {self.tasks[succ].description}")

                # Execute the new plan
                await self.run_cycle()

    def _persist_state(self):
        # (Persistence logic omitted for brevity in this update, assumes previous implementation)
        pass

    async def handle_startup(self, event: Event):
        pass

mission_control = DynamicGraphEngine()
