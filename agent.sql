CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE,
    email VARCHAR(50),
    name VARCHAR(50),
    created_at TIMESTAMP DEFAULT now(),
    last_seen_at TIMESTAMP
);

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL,
    title TEXT,
    context_summary TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT now(),

    CONSTRAINT fk_conversations_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE TYPE message_role AS ENUM (
    'system',
    'user',
    'assistant',
    'tool'
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    role message_role NOT NULL,
    content TEXT NOT NULL,
    tokens INT,
    model_name VARCHAR(30),
    created_at TIMESTAMP DEFAULT now(),

    CONSTRAINT fk_messages_conversation
        FOREIGN KEY (conversation_id)
        REFERENCES conversations(id)
        ON DELETE CASCADE
);

CREATE TYPE memory_type AS ENUM (
    'profile',
    'preference',
    'fact',
    'summary'
);

CREATE TABLE memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL,
    conversation_id UUID NULL,
    memory_type memory_type NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now(),

    CONSTRAINT fk_memories_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_memories_conversation
        FOREIGN KEY (conversation_id)
        REFERENCES conversations(id)
        ON DELETE CASCADE
);
