DROP TABLE IF EXISTS tasks;

CREATE TABLE tasks (
  unique_id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_num INTEGER UNIQUE NOT NULL,
  title TEXT NOT NULL,
  details TEXT,
  importance TEXT DEFAULT 'low' CHECK (importance IN ('low', 'medium', 'high'))
)