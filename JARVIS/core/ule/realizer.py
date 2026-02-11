from typing import Dict, List, Any
import random
from JARVIS.intelligence.llm_engine.core import llm_engine

class ULERealizer:
    """
    Universal Language Engine (ULE) - Hybrid Realizer.
    Switches between Deterministic Templates (Fast/Safe) and LLM (Fluid/Cognitive).
    """

    def __init__(self):
        self.templates = {
            "thesis_abstract": [
                "ABSTRACT: {title}\n\nThis study investigates {topic} as implemented in {target}. Our analysis identified {count} core components focused on {focus}. Literature review confirms the viability of {key_finding}.",
            ],
            "status_report": [
                "STATUS: {status}. Active Project: {project}. Current Focus: {focus}.",
            ]
        }
        llm_engine.load_model()

    def generate_report(self, context_nodes: List[Dict], intent: str = "General Report", intent_type: str = "QUERY", use_llm: bool = True) -> str:
        """
        Intelligent Aggregation of Memory Nodes into a Report context.
        """
        # 1. Extract Signals
        data = {
            "title": "Automated Analysis",
            "topic": "Unknown Topic",
            "target": "Unknown Target",
            "count": 0,
            "focus": "General Logic",
            "key_finding": "Standard Patterns",
            "paper": "Unknown Paper"
        }

        # Flatten context for LLM
        flat_context = {}
        for i, node in enumerate(context_nodes):
            payload = node.get("payload", {})
            flat_context[f"Item_{i}"] = str(payload)

            # Heuristics for Template
            if "files" in payload:
                data["count"] = len(payload["files"])
            if "topic" in payload:
                data["topic"] = payload["topic"]
                data["title"] = f"Analysis of {payload['topic']}"
            if "MAREY" in str(node):
                data["target"] = "MAREY Repository"
            if "Adaptive" in str(node):
                data["focus"] = "Adaptive Processing"
            if "title" in payload:
                data["paper"] = payload["title"]
                data["key_finding"] = payload.get("summary", "published research")

        # 2. Decide: Template or LLM?
        if use_llm:
            return llm_engine.generate_response(flat_context, intent=intent, intent_type=intent_type)
        else:
            return self._apply_template("thesis_abstract", data)

    def _apply_template(self, intent, context):
        if intent not in self.templates: return "Unknown Intent"
        template = random.choice(self.templates[intent])
        try:
            return template.format(**context)
        except:
            return "Template Error"

ule_realizer = ULERealizer()
