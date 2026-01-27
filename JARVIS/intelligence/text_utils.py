import re
from typing import List, Set

def tokenize(text: str) -> List[str]:
    """Simple tokenizer for text analysis."""
    # Convert to lowercase, replace non-word/non-space with space
    clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
    # Split by whitespace and filter short tokens
    return [t for t in clean_text.split() if len(t) > 1]

def stem(word: str) -> str:
    """Simple stemmer (Porter-like, simplified)."""
    result = word.lower()
    suffixes = ['ing', 'ed', 'ly', 'tion', 'ness', 'ment', 'able', 'ible', 's']

    for suffix in suffixes:
        if result.endswith(suffix) and len(result) > len(suffix) + 2:
            result = result[:-len(suffix)]
            break

    return result

def jaccard_similarity(tokens1: List[str], tokens2: List[str]) -> float:
    """Jaccard similarity between two sets of tokens."""
    set1 = set(map(stem, tokens1))
    set2 = set(map(stem, tokens2))

    if not set1 or not set2:
        return 0.0

    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))

    return intersection / union if union > 0 else 0.0
