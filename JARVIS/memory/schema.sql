-- JARVIS Memory Schema (Unified)

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =============================================================================
-- LAYER 1: THE FACT LOG (Immutable Reality)
-- =============================================================================
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace TEXT NOT NULL DEFAULT 'user',
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actor TEXT NOT NULL, -- 'USER', 'JARVIS', 'ORE', 'SYSTEM'
    action TEXT NOT NULL, -- 'OBSERVE', 'INFER', 'DECIDE', 'ACT'
    object_id UUID NOT NULL, -- Logical reference to an entity
    payload JSONB NOT NULL DEFAULT '{}', -- The raw content/delta
    antecedents UUID[] DEFAULT '{}', -- Causal parents (Event IDs)
    truth_vector JSONB NOT NULL DEFAULT '{}' -- {confidence, authority, freshness, corroboration}
);

CREATE INDEX IF NOT EXISTS idx_events_object_id ON events(object_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);

-- =============================================================================
-- LAYER 2: THE CONSENSUS STATE (Fast Recall)
-- =============================================================================
CREATE TABLE IF NOT EXISTS entity_state (
    entity_id UUID PRIMARY KEY,
    namespace TEXT NOT NULL,
    current_value JSONB NOT NULL,
    truth_vector JSONB NOT NULL,
    version INTEGER NOT NULL DEFAULT 0,
    last_event_id UUID NOT NULL REFERENCES events(id),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'archived')),
    access_count INTEGER DEFAULT 0
);

-- =============================================================================
-- LAYER 3: THE COGNITIVE GALAXY (Divergent Beliefs)
-- =============================================================================
-- Allows different agents (dimensions) to hold different views on the same entity
CREATE TABLE IF NOT EXISTS beliefs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID NOT NULL, -- Link to the conceptual entity
    agent_id TEXT NOT NULL, -- Who holds this belief (e.g., 'researcher_agent', 'security_agent')
    content JSONB NOT NULL, -- What they believe
    confidence FLOAT NOT NULL DEFAULT 0.5,
    derived_from_event_id UUID REFERENCES events(id),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(entity_id, agent_id)
);

-- =============================================================================
-- LAYER 4: KNOWLEDGE GRAPH (Relations)
-- =============================================================================
CREATE TABLE IF NOT EXISTS relations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_entity_id UUID NOT NULL,
    target_entity_id UUID NOT NULL,
    relation_type TEXT NOT NULL, -- 'is_a', 'part_of', 'contradicts'
    confidence FLOAT NOT NULL DEFAULT 1.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',

    UNIQUE(source_entity_id, target_entity_id, relation_type)
);

CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source_entity_id);
CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target_entity_id);
