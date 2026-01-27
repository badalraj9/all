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
from JARVIS.memory.bridge import memory_bridge

class LogHandler:
    def __init__(self, widget: RichLog):
        self.widget = widget

    def write(self, message):
        self.widget.write(message)

    def flush(self):
        pass

class BrainMonitor(Static):
    """Displays Neural Hub status."""
    def compose(self) -> ComposeResult:
        yield Label("🧠 NEURAL HUB: ONLINE", id="brain-status")
        yield Label("Confidence: ---", id="brain-confidence")
        yield Label("Current Focus: Idle", id="brain-focus")

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

        logger.info("[bold green]JARVIS SYSTEM INITIALIZING...[/]")

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

    async def update_ui(self, event: Event):
        # Update Pending Tasks Count
        pending = len(mission_control.get_executable_tasks())
        self.query_one("#mission-pending", Label).update(f"Tasks Pending: {pending}")

    async def show_research(self, event: Event):
        data = event.data.get("findings", {})
        title = data.get("title", "Unknown")
        logger.info(f"[bold cyan]RESEARCH RESULT:[/bold cyan] {title}")
        logger.info(f"Summary: {data.get('summary')}")

    async def on_input_submitted(self, message: Input.Submitted):
        cmd = message.value
        message.input.value = ""

        logger.info(f"[bold yellow]USER:[/bold yellow] {cmd}")

        if cmd.lower().startswith("build"):
            goal = cmd[6:]
            logger.info(f"Initiating Mission: {goal}")

            # Manually triggering a flow for Demo purposes
            # In real system, LLM would parse this
            t1 = mission_control.add_task(f"Research {goal}", "research.start", {"query": goal})
            t2 = mission_control.add_task(f"Design {goal}", "design.draft", {}, depends_on=[t1])

            await mission_control.run_cycle()

if __name__ == "__main__":
    app = JarvisApp()
    app.run()
