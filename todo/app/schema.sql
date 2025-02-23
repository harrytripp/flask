DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS completed;

CREATE TABLE tasks (
    unique_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_num INTEGER UNIQUE NOT NULL,
    title TEXT NOT NULL,
    details TEXT,
    importance TEXT DEFAULT 'low' CHECK (importance IN ('low', 'medium', 'high'))
);

CREATE TABLE completed (
    unique_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    details TEXT,
    importance TEXT DEFAULT 'low' CHECK (importance IN ('low', 'medium', 'high'))
);