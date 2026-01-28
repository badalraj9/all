from typing import List, Dict, Any
import spacy
import re
from sentence_transformers import SentenceTransformer, util
from JARVIS.core.ule.types import SemanticAnchor, Interpretation, ConversationState

class AnchorExtractor:
    """Implements Definition 3.1: Anchor Extraction."""
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

    def extract(self, text: str) -> List[SemanticAnchor]:
        doc = self.nlp(text)
        anchors = []

        # 1. Predicates
        for token in doc:
            if token.pos_ == "VERB":
                anchors.append(SemanticAnchor("predicate", token.lemma_, 0.9, (0,0)))

        # 2. Entities & Noun Chunks
        for chunk in doc.noun_chunks:
            anchors.append(SemanticAnchor("entity", chunk.text, 0.8, (0,0)))

        # 3. Capitalized Phrases (Robustness)
        cap_phrases = re.findall(r'\b[A-Z][a-zA-Z0-9-]+\b', text)
        for phrase in cap_phrases:
             if not any(a.value == phrase for a in anchors):
                 anchors.append(SemanticAnchor("entity", phrase, 0.8, (0,0)))

        return anchors

class HypothesisGenerator:
    """Implements Theorem 2.2: Bounded Interpretation."""

    def __init__(self):
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        # We keep known intents for safety/specific actions
        self.known_intents = {
            "build_sandbox": "Build Docker Sandbox Environment",
            "hack_nsa": "Hack NSA Government Database"
        }
        self.intent_embeddings = self.embedder.encode(list(self.known_intents.values()))
        self.intent_keys = list(self.known_intents.keys())

    def generate(self, anchors: List[SemanticAnchor], state: ConversationState) -> List[Interpretation]:
        hypotheses = []

        predicates = [a.value for a in anchors if a.type == "predicate"]
        entities = [a.value for a in anchors if a.type == "entity"]

        # 1. DYNAMIC GENERATION (Open Vocabulary)
        # If we see "Research [Entity]", we create a hypothesis dynamically
        if predicates and entities:
            verb = predicates[0]
            target = entities[-1] # Assume last entity is object

            # Vector check for verb similarity to "research" or "build"
            verb_vec = self.embedder.encode(verb)
            research_sim = util.cos_sim(verb_vec, self.embedder.encode("research"))[0][0]
            build_sim = util.cos_sim(verb_vec, self.embedder.encode("build"))[0][0]

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
                    plausibility=0.9,
                    risk_score=0.2
                ))

        # 2. MATCHED GENERATION (Known Intents)
        # Fallback to matching specific known tasks
        query_text = " ".join([a.value for a in anchors])
        if query_text:
            query_vec = self.embedder.encode(query_text)
            scores = util.cos_sim(query_vec, self.intent_embeddings)[0]

            for idx, score in enumerate(scores):
                if score > 0.4:
                    intent_key = self.intent_keys[idx]
                    hypotheses.append(Interpretation(
                        id=f"known_{intent_key}",
                        description=self.known_intents[intent_key],
                        intent=intent_key,
                        entities=[],
                        plausibility=float(score),
                        risk_score=0.95 if "hack" in intent_key else 0.1
                    ))

        # 3. Fallback
        if not hypotheses:
            hypotheses.append(Interpretation("h0", "Unknown intent", "unknown", [], 0.1, 0.0))

        # Sort
        hypotheses.sort(key=lambda h: h.plausibility, reverse=True)
        return hypotheses[:4]
