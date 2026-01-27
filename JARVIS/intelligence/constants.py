import re
from typing import Dict, List, Pattern
from dataclasses import dataclass

# =============================================================================
# NEURAL HUB CONSTANTS
# =============================================================================

DEFAULT_THRESHOLD = 0.75
MIN_THRESHOLD = 0.60
MAX_THRESHOLD = 0.90

DEFAULT_LEARNING_RATE = 0.05
DECAY_RATE = 0.01

MIN_WEIGHT = 0.01
MAX_WEIGHT = 1.0
BASE_WEIGHT = 0.5

# =============================================================================
# LINGUISTIC PATTERNS
# =============================================================================

@dataclass
class PatternDefinition:
    name: str
    pattern: str  # String pattern for Python regex
    base_weight: float
    compiled: Pattern = None

DECISION_PATTERNS_DATA = [
    # High confidence markers
    {"name": "decided", "pattern": r"\b(decided|decision)\b", "base_weight": 0.35},
    {"name": "lets_go_with", "pattern": r"\blet'?s\s+go\s+with\b", "base_weight": 0.32},
    {"name": "will_use", "pattern": r"\bwe('ll|\s+will)\s+use\b", "base_weight": 0.30},
    {"name": "final", "pattern": r"\bfinal(ly|ized)?\b", "base_weight": 0.28},

    # Medium confidence markers
    {"name": "settled_on", "pattern": r"\bsettled\s+on\b", "base_weight": 0.25},
    {"name": "going_with", "pattern": r"\bgoing\s+(with|forward)\b", "base_weight": 0.22},
    {"name": "agreed", "pattern": r"\bagreed\b", "base_weight": 0.20},

    # Weak markers (need structural support)
    {"name": "pick", "pattern": r"\bpick(ed|ing)?\b", "base_weight": 0.12},
    {"name": "choose", "pattern": r"\bchoose|chose\b", "base_weight": 0.12},
]

# Compile patterns
DECISION_PATTERNS: List[PatternDefinition] = []
for p in DECISION_PATTERNS_DATA:
    DECISION_PATTERNS.append(PatternDefinition(
        name=p["name"],
        pattern=p["pattern"],
        base_weight=p["base_weight"],
        compiled=re.compile(p["pattern"], re.IGNORECASE)
    ))

# Quick pattern for early exit optimization
QUICK_DECISION_PATTERN = re.compile(
    r"\b(decid|let'?s\s+go|we('ll|\s+will)\s+use|final|settled|agreed|going\s+with)\b",
    re.IGNORECASE
)

# =============================================================================
# STRUCTURAL SIGNAL WEIGHTS
# =============================================================================

STRUCTURAL_WEIGHTS = {
    "thread_depth": {
        "multiplier": 0.03,
        "max": 0.15,
    },
    "maintainer_author": {
        "bonus": 0.12,
    },
    "acknowledgment_ratio": {
        "multiplier": 0.05,
        "max": 0.10,
    },
    "debate_burst": {
        "divisor": 3,
        "max": 0.08,
    },
}

# =============================================================================
# CONTEXTUAL SIGNAL WEIGHTS
# =============================================================================

CHAT_TYPE_WEIGHTS: Dict[str, float] = {
    "workshop": 0.15,
    "group_collab": 0.10,
    "direct": 0.05,
    "community": 0.03,
}

INTENT_ALIGNMENT_MAX = 0.20
