"""Database connection manager for MINDSPACE."""


import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional


class DatabaseConnection:
    

    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = Path(db_path)
        elif os.environ.get("MINDSPACE_DB"):
            self.db_path = Path(os.environ["MINDSPACE_DB"])
        else:
            
            try:
                home_dir = Path.home() / ".mindspace"
                home_dir.mkdir(parents=True, exist_ok=True)
                test_file = home_dir / ".perm_check"
                test_file.touch()
                test_file.unlink(missing_ok=True)
                self.db_path = home_dir / "mindspace.db"
            except (OSError, PermissionError):
                local_dir = Path(__file__).resolve().parent.parent.parent / "data"
                local_dir.mkdir(parents=True, exist_ok=True)
                self.db_path = local_dir / "mindspace.db"

       
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError):
            pass

    def get_connection(self) -> sqlite3.Connection:
        """Creates and configures a new SQLite connection."""
        try:
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=30.0,
                detect_types=sqlite3.PARSE_DECLTYPES,
                check_same_thread=False,
            )
        except sqlite3.OperationalError:
            local_dir = Path(__file__).resolve().parent.parent.parent / "data"
            local_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = local_dir / "mindspace.db"
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=30.0,
                detect_types=sqlite3.PARSE_DECLTYPES,
                check_same_thread=False,
            )
        conn.row_factory = sqlite3.Row
        
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.execute("PRAGMA busy_timeout=5000;")
        return conn

    @contextmanager
    def session(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager providing an auto-committing or rolling-back session."""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @contextmanager
    def cursor(self) -> Generator[sqlite3.Cursor, None, None]:
        """Context manager providing a cursor with auto-commit."""
        with self.session() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
            finally:
                cursor.close()
