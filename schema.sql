CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE UNIQUE INDEX username_unique
ON users(username);


CREATE TABLE subjects (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE (user_id, name)
);


CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    subject_id INTEGER NOT NULL,
    task TEXT NOT NULL,
    due_date DATE,
    is_done BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);


CREATE TABLE summaries (
    id INTEGER PRIMARY KEY,
    subject_id INTEGER NOT NULL,
    source_text TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);