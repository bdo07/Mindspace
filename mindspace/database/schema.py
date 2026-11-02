"""Database schema initialization and seed data."""

import sqlite3
from datetime import datetime, date, timedelta

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    color TEXT NOT NULL DEFAULT '#8B79D9',
    icon TEXT NOT NULL DEFAULT 'folder',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT DEFAULT '',
    category_id INTEGER,
    is_pinned INTEGER NOT NULL DEFAULT 0,
    is_favorite INTEGER NOT NULL DEFAULT 0,
    is_archived INTEGER NOT NULL DEFAULT 0,
    is_quick INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    is_completed INTEGER NOT NULL DEFAULT 0,
    due_date TEXT,
    priority TEXT NOT NULL DEFAULT 'normal',
    category_id INTEGER,
    completed_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_notes_archived ON notes(is_archived);
CREATE INDEX IF NOT EXISTS idx_notes_favorite ON notes(is_favorite);
CREATE INDEX IF NOT EXISTS idx_notes_pinned ON notes(is_pinned);
CREATE INDEX IF NOT EXISTS idx_notes_category ON notes(category_id);
CREATE INDEX IF NOT EXISTS idx_notes_quick ON notes(is_quick);
CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(is_completed);
CREATE INDEX IF NOT EXISTS idx_tasks_due ON tasks(due_date);
"""

DEFAULT_CATEGORIES = [
    ("Personal", "#6C5CE7", "user"),
    ("Work", "#0984E3", "briefcase"),
    ("Ideas", "#00B894", "lightbulb"),
    ("Learning", "#E17055", "book-open"),
]

WELCOME_NOTE_TITLE = "Welcome to MINDSPACE 👋"
WELCOME_NOTE_CONTENT = """# Welcome to MINDSPACE — Your Personal Space

MINDSPACE is designed to be your quiet, focused sanctuary for ideas, notes, tasks, and quick thoughts.

---

### ✨ Key Features
- **Minimalist Design**: Crafted with clean typography, generous whitespace, and zero visual clutter.
- **Markdown Support**: Format text effortlessly with headers, bold, italics, checklists, and code snippets.
- **Quick Thoughts**: Capture fleeting sparks of inspiration in seconds from the Quick Notes view.
- **Task Management**: Keep track of daily actions, due dates, and priorities.
- **Light & Dark Mode**: Seamlessly switch themes anytime in **Settings**.
- **Local & Private**: All data is stored in a clean local SQLite database on your device.

---

### ⌨️ Useful Keyboard Shortcuts
- `Ctrl` / `Cmd` + `N`: Create a new note
- `Ctrl` / `Cmd` + `F`: Quick search
- `Ctrl` / `Cmd` + `S`: Save note immediately (Auto-save is also active!)
- `Ctrl` / `Cmd` + `Q`: Quit MINDSPACE

---

### 💡 Markdown Quick Tips
1. Use `#` for large headings, `##` for section titles
2. Wrap text in `**bold**` or `*italic*`
3. Create checklists with `- [ ] To do item`
4. Organize your thoughts using custom categories in the sidebar.

Enjoy your focused personal space!
"""


def initialize_schema(conn: sqlite3.Connection) -> None:
    """Executes schema creation and seeds default data if tables are empty."""
    conn.executescript(SCHEMA_SQL)

    # Check if categories already exist
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM categories")
    cat_count = cursor.fetchone()[0]

    now = datetime.now().isoformat()

    if cat_count == 0:
        for name, color, icon in DEFAULT_CATEGORIES:
            cursor.execute(
                "INSERT INTO categories (name, color, icon, created_at) VALUES (?, ?, ?, ?)",
                (name, color, icon, now),
            )

    # Check if notes exist
    cursor.execute("SELECT COUNT(*) FROM notes")
    note_count = cursor.fetchone()[0]
    if note_count == 0:
        cursor.execute("SELECT id FROM categories WHERE name = 'Personal' LIMIT 1")
        personal_row = cursor.fetchone()
        personal_id = personal_row[0] if personal_row else None

        cursor.execute(
            """INSERT INTO notes (title, content, category_id, is_pinned, is_favorite, is_archived, is_quick, created_at, updated_at)
               VALUES (?, ?, ?, 1, 1, 0, 0, ?, ?)""",
            (WELCOME_NOTE_TITLE, WELCOME_NOTE_CONTENT, personal_id, now, now),
        )

    # Check if tasks exist
    cursor.execute("SELECT COUNT(*) FROM tasks")
    task_count = cursor.fetchone()[0]
    if task_count == 0:
        cursor.execute("SELECT id FROM categories WHERE name = 'Work' LIMIT 1")
        work_row = cursor.fetchone()
        work_id = work_row[0] if work_row else None

        today = date.today().isoformat()
        tomorrow = (date.today() + timedelta(days=1)).isoformat()

        starter_tasks = [
            ("Explore MINDSPACE features and keyboard shortcuts", "Try creating your first note or task", 0, today, "high", personal_id),
            ("Organize projects into categories", "Create custom categories with unique accent colors", 0, tomorrow, "normal", work_id),
            ("Install Mindspace theme preference", "Choose between Light and Dark mode in Settings", 1, today, "low", personal_id),
        ]
        for title, desc, is_comp, due, prio, cat_id in starter_tasks:
            cursor.execute(
                """INSERT INTO tasks (title, description, is_completed, due_date, priority, category_id, completed_at, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (title, desc, is_comp, due, prio, cat_id, now if is_comp else None, now, now),
            )

    # Check default settings
    cursor.execute("SELECT COUNT(*) FROM settings")
    settings_count = cursor.fetchone()[0]
    if settings_count == 0:
        default_settings = [
            ("theme", "light"),
            ("auto_save_delay_ms", "600"),
            ("default_view", "notes"),
            ("editor_font_size", "14"),
            ("editor_font_family", "Inter"),
            ("show_markdown_preview", "0"),
            ("window_width", "1180"),
            ("window_height", "760"),
        ]
        for k, v in default_settings:
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, v))

