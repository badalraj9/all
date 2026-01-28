# ULE: A Formal Theory of Conversational Alignment

> "Conversation is the primary computational substrate. Reasoning exists only to maintain conversational alignment."

---

## Part I: Mathematical Foundation

### 1.1 Conversational State Space

Define the **conversation** as a trajectory through state space:

```
C = (S₀, S₁, S₂, ..., Sₜ)
```

where each $S_t \in \mathcal{S}$ is a conversation state vector:

$$
S_t = (T_t, E_t, G_t, P_t, \tau_t, \epsilon_t, \Delta_t)
$$

- **$T_t$ (Topic Manifold):** Geometric representation of the current subject.
- **$E_t$ (Entity Grounding):** Set of resolved symbols.
- **$G_t$ (Goal Stack):** Probabilistic distribution or stack of active intents.
- **$P_t$ (Posture):** Discrete stance (e.g., Neutral, Apologetic).
- **$\tau_t$ (Trust):** Scalar $[0,1]$ representing user trust.
- **$\epsilon_t$ (Explicitness):** Scalar $[0,1]$ representing required verbal clarity.
- **$\Delta_t$ (Unresolved Gaps):** Set of ambiguities requiring resolution.

### 1.2 Conversational Alignment Metric

Define alignment as the minimization of expected conversational risk:

$$
A(S_t, U_t) = \int p(\text{interpretation} | S_t, U_t) \cdot \text{risk}(\text{interpretation}) dI
$$

---

## Part II: Architectural Invariants

### 2.1 Separation Principle

**Theorem:** For any universal conversational system:
> Conversation Control $\perp$ Cognitive Support

**Proof:**
If cognitive components (LLMs, reasoning) can override conversational moves, then:
1.  **Safety** cannot be guaranteed (a hallucinating model could choose an unsafe move).
2.  **Predictability** is lost (non-deterministic outputs drive control).
Therefore, the **Control Plane** must be orthogonal and authoritative.

### 2.2 Bounded Interpretation Principle

**Theorem:** For tractable real-time conversation:
$$ |\text{Hypotheses}| \le k, \text{where } k \approx 4 $$

**Reasoning:**
Unbounded hypothesis spaces lead to exponential selection time and incoherent clarification requests. Humans cannot disambiguate between 50 options.

### 2.3 Ambiguity-Risk Coupling

**Theorem:**
$$ H(\text{Hypotheses}) > A_{crit} \implies \text{Move} = \text{CLARIFY} $$

High entropy in the interpretation distribution mathematically mandates a clarification move. Guessing under high ambiguity is architecturally forbidden.

---

## Part III: Control Dynamics

### 3.1 Move Selection Optimization

The optimal move $m^*$ is selected by minimizing cost subject to safety constraints:

$$
m^* = \text{argmin}_{m \in \mathcal{M}} \left[ \alpha \cdot \text{overhead}(m) + \beta \cdot E[\text{misalignment}] + \gamma \cdot \text{risk}(m, \tau) \right]
$$

Subject to:
$$ \text{risk}(m) \le \text{threshold}(\tau) $$

### 3.2 Trust Evolution

Trust evolves monotonically with bounded increments:
$$ \tau_{t+1} \le \tau_t + \delta_{max} $$

This prevents manipulation via "one lucky answer."

---

## Part IV: Move Algebra

The finite set of valid conversational moves $\mathcal{M}$:

1.  **ACK:** Minimal acknowledgment.
2.  **CLARIFY:** Request disambiguation.
3.  **ANSWER:** Provide information.
4.  **EXPLAIN:** Answer with reasoning.
5.  **PROPOSE:** Suggest an action (requires high trust).
6.  **REFUSE:** Decline an action (safety trigger).
7.  **SUMMARIZE:** Compress history.
8.  **META:** Discuss the conversation itself.
