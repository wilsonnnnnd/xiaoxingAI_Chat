-- 主表：对话记录
CREATE TABLE IF NOT EXISTS chat_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL,                   -- 'user' 或 'assistant'
    content TEXT NOT NULL,
    topic TEXT,
    tags TEXT,                            -- JSON 格式的标签数组
    context_version INTEGER DEFAULT 1,
    is_deleted INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_chat_created_at ON chat_log(created_at);
CREATE INDEX IF NOT EXISTS idx_chat_context ON chat_log(context_version);

-- 记忆表：关键词记忆记录
CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_log_id INTEGER NOT NULL,
    keyword TEXT NOT NULL,
    value TEXT NOT NULL,
    topic TEXT,
    tags TEXT,                            -- JSON 格式
    source TEXT,
    is_deleted INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_log_id) REFERENCES chat_log(id) ON DELETE CASCADE,
    UNIQUE(chat_log_id, keyword, value)
);

CREATE INDEX IF NOT EXISTS idx_memory_keyword ON memory(keyword);
CREATE INDEX IF NOT EXISTS idx_memory_created_at ON memory(created_at);

-- 情绪日志表：检测情绪
CREATE TABLE IF NOT EXISTS emotion_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_log_id INTEGER NOT NULL,
    emotion TEXT NOT NULL,
    confidence REAL,
    chart_data TEXT,                      -- JSON，如 {"happy":0.6,"angry":0.2}
    context TEXT,
    is_deleted INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_log_id) REFERENCES chat_log(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_emotion_emotion ON emotion_log(emotion);

-- 用户偏好表
CREATE TABLE IF NOT EXISTS preference (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_log_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    value TEXT NOT NULL,
    importance INTEGER DEFAULT 1,
    tags TEXT,
    is_deleted INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_log_id) REFERENCES chat_log(id) ON DELETE CASCADE,
    UNIQUE(chat_log_id, category, value)
);

-- 每日总结表
CREATE TABLE IF NOT EXISTS daily_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL UNIQUE,
    summary TEXT NOT NULL,
    emotion_chart TEXT,                   -- JSON，如 {"happy": 4, "sad": 1}
    wordcloud_keywords TEXT,              -- JSON数组，如 ["音乐", "散步"]
    tags TEXT,                            -- JSON数组，如 ["积极", "成长"]
    is_deleted INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
