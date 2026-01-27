import asyncio
import pyperclip
from textual import work
from loguru import logger
from JARVIS.core.event_bus import event_bus

class WatchDog:
    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.last_clipboard = ""
        self.active = False

    async def start(self):
        self.active = True
        logger.info("[WatchDog] Passive Monitoring Active (Clipboard).")
        while self.active:
            try:
                # Run clipboard check in thread executor to avoid blocking async loop
                content = await asyncio.to_thread(pyperclip.paste)

                if content != self.last_clipboard:
                    self.last_clipboard = content
                    # Passive filter: Only react if specific triggers found
                    # In real JARVIS, this would be smarter
                    triggers = ["jarvis", "analyze", "debug", "error", "exception"]
                    if any(t in content.lower() for t in triggers):
                        logger.info(f"[WatchDog] Trigger detected in clipboard!")
                        await event_bus.emit(
                            "watch.clipboard",
                            {"content": content},
                            source="watchdog"
                        )
            except Exception as e:
                logger.debug(f"WatchDog Error: {e}")

            await asyncio.sleep(self.interval)

    def stop(self):
        self.active = False

watch_dog = WatchDog()
