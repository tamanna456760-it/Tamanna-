-- ============================================================
-- BD-KING-R7 / TAMANNA AI
-- FULL POSTGRESQL DATABASE INITIALIZATION
-- ============================================================
-- Owner: HM INSAN ALI
--
-- Purpose:
--   Users
--   Authentication
--   Conversations
--   Messages
--   Usage metrics
--   AI memory
--   Message library
--   Vocabulary
--   Language system
--   Modules
--   Audit logs
--   Backups
--   System settings
--   API keys
--   Performance indexes
--
-- PostgreSQL
-- ============================================================


-- ============================================================
-- 01. EXTENSIONS
-- ============================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;


-- ============================================================
-- 02. USERS
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    email VARCHAR(255) UNIQUE NOT NULL,

    password_hash VARCHAR(255) NOT NULL,

    name VARCHAR(255) NOT NULL,

    created_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP,

    last_login TIMESTAMPTZ,

    is_active BOOLEAN
        DEFAULT TRUE,

    is_verified BOOLEAN
        DEFAULT FALSE
);


-- ============================================================
-- 03. USER SESSIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL
        REFERENCES users(id)
        ON DELETE CASCADE,

    session_token_hash VARCHAR(255) UNIQUE NOT NULL,

    ip_address INET,

    user_agent TEXT,

    created_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP,

    expires_at TIMESTAMPTZ NOT NULL,

    revoked_at TIMESTAMPTZ
);


CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id
    ON user_sessions(user_id);

CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at
    ON user_sessions(expires_at);


-- ============================================================
-- 04. CONVERSATIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID
        REFERENCES users(id)
        ON DELETE CASCADE,

    title VARCHAR(500),

    created_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP,

    is_archived BOOLEAN
        DEFAULT FALSE
);


CREATE INDEX IF NOT EXISTS idx_conversations_user_id
    ON conversations(user_id);

CREATE INDEX IF NOT EXISTS idx_conversations_updated_at
    ON conversations(updated_at);


-- ============================================================
-- 05. MESSAGES
-- ============================================================

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    conversation_id UUID NOT NULL
        REFERENCES conversations(id)
        ON DELETE CASCADE,

    role VARCHAR(20) NOT NULL
        CHECK (
            role IN (
                'user',
                'assistant',
                'system',
                'tool'
            )
        ),

    content TEXT NOT NULL,

    tokens INTEGER,

    model VARCHAR(100),

    metadata JSONB
        DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
    ON messages(conversation_id);

CREATE INDEX IF NOT EXISTS idx_messages_created_at
    ON messages(created_at);

CREATE INDEX IF NOT EXISTS idx_messages_role
    ON messages(role);

CREATE INDEX IF NOT EXISTS idx_messages_metadata
    ON messages USING GIN(metadata);


-- ============================================================
-- 06. USAGE METRICS
-- ============================================================

CREATE TABLE IF NOT EXISTS usage_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID
        REFERENCES users(id)
        ON DELETE SET NULL,

    conversation_id UUID
        REFERENCES conversations(id)
        ON DELETE SET NULL,

    input_tokens INTEGER DEFAULT 0,

    output_tokens INTEGER DEFAULT 0,

    total_tokens INTEGER DEFAULT 0,

    model VARCHAR(100),

    cost DECIMAL(12, 6)
        DEFAULT 0,

    request_type VARCHAR(100),

    created_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_usage_metrics_created_at
    ON usage_metrics(created_at);

CREATE INDEX IF NOT EXISTS idx_usage_metrics_user_id
    ON usage_metrics(user_id);

CREATE INDEX IF NOT EXISTS idx_usage_metrics_conversation_id
    ON usage_metrics(conversation_id);


-- ============================================================
-- 07. AI MEMORY
-- ============================================================

CREATE TABLE IF NOT EXISTS ai_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID
        REFERENCES users(id)
        ON DELETE CASCADE,

    memory_type VARCHAR(100) NOT NULL,

    memory_key VARCHAR(255),

    memory_value TEXT NOT NULL,

    importance INTEGER
        DEFAULT 1
        CHECK (importance BETWEEN 1 AND 10),

    source VARCHAR(100),

    metadata JSONB
        DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP,

    is_active BOOLEAN
        DEFAULT TRUE
);


CREATE INDEX IF NOT EXISTS idx_ai_memory_user_id
    ON ai_memory(user_id);

CREATE INDEX IF NOT EXISTS idx_ai_memory_type
    ON ai_memory(memory_type);

CREATE INDEX IF NOT EXISTS idx_ai_memory_key
    ON ai_memory(memory_key);

CREATE INDEX IF NOT EXISTS idx_ai_memory_metadata
    ON ai_memory USING GIN(metadata);


-- ============================================================
-- 08. MESSAGE LIBRARY
-- ============================================================

CREATE TABLE IF NOT EXISTS message_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    message TEXT NOT NULL,

    reply TEXT NOT NULL,

    category VARCHAR(100),

    keywords JSONB
        DEFAULT '[]'::jsonb,

    language VARCHAR(50),

    intent VARCHAR(150),

    confidence DECIMAL(5, 4),

    approved BOOLEAN
        DEFAULT FALSE,

    usage_count INTEGER
        DEFAULT 0,

    created_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_message_library_category
    ON message_library(category);

CREATE INDEX IF NOT EXISTS idx_message_library_language
    ON message_library(language);

CREATE INDEX IF NOT EXISTS idx_message_library_intent
    ON message_library(intent);

CREATE INDEX IF NOT EXISTS idx_message_library_keywords
    ON message_library USING GIN(keywords);


-- ============================================================
-- 09. VOCABULARY
-- ============================================================

CREATE TABLE IF NOT EXISTS vocabulary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    language VARCHAR(100) NOT NULL,

    word VARCHAR(255) NOT NULL,

    normalized_word VARCHAR(255) NOT NULL,

    word_type VARCHAR(100),

    meaning TEXT,

    pronunciation VARCHAR(500),

    transliteration VARCHAR(500),

    examples JSONB
        DEFAULT '[]'::jsonb,

    metadata JSONB
        DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(language, normalized_word)
);


CREATE INDEX IF NOT EXISTS idx_vocabulary_language
    ON vocabulary(language);

CREATE INDEX IF NOT EXISTS idx_vocabulary_word
    ON vocabulary(word);

CREATE INDEX IF NOT EXISTS idx_vocabulary_normalized
    ON vocabulary(normalized_word);

CREATE INDEX IF NOT EXISTS idx_vocabulary_type
    ON vocabulary(word_type);


-- ============================================================
-- 10. LANGUAGE DEFINITIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS languages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    language_code VARCHAR(20) UNIQUE NOT NULL,

    language_name VARCHAR(100) NOT NULL,

    native_name VARCHAR(100),

    script_name VARCHAR(100),

    alphabet JSONB
        DEFAULT '[]'::jsonb,

    grammar JSONB
        DEFAULT '{}'::jsonb,

    number_system JSONB
        DEFAULT '{}'::jsonb,

    is_active BOOLEAN
        DEFAULT TRUE,

    created_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_languages_name
    ON languages(language_name);

CREATE INDEX IF NOT EXISTS idx_languages_active
    ON languages(is_active);


-- ============================================================
-- 11. LANGUAGE WORD MAPPINGS
-- ============================================================

CREATE TABLE IF NOT EXISTS language_word_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    language_id UUID
        REFERENCES languages(id)
        ON DELETE CASCADE,

    word_id UUID
        REFERENCES vocabulary(id)
        ON DELETE CASCADE,

    intent VARCHAR(150),

    action VARCHAR(150),

    semantic_group VARCHAR(150),

    synonyms JSONB
        DEFAULT '[]'::jsonb,

    antonyms JSONB
        DEFAULT '[]'::jsonb,

    created_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_language_word_language
    ON language_word_mappings(language_id);

CREATE INDEX IF NOT EXISTS idx_language_word_word
    ON language_word_mappings(word_id);

CREATE INDEX IF NOT EXISTS idx_language_word_intent
    ON language_word_mappings(intent);


-- ============================================================
-- 12. AI MODULES
-- ============================================================

CREATE TABLE IF NOT EXISTS ai_modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    module_name VARCHAR(255) UNIQUE NOT NULL,

    module_path TEXT,

    module_type VARCHAR(100),

    version VARCHAR(100),

    status VARCHAR(50)
        DEFAULT 'offline',

    description TEXT,

    capabilities JSONB
        DEFAULT '[]'::jsonb,

    configuration JSONB
        DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_ai_modules_status
    ON ai_modules(status);

CREATE INDEX IF NOT EXISTS idx_ai_modules_type
    ON ai_modules(module_type);


-- ============================================================
-- 13. MODULE EXECUTION LOG
-- ============================================================

CREATE TABLE IF NOT EXISTS module_execution_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    module_id UUID
        REFERENCES ai_modules(id)
        ON DELETE SET NULL,

    user_id UUID
        REFERENCES users(id)
        ON DELETE SET NULL,

    action VARCHAR(255),

    status VARCHAR(50),

    input_data JSONB
        DEFAULT '{}'::jsonb,

    output_data JSONB
        DEFAULT '{}'::jsonb,

    error_message TEXT,

    execution_time_ms INTEGER,

    created_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_module_logs_module
    ON module_execution_logs(module_id);

CREATE INDEX IF NOT EXISTS idx_module_logs_user
    ON module_execution_logs(user_id);

CREATE INDEX IF NOT EXISTS idx_module_logs_created
    ON module_execution_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_module_logs_status
    ON module_execution_logs(status);


-- ============================================================
-- 14. AUDIT LOG
-- ============================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID
        REFERENCES users(id)
        ON DELETE SET NULL,

    action VARCHAR(255) NOT NULL,

    resource_type VARCHAR(100),

    resource_id UUID,

    ip_address INET,

    user_agent TEXT,

    details JSONB
        DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_audit_logs_user
    ON audit_logs(user_id);

CREATE INDEX IF NOT EXISTS idx_audit_logs_action
    ON audit_logs(action);

CREATE INDEX IF NOT EXISTS idx_audit_logs_resource
    ON audit_logs(resource_type);

CREATE INDEX IF NOT EXISTS idx_audit_logs_created
    ON audit_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_audit_logs_details
    ON audit_logs USING GIN(details);


-- ============================================================
-- 15. SYSTEM SETTINGS
-- ============================================================

CREATE TABLE IF NOT EXISTS system_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    setting_key VARCHAR(255) UNIQUE NOT NULL,

    setting_value TEXT,

    value_type VARCHAR(50)
        DEFAULT 'string',

    description TEXT,

    is_secret BOOLEAN
        DEFAULT FALSE,

    created_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_system_settings_key
    ON system_settings(setting_key);


-- ============================================================
-- 16. API KEYS
-- ============================================================

CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID
        REFERENCES users(id)
        ON DELETE CASCADE,

    key_name VARCHAR(255) NOT NULL,

    key_hash VARCHAR(255) UNIQUE NOT NULL,

    last_used_at TIMESTAMPTZ,

    expires_at TIMESTAMPTZ,

    is_active BOOLEAN
        DEFAULT TRUE,

    created_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_api_keys_user
    ON api_keys(user_id);

CREATE INDEX IF NOT EXISTS idx_api_keys_active
    ON api_keys(is_active);


-- ============================================================
-- 17. BACKUP RECORDS
-- ============================================================

CREATE TABLE IF NOT EXISTS backup_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    backup_name VARCHAR(255) NOT NULL,

    backup_path TEXT,

    backup_type VARCHAR(100),

    size_bytes BIGINT,

    checksum VARCHAR(255),

    status VARCHAR(50)
        DEFAULT 'created',

    metadata JSONB
        DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_backup_records_created
    ON backup_records(created_at);

CREATE INDEX IF NOT EXISTS idx_backup_records_status
    ON backup_records(status);


-- ============================================================
-- 18. SYSTEM EVENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS system_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    event_type VARCHAR(100) NOT NULL,

    severity VARCHAR(50)
        DEFAULT 'info',

    source VARCHAR(255),

    message TEXT,

    details JSONB
        DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_system_events_type
    ON system_events(event_type);

CREATE INDEX IF NOT EXISTS idx_system_events_severity
    ON system_events(severity);

CREATE INDEX IF NOT EXISTS idx_system_events_created
    ON system_events(created_at);

CREATE INDEX IF NOT EXISTS idx_system_events_details
    ON system_events USING GIN(details);


-- ============================================================
-- 19. FILE / PROJECT INDEX
-- ============================================================

CREATE TABLE IF NOT EXISTS project_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    file_path TEXT UNIQUE NOT NULL,

    file_name VARCHAR(500),

    extension VARCHAR(50),

    file_size BIGINT,

    checksum VARCHAR(255),

    language VARCHAR(100),

    is_directory BOOLEAN
        DEFAULT FALSE,

    is_ignored BOOLEAN
        DEFAULT FALSE,

    metadata JSONB
        DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_project_files_extension
    ON project_files(extension);

CREATE INDEX IF NOT EXISTS idx_project_files_language
    ON project_files(language);

CREATE INDEX IF NOT EXISTS idx_project_files_checksum
    ON project_files(checksum);


-- ============================================================
-- 20. PROJECT CHANGE LOG
-- ============================================================

CREATE TABLE IF NOT EXISTS project_change_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    file_id UUID
        REFERENCES project_files(id)
        ON DELETE CASCADE,

    change_type VARCHAR(100) NOT NULL,

    old_checksum VARCHAR(255),

    new_checksum VARCHAR(255),

    description TEXT,

    changed_by VARCHAR(255),

    created_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_project_changes_file
    ON project_change_logs(file_id);

CREATE INDEX IF NOT EXISTS idx_project_changes_created
    ON project_change_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_project_changes_type
    ON project_change_logs(change_type);


-- ============================================================
-- 21. AI TASKS
-- ============================================================

CREATE TABLE IF NOT EXISTS ai_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID
        REFERENCES users(id)
        ON DELETE SET NULL,

    task_type VARCHAR(100) NOT NULL,

    task_name VARCHAR(255),

    status VARCHAR(50)
        DEFAULT 'pending',

    priority INTEGER
        DEFAULT 5,

    input_data JSONB
        DEFAULT '{}'::jsonb,

    output_data JSONB
        DEFAULT '{}'::jsonb,

    error_message TEXT,

    started_at TIMESTAMPTZ,

    completed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ
        DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_ai_tasks_user
    ON ai_tasks(user_id);

CREATE INDEX IF NOT EXISTS idx_ai_tasks_status
    ON ai_tasks(status);

CREATE INDEX IF NOT EXISTS idx_ai_tasks_priority
    ON ai_tasks(priority);

CREATE INDEX IF NOT EXISTS idx_ai_tasks_created
    ON ai_tasks(created_at);


-- ============================================================
-- 22. FUNCTION: UPDATED_AT
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


-- ============================================================
-- 23. UPDATED_AT TRIGGERS
-- ============================================================

DROP TRIGGER IF EXISTS update_users_updated_at
ON users;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


DROP TRIGGER IF EXISTS update_conversations_updated_at
ON conversations;

CREATE TRIGGER update_conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


DROP TRIGGER IF EXISTS update_ai_memory_updated_at
ON ai_memory;

CREATE TRIGGER update_ai_memory_updated_at
    BEFORE UPDATE ON ai_memory
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


DROP TRIGGER IF EXISTS update_message_library_updated_at
ON message_library;

CREATE TRIGGER update_message_library_updated_at
    BEFORE UPDATE ON message_library
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


DROP TRIGGER IF EXISTS update_vocabulary_updated_at
ON vocabulary;

CREATE TRIGGER update_vocabulary_updated_at
    BEFORE UPDATE ON vocabulary
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


DROP TRIGGER IF EXISTS update_languages_updated_at
ON languages;

CREATE TRIGGER update_languages_updated_at
    BEFORE UPDATE ON languages
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


DROP TRIGGER IF EXISTS update_ai_modules_updated_at
ON ai_modules;

CREATE TRIGGER update_ai_modules_updated_at
    BEFORE UPDATE ON ai_modules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


DROP TRIGGER IF EXISTS update_system_settings_updated_at
ON system_settings;

CREATE TRIGGER update_system_settings_updated_at
    BEFORE UPDATE ON system_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


DROP TRIGGER IF EXISTS update_project_files_updated_at
ON project_files;

CREATE TRIGGER update_project_files_updated_at
    BEFORE UPDATE ON project_files
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================================
-- 24. DEFAULT SYSTEM SETTINGS
-- ============================================================

INSERT INTO system_settings
    (setting_key, setting_value, value_type, description)
VALUES
    (
        'system.name',
        'Tamanna AI',
        'string',
        'Primary AI system name'
    ),
    (
        'system.project',
        'BD-KING-R7',
        'string',
        'Primary project name'
    ),
    (
        'system.owner',
        'HM INSAN ALI',
        'string',
        'Project owner'
    ),
    (
        'memory.enabled',
        'true',
        'boolean',
        'Enable AI memory'
    ),
    (
        'message_library.enabled',
        'true',
        'boolean',
        'Enable message library'
    ),
    (
        'vocabulary.enabled',
        'true',
        'boolean',
        'Enable vocabulary system'
    ),
    (
        'language_system.enabled',
        'true',
        'boolean',
        'Enable language system'
    ),
    (
        'audit.enabled',
        'true',
        'boolean',
        'Enable audit logging'
    ),
    (
        'project_index.enabled',
        'true',
        'boolean',
        'Enable project-wide file index'
    )
ON CONFLICT (setting_key)
DO NOTHING;


-- ============================================================
-- 25. DEFAULT LANGUAGES
-- ============================================================

INSERT INTO languages
    (
        language_code,
        language_name,
        native_name,
        script_name
    )
VALUES
    ('bn', 'Bengali', 'বাংলা', 'Bengali'),
    ('en', 'English', 'English', 'Latin'),
    ('hi', 'Hindi', 'हिन्दी', 'Devanagari'),
    ('ar', 'Arabic', 'العربية', 'Arabic')
ON CONFLICT (language_code)
DO NOTHING;


-- ============================================================
-- 26. SYSTEM STARTUP EVENT
-- ============================================================

INSERT INTO system_events
    (
        event_type,
        severity,
        source,
        message,
        details
    )
VALUES
    (
        'database.initialized',
        'info',
        'BD-KING-R7',
        'Tamanna AI database schema initialized',
        jsonb_build_object(
            'project', 'BD-KING-R7',
            'system', 'Tamanna AI',
            'owner', 'HM INSAN ALI'
        )
    );


-- ============================================================
-- 27. VERIFICATION
-- ============================================================

DO $$
DECLARE
    table_count INTEGER;
BEGIN

    SELECT COUNT(*)
    INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
      AND table_type = 'BASE TABLE';

    RAISE NOTICE
        'BD-KING-R7 / Tamanna AI database initialized. Tables: %',
        table_count;

END $$;


-- ============================================================
-- END
-- ============================================================