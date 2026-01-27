from abc import ABC, abstractmethod
from typing import Dict, Any
from JARVIS.core.event_bus import event_bus

class BasePlugin(ABC):
    def __init__(self, manifest: Dict[str, Any]):
        self.manifest = manifest
        self.plugin_id = manifest.get("plugin_id")

    @abstractmethod
    async def initialize(self, context: Dict[str, Any]):
        """Called when the plugin is loaded."""
        pass

    @abstractmethod
    async def cleanup(self):
        """Called when the plugin is unloaded."""
        pass
