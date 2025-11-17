"""This module provides the Enter dialog, a dialog for creating and editing an entry."""

from PyQt6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QLabel, QLineEdit, QToolButton
from PyQt6.uic.load_ui import loadUi

from ..models.db import Glue
from ..resources import ui_path
from ..utils.logger import error
from .generation import GenerateDialog
from .icons import Icons


class EnterDialog(QDialog):
    """The dialog for creating an entry."""

    def __init__(self, glue: Glue, i: int | None = None):
        """The dialog for creating or editing an entry.

        Args:
            glue: A `Glue` instance to insert entry to.
            i: An existing entry ID to edit, if passed. Otherwise a new one is created
        """
        super().__init__()
        loadUi(ui_path("entry.ui"), self)

        self.glue = glue

        self.generateButton: QToolButton
        self.showButton: QToolButton
        self.passwordEdit: QLineEdit
        self.nameEdit: QLineEdit
        self.loginEdit: QLineEdit
        self.websiteEdit: QLineEdit
        self.groupCombo: QComboBox
        self.buttonBox: QDialogButtonBox
        self.errorLabel: QLabel

        self.generateButton.clicked.connect(self.generate)
        self.showButton.clicked.connect(self._hide_n_seek)

        self.buttonBox.rejected.connect(self.close)
        if i is None:
            self.buttonBox.accepted.connect(self.save)
        else:
            self.buttonBox.accepted.connect(lambda: self.apply(i))
            self._pull_up(i)

        groups = self.glue.groups()
        self.groupCombo.addItem(Icons.all, "<no group>", None)
        for j, name, icon_id in groups:
            self.groupCombo.addItem(getattr(Icons, icon_id, Icons.key), name, j)
        self.groupCombo.setCurrentIndex(0)

        self.setWindowIcon(Icons.app)

    def generate(self) -> None:
        """Opens up password generation dialog."""
        gen = GenerateDialog()
        if gen.exec() == QDialog.DialogCode.Accepted:
            self.passwordEdit.setText(gen.password)

    def _hide_n_seek(self) -> None:
        if self.passwordEdit.echoMode() == QLineEdit.EchoMode.Normal:
            self.passwordEdit.setEchoMode(QLineEdit.EchoMode.Password)
            self.showButton.setIcon(Icons.visible)
        else:
            self.passwordEdit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.showButton.setIcon(Icons.invisible)

    def save(self) -> None:
        """Attempts to save an entry."""
        name = self.nameEdit.text()
        secret = self.passwordEdit.text()
        if not name or not secret:
            self.errorLabel.setText(self.tr("Please pick an entry name and secret."))
            return
        login = self.loginEdit.text() or None
        website = self.websiteEdit.text() or None
        group = self.groupCombo.currentData()
        self.glue.add_entry(name, secret, login, website, group)
        self.accept()

    def apply(self, i: int) -> None:
        """Applies changes to an existing entry.

        Args:
            i: The id of the entry to change, `int`
        """
        name = self.nameEdit.text()
        secret = self.passwordEdit.text()
        if not name or not secret:
            self.errorLabel.setText(self.tr("Please pick an entry name and secret."))
            return
        login = self.loginEdit.text() or None
        website = self.websiteEdit.text() or None
        group = self.groupCombo.currentData()
        self.glue.edit_entry(i, name, secret, login, website, group)
        self.accept()

    def _pull_up(self, i: int) -> None:
        res = self.glue.get_entry(i)
        if not res:
            error("Tried to pull up info on a nonexistent entry, aborting.")
            self.reject()
            return
        name, secret, login, website, group = res
        self.nameEdit.setText(name)
        self.passwordEdit.setText(secret)
        self.loginEdit.setText(login)
        self.websiteEdit.setText(website)
        self.groupCombo.setCurrentText(group)
