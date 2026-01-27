import math
from typing import List, Set, Literal

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max."""
    return max(min_val, min(max_val, value))

def sigmoid(z: float, threshold: float, steepness: float = 10.0) -> float:
    """
    Sigmoid activation function
    σ(z) = 1 / (1 + e^(-k(z - θ)))
    """
    try:
        return 1.0 / (1.0 + math.exp(-steepness * (z - threshold)))
    except OverflowError:
        return 0.0 if z < threshold else 1.0

def exponential_decay(
    current_value: float,
    base_value: float,
    days_since_update: float,
    decay_rate: float = 0.01
) -> float:
    """
    Exponential decay function
    v(t) = v0 * e^(-λt) + base * (1 - e^(-λt))
    """
    factor = math.exp(-decay_rate * days_since_update)
    return current_value * factor + base_value * (1.0 - factor)

def hebbian_update(
    current_weight: float,
    signal_value: float,
    outcome: Literal['confirmed', 'rejected'],
    learning_rate: float = 0.05,
    min_weight: float = 0.01,
    max_weight: float = 1.0
) -> float:
    """
    Hebbian weight update
    Δw = η * signal * direction
    """
    direction = 1.0 if outcome == 'confirmed' else -1.0
    delta = learning_rate * signal_value * direction
    return clamp(current_weight + delta, min_weight, max_weight)

def beta_mean(alpha: float, beta: float) -> float:
    """
    Beta distribution mean (for confidence intervals)
    E[X] = α / (α + β)
    """
    return alpha / (alpha + beta)

def beta_variance(alpha: float, beta: float) -> float:
    """
    Beta distribution variance
    Var[X] = αβ / ((α+β)²(α+β+1))
    """
    total = alpha + beta
    return (alpha * beta) / (total * total * (total + 1))
