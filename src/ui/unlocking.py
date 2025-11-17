"""This module provides the password prompt modal."""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog, QLineEdit
from PyQt6.uic.load_ui import loadUi

from ..resources import ui_path
from .icons import Icons


class UnlockingDialog(QDialog):
    """The password prompt modal."""

    check = pyqtSignal(str)

    def __init__(self, file: str):
        """Spawn the prompt.

        Args:
            file: The path to database getting unlocked
        """
        super().__init__()
        loadUi(ui_path("unlock.ui"), self)

        self.pathLabel.setText(file)
        self.showButton.clicked.connect(self._hide_n_seek)
        self.setWindowIcon(Icons.app)

        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.accepted.connect(self._on_check_clicked)

    def _hide_n_seek(self) -> None:
        if self.passwordEdit.echoMode() == QLineEdit.EchoMode.Normal:
            self.passwordEdit.setEchoMode(QLineEdit.EchoMode.Password)
            self.showButton.setIcon(Icons.visible)
        else:
            self.passwordEdit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.showButton.setIcon(Icons.invisible)

    def _on_check_clicked(self) -> None:
        password = self.passwordEdit.text()
        self.check.emit(password)

    def wrong(self) -> None:
        """Tell the user that something is wrong."""
        self.errorLabel.setText(self.tr("The key doesn't fit."))
