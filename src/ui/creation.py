"""This module provides a database creation modal."""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QFileDialog, QLabel, QLineEdit, QPushButton
from PyQt6.uic.load_ui import loadUi

from ..models.cryptid import bytes_to_file
from ..models.db import Glue
from ..resources import ui_path
from .icons import Icons


class CreationDialog(QDialog):
    """The dialog for creating a new database."""

    complete = pyqtSignal(str)

    def __init__(self) -> None:
        """Create and bind buttons of the dialog."""
        super().__init__()
        loadUi(ui_path("create.ui"), self)

        self.passwordEdit: QLineEdit
        self.showButton: QPushButton
        self.browseButton: QPushButton
        self.repeatEdit: QLineEdit
        self.buttonBox: QDialogButtonBox
        self.errorLabel: QLabel
        self.pathLabel: QLabel

        self.showButton.clicked.connect(self._hide_n_seek)
        self.setWindowIcon(Icons.app)

        self.buttonBox.rejected.connect(self.close)
        self.buttonBox.accepted.connect(self.save)

        self.passwordEdit.textEdited.connect(self._compare)
        self.repeatEdit.textEdited.connect(self._compare)

        self.browseButton.clicked.connect(self._pick_path)

        self.save_to: str = ""

    def _hide_n_seek(self) -> None:
        if self.passwordEdit.echoMode() == QLineEdit.EchoMode.Normal:
            self.passwordEdit.setEchoMode(QLineEdit.EchoMode.Password)
            self.showButton.setIcon(Icons.visible)
        else:
            self.passwordEdit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.showButton.setIcon(Icons.invisible)

    def save(self) -> None:
        """Actually creates the database, validates inputs."""
        if not self._compare():
            return
        if not self.save_to:
            self.warn(self.tr("Save path is not selected."))
            return
        gl = Glue.new()
        bytes_to_file(self.save_to, self.passwordEdit.text(), gl.to_bytes())
        self.complete.emit(self.save_to)
        self.close()

    def _compare(self) -> bool:
        first = self.passwordEdit.text()
        second = self.repeatEdit.text()
        if first != second:
            self.warn(self.tr("Password doesn't match the repeat."))
        elif not first:
            self.warn("Don't use an empty password, please")
        else:
            self.warn("")
        return first == second and bool(first)

    def warn(self, message: str) -> None:
        """Displays a warning message to the user.

        Args:
            message: The message to show
        """
        self.errorLabel.setText(message)

    def _pick_path(self) -> None:
        filter_str = "Lock and Key DB (*.lak);;All Files (*)"

        path, _ = QFileDialog.getSaveFileName(
            caption="Where to store the db...",
            filter=filter_str,
        )

        if not path:
            return
        if not path.lower().endswith(".lak"):
            path += ".lak"

        self.pathLabel.setText(f"{self.tr('Save to:')} {path}")
        self.save_to = path
