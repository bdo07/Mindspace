"""Unit tests for BackupService: export, validate, and restore."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from mindspace.database.connection import DatabaseConnection
from mindspace.database.repository import MindspaceRepository
from mindspace.services.backup_service import BackupService
from mindspace.services.note_service import NoteService


class TestBackupService(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_mindspace.db"
        self.conn = DatabaseConnection(str(self.db_path))
        self.repo = MindspaceRepository(self.conn)
        self.note_service = NoteService(self.repo)
        self.backup_service = BackupService(self.conn)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_backup_and_restore_cycle(self):
        # Create some notes
        self.note_service.create_note(title="Backup Test Note 1", content="Alpha content")
        self.note_service.create_note(title="Backup Test Note 2", content="Beta content")

        stats = self.backup_service.get_stats()
        self.assertGreaterEqual(stats["active_notes"], 2)

        # Export backup
        backup_file = Path(self.temp_dir.name) / "mindspace_exported.db"
        success, msg = self.backup_service.export_backup(str(backup_file))
        self.assertTrue(success)
        self.assertTrue(backup_file.exists())

        # Validate backup
        is_valid, val_msg = self.backup_service.validate_backup(str(backup_file))
        self.assertTrue(is_valid)

        # Modify active DB
        self.note_service.create_note(title="Extra note after backup", content="Will be overwritten")
        notes_before_restore = self.note_service.list_notes()
        titles_before = [n.title for n in notes_before_restore]
        self.assertIn("Extra note after backup", titles_before)

        # Restore from backup
        restore_ok, restore_msg = self.backup_service.restore_backup(str(backup_file))
        self.assertTrue(restore_ok)

        # Verify extra note is gone, restored notes exist
        notes_after_restore = self.note_service.list_notes()
        titles_after = [n.title for n in notes_after_restore]
        self.assertNotIn("Extra note after backup", titles_after)
        self.assertIn("Backup Test Note 1", titles_after)

    def test_validate_invalid_backup(self):
        # Create empty or corrupted file
        fake_file = Path(self.temp_dir.name) / "corrupt.db"
        fake_file.write_text("not a sqlite database")

        is_valid, msg = self.backup_service.validate_backup(str(fake_file))
        self.assertFalse(is_valid)


if __name__ == "__main__":
    unittest.main()

