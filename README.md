# MINDSPACE — Your Personal Space

A minimalist, modern personal productivity desktop application crafted with **Python 3**, **PySide6 (Qt6)**, and **SQLite**. Designed with a quiet, focused macOS aesthetic to help you think clearly, organize your ideas, manage tasks, and capture fleeting thoughts without friction.

---

## ✨ Features

- 📝 **Markdown Note Editor**: Full formatting toolbar, live markdown preview toggle, heading support, code snippets, checklists, blockquotes, and links.
- ⚡ **Quick Notes Scratchpad**: Rapid idea capture pad with one-click conversion to full structured notes.
- ✅ **Task Manager**: Organize daily actions, due dates (overdue, today, upcoming badges), priorities, and completion progress metrics.
- 📂 **Custom Categories**: Color-coded category tags with custom palettes and live note counts.
- ⭐ **Favorites & Pinning**: Pin crucial notes to the top of your workspace; mark favorites for instant access.
- 📦 **Archived Notes**: Archive completed projects with one-click restoration or permanent deletion.
- 🔍 **Live Search**: Instant local search across note titles, contents, and tags.
- 💾 **Debounced Auto-Save**: Never lose a thought—notes auto-save quietly in the background as you write.
- 🌓 **Light & Dark Themes**: Pixel-perfect warm light canvas and slate dark theme with persistent preference storage.
- 🛡️ **Offline & Private**: All data is stored in a clean local SQLite database with automated WAL-mode journaling and zero telemetry.
- 📦 **Backup & Restore**: Native SQLite backup export and restoration with schema integrity checks.

---

## 🎨 Design System

MINDSPACE follows a clean, minimalist design language inspired by modern macOS productivity tools:

| Element | Light Mode | Dark Mode |
|---|---|---|
| **Background** | `#F7F6F2` (Warm Canvas) | `#18181B` (Deep Slate) |
| **Surface** | `#FFFFFF` (Pure White) | `#212126` (Charcoal) |
| **Primary Text** | `#202020` | `#F3F3F5` |
| **Secondary Text** | `#858585` | `#9E9EA8` |
| **Accent Color** | `#8B79D9` (Mindspace Lavender) | `#9D8DE6` |
| **Borders** | `#EAE8E2` | `#2E2E38` |
| **Typography** | Inter, -apple-system, Segoe UI, sans-serif | Inter, -apple-system, Segoe UI, sans-serif |

---

## 🏗️ Architecture

```
Mindspace/
├── mindspace/
│   ├── __init__.py               # Package metadata and version info
│   ├── main.py                   # Main Qt application entry point
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py         # SQLite connection manager with WAL mode
│   │   ├── schema.py             # Schema initialization and default seed data
│   │   └── repository.py         # Parameterized DAO operations
│   ├── models/
│   │   ├── __init__.py
│   │   ├── note.py               # Note data model
│   │   ├── task.py               # Task data model
│   │   ├── category.py           # Category data model
│   │   └── settings.py           # Application settings model
│   ├── services/
│   │   ├── __init__.py
│   │   ├── note_service.py       # Note business logic
│   │   ├── task_service.py       # Task business logic
│   │   ├── category_service.py   # Category business logic
│   │   ├── settings_service.py   # Preferences persistence
│   │   └── backup_service.py     # SQLite backup & restoration
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py        # Central MainWindow controller
│   │   ├── components/
│   │   │   ├── sidebar.py        # Sidebar navigation & badges
│   │   │   ├── search_bar.py     # Search input with debounce
│   │   │   ├── note_card.py      # Interactive note card
│   │   │   ├── task_item.py      # Interactive task checklist item
│   │   │   ├── toolbar.py        # Markdown formatting toolbar
│   │   │   └── toast.py          # Notification toast overlay
│   │   ├── views/
│   │   │   ├── notes_view.py     # Notes grid with search & sort
│   │   │   ├── editor_view.py    # Full-featured markdown editor
│   │   │   ├── quick_notes_view.py # Frictionless scratchpad
│   │   │   ├── tasks_view.py     # Tasks board with progress
│   │   │   └── settings_view.py  # Preferences & database stats
│   │   ├── dialogs/
│   │   │   ├── confirm_dialog.py # Clean confirmation modal
│   │   │   ├── category_dialog.py# Color palette & category creator
│   │   │   ├── task_dialog.py    # Task editor with date picker
│   │   │   └── about_dialog.py   # About & keyboard shortcuts modal
│   │   ├── themes/
│   │   │   ├── light.qss         # Light theme stylesheet
│   │   │   ├── dark.qss          # Dark theme stylesheet
│   │   │   └── theme_manager.py  # Theme switcher service
│   │   └── assets/
│   │       └── icons.py          # Lucide-style vector SVG library
│   └── utils/
│       ├── debounce.py           # QTimer-based event debouncer
│       ├── markdown_utils.py     # Markdown-to-HTML converter
│       └── date_utils.py         # Human-friendly relative date formatting
├── tests/
│   ├── test_database.py          # Database schema & CRUD tests
│   ├── test_services.py          # Business logic tests
│   ├── test_backup.py            # Backup & restore tests
│   ├── test_ui_smoke.py          # PySide6 UI instantiation tests
│   └── test_e2e_flow.py          # End-to-end user workflow test
├── run.py                        # Root launcher script
├── requirements.txt              # Production dependencies
├── .gitignore                    # Git ignore specifications
└── README.md                     # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- Git

### Installation

#### macOS & Linux:

```bash
# 1. Clone repository or navigate to directory
cd Mindspace

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install required dependencies
pip install -r requirements.txt
```

#### Windows:

```powershell
# 1. Navigate to directory
cd Mindspace

# 2. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 💻 Running the Application

Launch MINDSPACE with the convenience runner:

```bash
python run.py
```

Or execute as a module:

```bash
python -m mindspace.main
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl` / `Cmd` + `N` | Create a new note and open editor |
| `Ctrl` / `Cmd` + `F` | Focus search bar in active view |
| `Ctrl` / `Cmd` + `S` | Force immediate note save |
| `Ctrl` / `Cmd` + `B` | Bold text in editor (`**bold**`) |
| `Ctrl` / `Cmd` + `I` | Italic text in editor (`*italic*`) |
| `Ctrl` / `Cmd` + `Enter` | Capture thought in Quick Notes |
| `Ctrl` / `Cmd` + `Q` | Quit MINDSPACE |

---

## 🧪 Running Tests

The application includes automated unit and integration test suites:

```bash
# Run all tests
python -m unittest discover -s tests -p "test_*.py" -v
```

All 13 tests cover:
- SQLite schema initialization, foreign keys, and WAL mode
- Note, task, category, and settings CRUD operations
- Quick note conversion workflow
- Due date calculation and status badges
- Backup export, validation, and full restoration cycle
- PySide6 UI views instantiation and navigation transitions
- End-to-end user workflow simulation

---

## 🛡️ Privacy & Data Persistence

MINDSPACE operates 100% locally and offline:
- User data is saved in SQLite at `~/.mindspace/mindspace.db` (with safe fallback to local `./data/mindspace.db`).
- WAL (Write-Ahead Logging) mode is enabled for maximum performance and crash-safety.
- You can backup your database anytime under **Settings → Data & Backup → Export Backup**.

---

## 📄 License

MINDSPACE is open source and available under the [MIT License](LICENSE).

