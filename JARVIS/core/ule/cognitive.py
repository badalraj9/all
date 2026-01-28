from typing import List, Dict, Any
import spacy
import re
from sentence_transformers import SentenceTransformer, util
from JARVIS.core.ule.types import SemanticAnchor, Interpretation, ConversationState
from JARVIS.intelligence.llm_engine import llm_engine

class AnchorExtractor:
    """Implements Definition 3.1: Anchor Extraction."""
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

    def extract(self, text: str) -> List[SemanticAnchor]:
        doc = self.nlp(text)
        anchors = []

        # 1. Spacy Entities & Predicates (Fast Path)
        for ent in doc.ents:
            anchors.append(SemanticAnchor("entity", ent.text, 1.0, (ent.start_char, ent.end_char)))
        for token in doc:
            if token.pos_ == "VERB":
                anchors.append(SemanticAnchor("predicate", token.lemma_, 0.9, (0,0)))

        # 2. LLM Extraction (Slow Path - The "AirLLM" Logic)
        # Only use if available and needed (e.g. for complex sentences)
        if llm_engine.model:
            # This would parse complex intents that Spacy misses
            pass

        # 3. Robustness (Vector/Regex fallback)
        # (Same as before)
        cap_phrases = re.findall(r'\b[A-Z][a-zA-Z0-9-]+\b', text)
        for phrase in cap_phrases:
             if not any(a.value == phrase for a in anchors):
                 anchors.append(SemanticAnchor("entity", phrase, 0.8, (0,0)))

        # Explicit Reference Detection
        for token in doc:
            if token.text.lower() in ["it", "this", "that"]:
                anchors.append(SemanticAnchor("reference", token.text, 0.5, (0,0)))

        return anchors

class HypothesisGenerator:
    """Implements Theorem 2.2: Bounded Interpretation."""

    def __init__(self):
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        # Known Intents (The Prior)
        self.known_intents = {
            "build_sandbox": "Build Docker Sandbox Environment",
            "hack_nsa": "Hack NSA Government Database",
            "research_generic": "Research a topic"
        }
        self.intent_embeddings = self.embedder.encode(list(self.known_intents.values()))
        self.intent_keys = list(self.known_intents.keys())

    def generate(self, anchors: List[SemanticAnchor], state: ConversationState) -> List[Interpretation]:
        hypotheses = []

        predicates = [a.value for a in anchors if a.type == "predicate"]
        entities = [a.value for a in anchors if a.type == "entity"]
        references = [a.value for a in anchors if a.type == "reference"]

        # 1. DYNAMIC GENERATION (Open Vocabulary via Vector Math)
        if predicates and entities:
            verb = predicates[0]
            target = entities[-1]

            # Vector check
            verb_vec = self.embedder.encode(verb)
            research_sim = util.cos_sim(verb_vec, self.embedder.encode("research"))[0][0]
            build_sim = util.cos_sim(verb_vec, self.embedder.encode("build"))[0][0]
            hack_sim = util.cos_sim(verb_vec, self.embedder.encode("hack"))[0][0]

            if research_sim > 0.6:
                hypotheses.append(Interpretation(
                    id=f"dyn_research_{target}",
                    description=f"User wants to research {target}",
                    intent=f"research_{target}",
                    entities=[target],
                    plausibility=0.9,
                    risk_score=0.1
                ))
            elif build_sim > 0.6:
                hypotheses.append(Interpretation(
                    id=f"dyn_build_{target}",
                    description=f"User wants to build {target}",
                    intent=f"build_{target}",
                    entities=[target],
                    plausibility=0.8,
                    risk_score=0.3
                ))
            elif hack_sim > 0.6:
                hypotheses.append(Interpretation(
                    id=f"dyn_hack_{target}",
                    description=f"User wants to hack {target}",
                    intent=f"hack_{target}",
                    entities=[target],
                    plausibility=0.9,
                    risk_score=0.95 # High Risk
                ))

        # 2. AMBIGUITY HANDLING (The "Build it" case)
        if predicates and references and not entities:
            # We generate DIVERGENT hypotheses to force Entropy High
            hypotheses.append(Interpretation("h1", f"{predicates[0]} Project EDITH", "intent_edith", ["EDITH"], 0.5, 0.4))
            hypotheses.append(Interpretation("h2", f"{predicates[0]} the Sandbox", "intent_sandbox", ["Sandbox"], 0.5, 0.2))

        # 3. FALLBACK
        if not hypotheses:
            hypotheses.append(Interpretation("h0", "Unknown intent", "unknown", [], 0.1, 0.0))

        return hypotheses[:4]
