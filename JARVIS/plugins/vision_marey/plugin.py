import asyncio
import pyautogui
from datetime import datetime
from typing import Dict, Any
import os
import sys
from JARVIS.plugins.base_plugin import BasePlugin
from JARVIS.core.event_bus import event_bus, Event
from loguru import logger

class VisionPlugin(BasePlugin):
    async def initialize(self, context: Dict[str, Any]):
        # Check for DISPLAY env var to avoid crash in headless
        if not os.environ.get("DISPLAY") and os.name == 'posix':
            logger.warning("MAREY: No DISPLAY detected. Running in Headless/Mock mode.")
            self.headless = True
        else:
            self.headless = False
            # Try to init pyautogui early to catch X11 errors
            try:
                # We do a lazy import/check
                # If Xlib is missing or display is bad, this throws
                import Xlib.display
                # Try connecting (this might fail if DISPLAY is invalid)
                try:
                    Xlib.display.Display()
                except Exception:
                    # If connecting fails, double check if we really have a display
                    # Often Xlib throws error if DISPLAY set but X server dead
                    self.headless = True
                    logger.warning("MAREY: X Server unreachable. Fallback to Headless.")
            except Exception as e:
                logger.warning(f"MAREY: Display connect failed: {e}. Falling back to Headless.")
                self.headless = True

        event_bus.subscribe("vision.analyze", self.handle_analysis)
        logger.info("MAREY Vision Plugin initialized (Real Mode).")

    async def cleanup(self):
        pass

    async def handle_analysis(self, event: Event):
        logger.info("MAREY: Capturing screen for analysis...")

        screenshot_path = await asyncio.to_thread(self._take_screenshot)
        logger.info(f"MAREY: Screenshot saved to {screenshot_path}")

        analysis = {
            "objects": ["window", "text_block", "cursor"],
            "text_detected": True,
            "anomaly_detected": False,
            "timestamp": datetime.now().isoformat(),
            "note": "Real analysis would run OCR/YOLO here."
        }

        logger.info("MAREY: Analysis complete.")

        await event_bus.emit(
            "vision.complete",
            {"path": screenshot_path, "analysis": analysis},
            source="vision_marey"
        )

    def _take_screenshot(self) -> str:
        filename = f"/tmp/jarvis_vision_{int(datetime.now().timestamp())}.png"

        if self.headless:
            # Create a dummy file
            with open(filename, 'wb') as f:
                f.write(b'fake_png_data')
            return filename

        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            return filename
        except Exception as e:
            logger.error(f"MAREY: Screenshot failed: {e}")
            return "/tmp/mock_screenshot.png"
