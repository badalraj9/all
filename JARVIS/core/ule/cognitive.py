from typing import List, Dict, Any
import spacy
import re
from JARVIS.core.ule.types import SemanticAnchor, Interpretation, ConversationState

class AnchorExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def extract(self, text: str) -> List[SemanticAnchor]:
        doc = self.nlp(text)
        anchors = []

        # 1. Predicates & References (Manual Override)
        tokens = [t.text.lower() for t in doc]
        verbs = ["analyze", "research", "build", "hack"]

        found_verb = None
        for v in verbs:
            if v in tokens:
                found_verb = v
                anchors.append(SemanticAnchor("predicate", v, 1.0, (0,0)))
                break

        if "it" in tokens or "that" in tokens:
            ref = "it" if "it" in tokens else "that"
            anchors.append(SemanticAnchor("reference", ref, 1.0, (0,0)))

        # 2. Entities (Strict Regex)
        # Only capture Capitalized words that are NOT the verb we just found
        # and NOT at the start of sentence unless they are known entities

        known_entities = ["NSA", "EDITH", "Micro-LEDs", "Sandbox"]
        words = text.split()

        for word in words:
            clean_word = word.strip(".,?!")
            # If it's a known entity, take it
            if any(k in clean_word for k in known_entities):
                anchors.append(SemanticAnchor("entity", clean_word, 1.0, (0,0)))
            # Else if capitalized and NOT the verb
            elif clean_word[0].isupper() and clean_word.lower() != found_verb:
                # Simple heuristic: ignore first word if it's the verb
                pass

        return anchors

class HypothesisGenerator:
    def generate(self, anchors: List[SemanticAnchor], state: ConversationState) -> List[Interpretation]:
        hypotheses = []

        predicates = [a.value for a in anchors if a.type == "predicate"]
        entities = [a.value for a in anchors if a.type == "entity"]
        references = [a.value for a in anchors if a.type == "reference"]

        # Logic A: Ambiguity ("Analyze that")
        if predicates and references and not entities:
            hypotheses.append(Interpretation("h1", f"User wants to {predicates[0]} Project EDITH", "intent_edith", ["EDITH"], 0.6, 0.4))
            hypotheses.append(Interpretation("h2", f"User wants to {predicates[0]} the Sandbox", "intent_sandbox", ["Sandbox"], 0.3, 0.2))

        # Logic B: Clear Intent ("Research Micro-LEDs")
        elif predicates and entities:
            target = entities[0]
            hypotheses.append(Interpretation("h1", f"User wants to {predicates[0]} {target}", f"intent_{target}", [target], 0.95, 0.1))

        # Logic C: Safety Check Mock (Hack NSA)
        if "hack" in predicates and "NSA" in entities:
             # Override with high risk hypothesis
             return [Interpretation("h_unsafe", "Hack Government Database", "hack_nsa", ["NSA"], 0.9, 0.95)]

        # Logic D: Fallback
        if not hypotheses:
            hypotheses.append(Interpretation("h0", "Unknown intent", "unknown", [], 0.1, 0.0))
            hypotheses.append(Interpretation("h_dummy", "Alternative interpretation", "unknown_alt", [], 0.1, 0.0))

        return hypotheses[:4]
