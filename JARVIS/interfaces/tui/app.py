from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, RichLog, Static, Label
from textual.containers import Container, Horizontal, Vertical
from textual import work
from rich.text import Text
import asyncio
from loguru import logger
import sys

# Import JARVIS Core
from JARVIS.core.event_bus import event_bus, Event, EventPriority
from JARVIS.core.mission_control import mission_control
from JARVIS.core.plugin_loader import plugin_loader
from JARVIS.core.ule.engine import ule_engine

class LogHandler:
    def __init__(self, widget: RichLog):
        self.widget = widget

    def write(self, message):
        self.widget.write(message)

    def flush(self):
        pass

class BrainMonitor(Static):
    """Displays ULE State."""
    def compose(self) -> ComposeResult:
        yield Label("🧠 ULE BRAIN: ONLINE", id="brain-status")
        yield Label("Trust: 0.50", id="brain-trust")
        yield Label("Ambiguity: ---", id="brain-ambiguity")
        yield Label("Move: IDLE", id="brain-move")

class MissionMonitor(Static):
    """Displays active mission status."""
    def compose(self) -> ComposeResult:
        yield Label("🛡️ MISSION CONTROL: READY", id="mission-status")
        yield Label("Tasks Pending: 0", id="mission-pending")

class JarvisApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }

    #main-container {
        height: 1fr;
        layout: horizontal;
    }

    #left-panel {
        width: 30%;
        height: 100%;
        border-right: solid green;
    }

    #right-panel {
        width: 70%;
        height: 100%;
    }

    #log-view {
        height: 1fr;
        border: solid green;
        background: $surface;
    }

    BrainMonitor, MissionMonitor {
        height: auto;
        border-bottom: solid green;
        padding: 1;
    }

    Input {
        dock: bottom;
        border: solid green;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Vertical(
                BrainMonitor(),
                MissionMonitor(),
                id="left-panel"
            ),
            Vertical(
                RichLog(id="log-view", highlight=True, markup=True),
                id="right-panel"
            ),
            id="main-container"
        )
        yield Input(placeholder="Enter command...", id="command-input")
        yield Footer()

    async def on_mount(self):
        # Redirect Logger to UI
        log_widget = self.query_one("#log-view", RichLog)
        logger.remove()
        logger.add(lambda msg: log_widget.write(msg), format="{time:HH:mm:ss} | {level} | {message}")

        logger.info("[bold green]JARVIS SYSTEM INITIALIZING (ULE KERNEL)...[/]")

        # Start Systems
        await self.start_jarvis()

    @work
    async def start_jarvis(self):
        # Load Plugins
        await plugin_loader.load_all()
        logger.info("Plugins Loaded.")

        # Subscribe to updates
        event_bus.subscribe("task.*", self.update_ui)
        event_bus.subscribe("research.complete", self.show_research)

        # Trigger Startup
        await event_bus.emit("system.startup", {}, source="tui")

    async def update_ui(self, event: Event):
        # Update Pending Tasks Count
        pending = len(mission_control.get_executable_tasks())
        self.query_one("#mission-pending", Label).update(f"Tasks Pending: {pending}")

    async def show_research(self, event: Event):
        data = event.data.get("findings", {})
        title = data.get("title", "Unknown")
        logger.info(f"[bold cyan]RESEARCH RESULT:[/bold cyan] {title}")

    async def on_input_submitted(self, message: Input.Submitted):
        cmd = message.value
        message.input.value = ""

        logger.info(f"[bold yellow]USER:[/bold yellow] {cmd}")

        # --- THE ULE BRAIN TRANSPLANT ---
        # Instead of parsing "Build X" manually, we send it to ULE

        response, meta = ule_engine.process_turn(cmd)

        # Update Brain Monitor
        self.query_one("#brain-trust", Label).update(f"Trust: {meta['state']['trust']:.2f}")
        self.query_one("#brain-move", Label).update(f"Move: {meta['move']}")
        self.query_one("#brain-ambiguity", Label).update(f"Rationale: {meta['rationale']}")

        logger.info(f"[bold blue]JARVIS:[/bold blue] {response}")

        # If Move was PROPOSE, trigger Mission Control
        if meta.get("action_payload") and meta["move"] == "PROPOSE":
            goal = meta["action_payload"]["goal"]
            logger.info(f"Initiating Mission from ULE: {goal}")
            await event_bus.emit("mission.create", {"goal": goal}, source="ule")

if __name__ == "__main__":
    app = JarvisApp()
    app.run()
