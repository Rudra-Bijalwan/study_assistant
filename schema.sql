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
    FOREIGN KEY (user_id) references users(id),
    UNIQUE (user_id, name)
);


CREATE TABLE uploads (
    id INTEGER PRIMARY KEY,
    subject_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    file_path TEXT UNIQUE NOT NULL,
    file_type TEXT NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) references subjects(id),
    UNIQUE (subject_id, title)
);


CREATE TABLE summaries (
    id INTEGER PRIMARY KEY,
    upload_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (upload_id) references uploads(id)
);


CREATE TABLE flashcards (
    id INTEGER PRIMARY KEY,
    upload_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (upload_id) references uploads(id)
);


CREATE TABLE flashcard_review (
    id INTEGER PRIMARY KEY,
    flashcard_id INTEGER NOT NULL,
    reviewed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (flashcard_id) references flashcards(id)
);
