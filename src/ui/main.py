"""The main window spawn class and load up of Greeting or Table classes."""

from PyQt6.QtCore import QSettings, QUrl
from PyQt6.QtGui import QAction, QDesktopServices
from PyQt6.QtWidgets import QDialog, QFileDialog, QMainWindow, QMenu, QMessageBox
from PyQt6.uic.load_ui import loadUi

from ..errors import IncorrectError
from ..models.cryptid import bytes_to_file, file_to_bytes
from ..models.customs import dump_to_file, restore_from_file
from ..models.db import Glue
from ..resources import ui_path
from ..utils.logger import error, info
from .about import AboutDialog
from .creation import CreationDialog
from .greetings import GreetingsWidget
from .icons import Icons
from .settings import SettingDialog
from .table import SecretsWidget
from .unlocking import UnlockingDialog


class MainWindow(QMainWindow):
    """The main application window. Without a nested widget, it only provides the menu bar."""

    def __init__(self) -> None:
        """Spawn the MainWindow."""
        super().__init__()
        loadUi(ui_path("main.ui"), self)

        self.setWindowIcon(Icons.app)
        self.setWindowTitle(self.tr("Lock And Key"))
        self.glue: Glue | None = None
        self.cred: tuple[str, str] | None = None

        self.settings = QSettings("VIDEVSYS", "lockandkey")

        self.menuDatabase: QMenu
        self.menuEntry: QMenu
        self.menuGroup: QMenu
        self.menuAbout: QMenu

        self.actionCreate_database: QAction
        self.actionSave_database: QAction
        self.actionOpen_database: QAction
        self.actionLock_database: QAction
        self.actionDump: QAction
        self.actionRestore: QAction

        self.actionCreate_entry: QAction
        self.actionEdit_entry: QAction
        self.actionDelete_entry: QAction

        self.actionCreate_group: QAction
        self.actionEdit_group: QAction
        self.actionDelete_group: QAction

        self.actionDocs: QAction
        self.actionSettings: QAction
        self.actionInfo: QAction

        info("No recent database found, greeting user")  # mockup, recents aren't stored yet.
        self.greet()

        self.get_settings()

        self.actionCreate_database.triggered.connect(self.new_db)
        self.actionOpen_database.triggered.connect(lambda: self.open_db())
        self.actionLock_database.triggered.connect(self.lock_db)
        self.actionSave_database.triggered.connect(self.save_db)
        self.actionDump.triggered.connect(self.dump_db)
        self.actionRestore.triggered.connect(self.restore_db)

        self.actionDocs.triggered.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://github.com/vladzodchey/lockandkey"))
        )
        self.actionSettings.triggered.connect(lambda: self.set_settings())
        self.actionInfo.triggered.connect(lambda: AboutDialog().exec())

    def open_db(self, path: str | None = None) -> None:
        """Open a database file."""
        if path is not None:
            self.unlock_lak(path)
        else:
            path, t = QFileDialog.getOpenFileName(
                self,
                "Select a database...",
                "",
                "Lock and Key vault (*.lak);;Bare DB (*.db, *.sqlite)",
            )
            if not path:
                return
            match t:
                case "Bare DB (*.db, *.sqlite)":
                    self.glue = Glue.from_bare(path)
                    self.reveal_secrets()
                case "Lock and Key vault (*.lak)":
                    self.unlock_lak(path)

    def unlock_lak(self, path: str):
        """Prompts the user to unlock LaK's encrypted DB.

        Args:
            path: The path to the file, `str`
        """

        def check_password(password):
            try:
                data = file_to_bytes(path, password)
                self.glue = Glue.from_bytes(data)
                self.cred = (path, password)  # DO NOT DO THIS! My deadline is burning, yours don't.
                self.update_title()
                modal.accept()
            except IncorrectError:
                modal.wrong()
            except ValueError:
                error("Bad DB file. Your data may be corrupted.")
                modal.close()

        modal = UnlockingDialog(path)
        modal.check.connect(lambda password: check_password(password))
        if modal.exec() == QDialog.DialogCode.Accepted:
            self.reveal_secrets()

    def new_db(self) -> None:
        """Spawn database creation modal."""
        info("Creating new database...")
        modal = CreationDialog()
        modal.complete.connect(lambda path: self.open_db(path))
        if modal.exec() == QDialog.DialogCode.Accepted:
            info("Creation success.")

    def reveal_secrets(self) -> None:
        """Change the greet widget to a secrets table widget and populate it."""
        self.secrets = SecretsWidget(self)
        self.secrets.changed.connect(self._update_save_state)
        self.actionLock_database.setEnabled(True)
        self.actionDump.setEnabled(True)
        self.actionRestore.setEnabled(True)
        self.menuEntry.setEnabled(True)
        self.menuGroup.setEnabled(True)
        self.setCentralWidget(self.secrets)

    def greet(self) -> None:
        """Change the secrets table widget/empty widget to a greet widget."""
        greeting = GreetingsWidget(self)
        self.setCentralWidget(greeting)
        self.actionSave_database.setEnabled(False)
        self.actionLock_database.setEnabled(False)
        self.actionRestore.setEnabled(False)
        self.actionDump.setEnabled(False)
        self.menuEntry.setEnabled(False)
        self.menuGroup.setEnabled(False)

    def set_settings(self) -> None:
        """Spawn the setting window."""
        dialog = SettingDialog()
        dialog.exec()
        self.get_settings()

    def save_db(self) -> None:
        """Saves the database state back into its file."""
        if self.glue is None or not self.cred:
            return
        bytes_to_file(self.cred[0], self.cred[1], self.glue.to_bytes())
        self.glue.dirty = False
        self.update_title()

    def lock_db(self) -> None:
        """Save data and log out of the current database."""
        self.save_db()
        self.cred = None
        self.glue = None
        self.update_title()
        self.secrets = None
        self.greet()

    def closeEvent(self, a0):  # noqa: N802
        """Catches the close event, prompting saving before exiting."""
        if a0 is None:
            return
        if self.glue and self.glue.dirty:
            res = QMessageBox.question(
                self,
                "Achtung!",
                self.tr("Database was modified. Save changes?"),
                buttons=QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Cancel,
            )
            match res:
                case QMessageBox.StandardButton.Discard:
                    a0.accept()
                case QMessageBox.StandardButton.Save:
                    self.save_db()
                    a0.accept()
                case QMessageBox.StandardButton.Cancel:
                    a0.ignore()
            return
        a0.accept()

    def _update_save_state(self) -> None:
        self.actionSave_database.setEnabled(True)
        self.update_title()

    def update_title(self) -> None:
        """Updates the window title to display the DB path and dirtyness, if possible."""
        if not self.cred or not self.glue:
            self.setWindowTitle(self.tr("Lock And Key"))
            return
        self.setWindowTitle(f"{'* ' if self.glue.dirty else ''}{self.cred[0]}")

    def get_settings(self) -> None:
        """Reloads settings."""
        self.do_clear = self.settings.value("clear", True, bool)
        self.clear_delay = self.settings.value("clear_delay", 15, int)

    def dump_db(self) -> None:
        """Dumps the database to a file."""
        if self.glue is None:
            return
        output, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Dump to file..."),
            "",
            filter="Comma-separated values (*.csv);;All files (*)",
        )
        if not output:
            return
        dump_to_file(self.glue, output)
        QMessageBox.information(
            self, self.tr("Success"), f"{self.tr('Dumped database to ')} {output}"
        )

    def restore_db(self) -> None:
        """Prompt restoration from .csv file."""
        if self.glue is None:
            return
        inp, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Restore from file..."),
            "",
            filter="Comma-separated values (*.csv);;All files (*)",
        )
        if not inp:
            return
        restore_from_file(self.glue, inp)
        QMessageBox.information(self, self.tr("Success"), f"{self.tr('Restored from ')} {inp}")
        self._update_save_state()
        if self.secrets is not None:
            self.secrets.display()
            self.secrets.update_groups()
