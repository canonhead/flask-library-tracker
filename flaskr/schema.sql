-- TODO: Adapt to current project

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE book(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn INTEGER NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    publisher TEXT,
    publish_year NUMBER,
    book_lang TEXT,
    purchase_loc TEXT,
    purchase_date TEXT,
    book_loc TEXT NOT NULL,
    page_count INTEGER,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    owner_id INTEGER NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES user (id)
);