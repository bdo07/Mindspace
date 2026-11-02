"""Service layer for Database Backup and Restore."""

import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

from mindspace.database.connection import DatabaseConnection


class BackupService:
    """Provides safe backup, validation, and restoration for Mindspace data."""

    def __init__(self, db: DatabaseConnection):
        self.db = db

    def get_stats(self) -> Dict[str, int]:
        """Returns statistics about current database records."""
        with self.db.session() as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM notes WHERE is_archived = 0")
            active_notes = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM notes WHERE is_archived = 1")
            archived_notes = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM tasks")
            total_tasks = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM categories")
            total_categories = c.fetchone()[0]

        file_size = 0
        if self.db.db_path.exists():
            file_size = self.db.db_path.stat().st_size

        return {
            "active_notes": active_notes,
            "archived_notes": archived_notes,
            "total_tasks": total_tasks,
            "total_categories": total_categories,
            "file_size": file_size,
        }

    def export_backup(self, destination_path: str) -> Tuple[bool, str]:
        """Safely exports a consistent backup of the SQLite database."""
        source_conn = None
        dest_conn = None
        try:
            dest = Path(destination_path)
            dest.parent.mkdir(parents=True, exist_ok=True)

            source_conn = self.db.get_connection()
            dest_conn = sqlite3.connect(str(dest))
            with dest_conn:
                source_conn.backup(dest_conn)

            return True, f"Backup created successfully at: {dest.name}"
        except Exception as e:
            return False, f"Failed to export backup: {str(e)}"
        finally:
            if dest_conn:
                dest_conn.close()
            if source_conn:
                source_conn.close()

    def validate_backup(self, backup_path: str) -> Tuple[bool, str]:
        """Validates that a file is a valid Mindspace SQLite database."""
        path = Path(backup_path)
        if not path.is_file():
            return False, "File does not exist or is not a file."

        conn = None
        try:
            conn = sqlite3.connect(str(path))
            c = conn.cursor()
            c.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in c.fetchall()}
            c.close()

            required = {"notes", "tasks", "categories", "settings"}
            if not required.issubset(tables):
                missing = required - tables
                return False, f"Not a valid Mindspace backup. Missing tables: {', '.join(missing)}"

            return True, "Backup file is valid."
        except sqlite3.DatabaseError:
            return False, "Selected file is corrupted or not a valid SQLite database."
        except Exception as e:
            return False, f"Error inspecting backup file: {str(e)}"
        finally:
            if conn:
                conn.close()

    def restore_backup(self, backup_path: str) -> Tuple[bool, str]:
        """Restores database from a validated backup file."""
        is_valid, msg = self.validate_backup(backup_path)
        if not is_valid:
            return False, msg

        backup_source = None
        target_conn = None
        try:
            backup_source = sqlite3.connect(str(backup_path))
            target_conn = self.db.get_connection()
            with target_conn:
                backup_source.backup(target_conn)

            return True, "Database restored successfully!"
        except Exception as e:
            return False, f"Restore failed: {str(e)}"
        finally:
            if backup_source:
                backup_source.close()
            if target_conn:
                target_conn.close()
