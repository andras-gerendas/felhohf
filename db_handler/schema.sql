CREATE TABLE IF NOT EXISTS
  images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_normal TEXT NOT NULL,
    image_proc TEXT,
    caption_user TEXT NOT NULL,
    caption_gen TEXT,
    processed INTEGER NOT NULL
  );