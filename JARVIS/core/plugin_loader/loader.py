import os
import json
import importlib.util
import sys
import asyncio
from typing import Dict, Any, List
from pathlib import Path

# Simplified logger
import logging
logger = logging.getLogger("plugin_loader")

class BasePlugin:
    def __init__(self, manifest: Dict):
        self.manifest = manifest
    async def initialize(self, context: Dict): pass
    async def cleanup(self): pass

class PluginLoader:
    """
    JARVIS Plugin Loader (Assimilated CAPSULE).
    Supports Manifests and Isolated Loading.
    """
    def __init__(self, plugins_dir: str = "JARVIS/plugins"):
        self.plugins_dir = Path(plugins_dir)
        self._loaded_plugins: Dict[str, BasePlugin] = {}
        self._available_plugins: Dict[str, Dict[str, Any]] = {}

    async def discover_plugins(self):
        """Scan plugins directory for manifests."""
        if not self.plugins_dir.exists():
            return

        for plugin_dir in self.plugins_dir.iterdir():
            if plugin_dir.is_dir():
                manifest_path = plugin_dir / "manifest.json"
                if manifest_path.exists():
                    try:
                        with open(manifest_path, "r") as f:
                            manifest = json.load(f)
                        manifest["_path"] = str(plugin_dir)
                        self._available_plugins[manifest["plugin_id"]] = manifest
                    except Exception as e:
                        logger.error(f"Error reading manifest in {plugin_dir.name}: {e}")

    async def load_plugin(self, plugin_id: str) -> bool:
        if plugin_id not in self._available_plugins:
            return False

        manifest = self._available_plugins[plugin_id]
        plugin_path = Path(manifest["_path"])

        # Assimilation: We skip the dependency installation for now to avoid side effects
        # during the assimilation phase, but we keep the structure.

        try:
            entry_point = manifest.get("entry_point", "plugin.Plugin")
            module_name, class_name = entry_point.rsplit(".", 1)

            sys.path.insert(0, str(plugin_path))

            spec = importlib.util.spec_from_file_location(
                f"plugins.{plugin_id}.{module_name}",
                plugin_path / f"{module_name}.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            plugin_class = getattr(module, class_name)
            plugin_instance = plugin_class(manifest)

            await plugin_instance.initialize(context={})
            self._loaded_plugins[plugin_id] = plugin_instance

            return True
        except Exception as e:
            logger.error(f"Failed to load {plugin_id}: {e}")
            return False
        finally:
            if str(plugin_path) in sys.path:
                sys.path.remove(str(plugin_path))

plugin_loader = PluginLoader()
