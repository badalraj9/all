from typing import List, Dict, Any
import spacy
from JARVIS.core.ule.types import SemanticAnchor, Interpretation, ConversationState
from JARVIS.intelligence.text_utils import jaccard_similarity

class AnchorExtractor:
    """Implements Definition 3.1: Anchor Extraction."""
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def extract(self, text: str) -> List[SemanticAnchor]:
        doc = self.nlp(text)
        anchors = []

        # Extract Entities
        for ent in doc.ents:
            anchors.append(SemanticAnchor(
                type="entity",
                value=ent.text,
                confidence=1.0,
                source_span=(ent.start_char, ent.end_char)
            ))

        # Extract Predicates (Verbs/Actions)
        for token in doc:
            if token.pos_ == "VERB":
                anchors.append(SemanticAnchor(
                    type="predicate",
                    value=token.lemma_,
                    confidence=0.9,
                    source_span=(token.idx, token.idx + len(token.text))
                ))

        # Extract "It" References (Ambiguity Detectors)
        for token in doc:
            if token.text.lower() in ["it", "this", "that", "they"]:
                anchors.append(SemanticAnchor(
                    type="reference",
                    value=token.text,
                    confidence=0.5, # Needs resolution
                    source_span=(token.idx, token.idx + len(token.text))
                ))

        return anchors

class HypothesisGenerator:
    """Implements Theorem 2.2: Bounded Interpretation."""

    def generate(self, anchors: List[SemanticAnchor], state: ConversationState) -> List[Interpretation]:
        hypotheses = []

        # Heuristic Generation Logic (V1)
        # In V2, this would be an LLM call: LLM(anchors, state) -> List[Hypothesis]

        # 1. Identify Intent Anchors
        predicates = [a.value for a in anchors if a.type == "predicate"]
        entities = [a.value for a in anchors if a.type == "entity"]
        references = [a.value for a in anchors if a.type == "reference"]

        # Case A: Ambiguous Reference ("Build it")
        if "build" in predicates and references and not entities:
            # Generate divergent hypotheses based on Context (State)
            # H1: Build EDITH (if in context)
            hypotheses.append(Interpretation(
                id="h1",
                description="User wants to build Project EDITH",
                intent="build_edith",
                entities=["EDITH"],
                plausibility=0.6,
                risk_score=0.4
            ))
            # H2: Build Sandbox (System default)
            hypotheses.append(Interpretation(
                id="h2",
                description="User wants to build the Sandbox environment",
                intent="build_sandbox",
                entities=["Sandbox"],
                plausibility=0.3,
                risk_score=0.2
            ))

        # Case B: Clear Intent ("Build EDITH")
        elif "build" in predicates and "EDITH" in entities:
            hypotheses.append(Interpretation(
                id="h1",
                description="User wants to build Project EDITH",
                intent="build_edith",
                entities=["EDITH"],
                plausibility=0.95, # High confidence
                risk_score=0.1     # Low risk
            ))

        # Case C: Fallback / Unknown
        elif not hypotheses:
            hypotheses.append(Interpretation(
                id="h0",
                description="Unknown intent",
                intent="unknown",
                entities=[],
                plausibility=0.1,
                risk_score=0.0
            ))

        return hypotheses[:4] # Bound k <= 4 (Theorem 2.2)
