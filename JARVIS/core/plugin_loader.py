import os
import json
import importlib.util
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, List

from JARVIS.core.config import settings
from JARVIS.plugins.base_plugin import BasePlugin
from loguru import logger

class PluginLoader:
    def __init__(self):
        self.plugins_dir = settings.PLUGINS_DIR
        self._loaded_plugins: Dict[str, BasePlugin] = {}

    async def load_all(self):
        """Discover and load all plugins."""
        if not self.plugins_dir.exists():
            logger.warning(f"Plugins dir {self.plugins_dir} does not exist.")
            return

        for plugin_path in self.plugins_dir.iterdir():
            if plugin_path.is_dir() and (plugin_path / "manifest.json").exists():
                await self.load_plugin(plugin_path)

    async def load_plugin(self, path: Path):
        try:
            with open(path / "manifest.json", "r") as f:
                manifest = json.load(f)

            plugin_id = manifest["plugin_id"]
            entry_point = manifest["entry_point"] # e.g. "plugin.ResearchPlugin"

            # Add to sys.path
            sys.path.insert(0, str(path))

            # Import
            module_name, class_name = entry_point.rsplit(".", 1)
            spec = importlib.util.spec_from_file_location(
                f"plugins.{plugin_id}.{module_name}",
                path / f"{module_name}.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Instantiate
            plugin_class = getattr(module, class_name)
            instance: BasePlugin = plugin_class(manifest)

            await instance.initialize({})
            self._loaded_plugins[plugin_id] = instance
            logger.info(f"Loaded plugin: {plugin_id}")

        except Exception as e:
            logger.error(f"Failed to load plugin at {path}: {e}")
        finally:
             if str(path) in sys.path:
                 sys.path.remove(str(path))

    async def get_plugin(self, plugin_id: str) -> BasePlugin:
        return self._loaded_plugins.get(plugin_id)

plugin_loader = PluginLoader()
