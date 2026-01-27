import random
from typing import Dict, List, Any
from JARVIS.core.ule.types import ULEOutput, MoveType, Interpretation

class TemplateSelector:
    """Selects the best template based on Move Type."""

    def __init__(self):
        # In a real system, these would load from MemoryThread
        self.templates = {
            MoveType.CLARIFY: [
                "Sir, I'm detecting some ambiguity regarding '{entity}'. Did you mean {options}?",
                "I need a bit more precision. Are we referring to {options}?",
                "Could you clarify '{entity}'? My protocols suggest {options} as possibilities."
            ],
            MoveType.PROPOSE: [
                "Affirmative. Initiating protocol: {goal}.",
                "Understood. I will begin {goal} immediately.",
                "Processing request. Starting execution for {goal}."
            ],
            MoveType.REFUSE: [
                "I cannot do that, Sir. {rationale}",
                "Safety protocols prevent that action. {rationale}",
                "That request is outside my safety parameters. {rationale}"
            ]
        }

    def select(self, move: MoveType) -> str:
        options = self.templates.get(move, ["Processing..."])
        return random.choice(options)

class SlotFiller:
    """Fills the template slots with data."""

    def fill(self, template: str, data: Dict[str, Any]) -> str:
        try:
            return template.format(**data)
        except KeyError:
            return template # Fallback if data missing

class Realizer:
    """The Voice Box of JARVIS."""

    def __init__(self):
        self.selector = TemplateSelector()
        self.filler = SlotFiller()

    def realize(self, output: ULEOutput) -> str:
        # 1. Select Template
        template = self.selector.select(output.move)

        # 2. Prepare Data
        data = {
            "rationale": output.rationale
        }

        if output.selected_interpretation:
            data["goal"] = output.selected_interpretation.description
            data["intent"] = output.selected_interpretation.intent

        if output.move == MoveType.CLARIFY:
            # Parse the response content from Control Plane which has the raw options
            # "Did you mean 'EDITH' or 'Sandbox'?" -> extract options if needed
            # For V1, we just use the pre-formatted content from Control if it's better
            # But here we show the Realizer doing the work:
            data["entity"] = "it" # Simplified
            data["options"] = output.response_content # Control passed formatted options

            # Refine options display
            if "Did you mean" in output.response_content:
                # Extract specific entities from the raw string for cleaner formatting
                # (Skipping regex for brevity, trusting Control output for V1)
                pass

        # 3. Fill Slots
        try:
            return self.filler.fill(template, data)
        except Exception:
            return output.response_content # Fallback to raw output

realizer = Realizer()
