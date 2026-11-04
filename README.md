# MINDSPACE — Your Personal Space

A minimalist, modern personal productivity desktop application crafted with **Python 3**, **PySide6 (Qt6)**, and **SQLite**. Designed with a quiet, focused macOS aesthetic to help you think clearly, organize your ideas, manage tasks, and capture fleeting thoughts without friction.

---

## ✨ Features

- 📝 **Markdown Note Editor**: Full formatting toolbar, live markdown preview toggle, heading support, code snippets, checklists, blockquotes, and links.
- ⚡ **Quick Notes Scratchpad**: Rapid idea capture pad with one-click conversion to full structured notes.
- ✅ **Task Manager**: Organize daily actions, modal task dialog, due dates (overdue, today, upcoming badges), priorities, and completion progress metrics.
- 📂 **Custom Categories**: Color-coded category tags with custom palettes, live note counts, and contextual right-click edit/delete directly from the sidebar.
- ⭐ **Favorites & Pinning**: Pin crucial notes to the top of your workspace; mark favorites for instant access.
- 📦 **Archived Notes**: Archive completed projects with one-click restoration or permanent deletion.
- 🖱️ **Card Context Menus**: Right-click on any note card to pin, favorite, archive/restore, or delete in one click.
- 📐 **Responsive Architecture**: Smooth collapsible sidebar (expanded `220px`, collapsed `60px`), automatic collapse on compact screens (<860px), and dynamic 1-4 column card grid calculation.
- 🔍 **Live Search**: Instant local search across note titles, contents, and tags with debounced input.
- 💾 **Debounced Auto-Save**: Never lose a thought—notes auto-save quietly in the background as you write.
- 🌓 **Centralized Light & Dark Themes**: Pixel-perfect warm light canvas and slate dark theme with complete QSS widget coverage, instant switching, and persistent preference storage.
- 🛡️ **Offline & Private**: All data is stored in a clean local SQLite database with automated WAL-mode journaling and zero telemetry.
- 📦 **Backup & Restore**: Native SQLite backup export and restoration with schema integrity checks.

---

## 🎨 Design System & Brand Identity

MINDSPACE is built upon a refined, nature-inspired palette: **Primary Forest Green (`#15370D`)**, **Warm Amber (`#F1A344`)**, and **Soft Sky Blue (`#97D7FF`)**.

- **Forest Green (`#15370D`)**: Primary buttons, active navigation, selected states, and core branding.
- **Warm Amber (`#F1A344`)**: Highlights, subtle badges, progress indicators, and favorite stars.
- **Soft Sky Blue (`#97D7FF`)**: Secondary interactive emphasis, focus indicators, and dark mode interactive states.

| Element | Light Mode | Dark Mode |
|---|---|---|
| **Background** | `#F7F8F4` (Warm Canvas) | `#11170F` (Deep Forest) |
| **Sidebar** | `#F0F2EB` (Soft Celadon) | `#182116` (Foliage Charcoal) |
| **Cards / Surfaces** | `#FFFFFF` (Pure White) | `#202B1D` (Dark Olive Surface) |
| **Elevated Surfaces**| `#FFFFFF` | `#293725` (Elevated Forest Surface) |
| **Primary Text** | `#20251E` | `#F2F5ED` |
| **Secondary Text** | `#777E73` | `#A7B29F` |
| **Primary Accent** | `#15370D` (Forest Green) | `#97D7FF` (Soft Sky Blue) |
| **Secondary Accent**| `#F1A344` (Warm Amber) | `#F1A344` (Warm Amber) |
| **Structural Green**| `#15370D` | `#6C9B59` (Sage Green Accent) |
| **Borders** | `#E4E8DF` | `#354331` |
| **Typography** | `.AppleSystemUIFont`, Segoe UI, Roboto, Inter | `.AppleSystemUIFont`, Segoe UI, Roboto, Inter |

---

## 🏗️ Architecture

```
Mindspace/
├── main.py                       # Root launcher script
├── run.py                        # Alternative launcher script
├── requirements.txt              # Production dependencies
├── LICENSE                       # MIT License
├── README.md                     # Project documentation
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
│   │   │   ├── sidebar.py        # Responsive collapsible sidebar
│   │   │   ├── search_bar.py     # Search input with debounce & cached actions
│   │   │   ├── note_card.py      # Interactive note card with context menu
│   │   │   ├── task_item.py      # Interactive task checklist item
│   │   │   ├── toolbar.py        # Markdown formatting toolbar
│   │   │   └── toast.py          # Notification toast overlay
│   │   ├── views/
│   │   │   ├── notes_view.py     # Dynamic multi-column grid with search & sort
│   │   │   ├── editor_view.py    # Markdown editor with write/split/preview
│   │   │   ├── quick_notes_view.py # Frictionless scratchpad
│   │   │   ├── tasks_view.py     # Tasks board with tabs & progress
│   │   │   └── settings_view.py  # Preferences & database stats
│   │   ├── dialogs/
│   │   │   ├── confirm_dialog.py # Clean confirmation modal
│   │   │   ├── category_dialog.py# Color palette & category creator/editor
│   │   │   ├── task_dialog.py    # Task editor with date picker & validation
│   │   │   └── about_dialog.py   # About & keyboard shortcuts modal
│   │   ├── themes/
│   │   │   ├── light.qss         # Light theme stylesheet
│   │   │   ├── dark.qss          # Dark theme stylesheet
│   │   │   └── theme_manager.py  # Centralized theme manager
│   │   └── assets/
│   │       └── icons.py          # Lucide-style vector SVG library
│   └── utils/
│       ├── debounce.py           # QTimer-based event debouncer
│       ├── markdown_utils.py     # Markdown-to-HTML converter
│       └── date_utils.py         # Human-friendly relative date formatting
└── tests/
    ├── test_database.py          # Database schema & CRUD tests
    ├── test_services.py          # Business logic tests
    ├── test_backup.py            # Backup & restore tests
    ├── test_ui_smoke.py          # PySide6 UI instantiation tests
    ├── test_dark_mode_and_theme.py# Dark mode & theme coverage tests
    ├── test_audit_and_responsive.py# Full audit and responsive window tests
    └── test_e2e_flow.py          # End-to-end user workflow test
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

Launch MINDSPACE with any of the following standard runners:

```bash
# Option 1: Main entry
python main.py

# Option 2: Run script
python run.py

# Option 3: Module execution
python -m mindspace.main
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl` / `Cmd` + `N` | Smart New (creates Note or Task based on active view) |
| `Ctrl` / `Cmd` + `F` | Focus search bar in active view |
| `Ctrl` / `Cmd` + `S` | Force immediate note save |
| `Ctrl` / `Cmd` + `B` | Bold text in editor (`**bold**`) |
| `Ctrl` / `Cmd` + `I` | Italic text in editor (`*italic*`) |
| `Ctrl` / `Cmd` + `Enter` | Capture thought in Quick Notes |
| `Ctrl` / `Cmd` + `Q` | Quit MINDSPACE |

---

## 🧪 Running Tests

The application includes 20 automated unit, integration, responsive, and theme test suites:

```bash
# Run all tests
python -m unittest discover -s tests -p "test_*.py" -v
```

All 20 tests cover:
- SQLite schema initialization, foreign keys, and WAL mode
- Note, task, category, and settings CRUD operations
- Quick note conversion workflow
- Due date calculation and status badges
- Backup export, validation, and full restoration cycle
- Responsive window resize tests (1440x900, 1280x800, 1024x768, 800x600)
- Add Task 8-step workflow validation
- Dark Mode full widget styling, token validation, and live switching
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
