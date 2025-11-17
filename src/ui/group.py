"""This module provides a group creation/modification dialog."""

from PyQt6.QtWidgets import QButtonGroup, QDialog, QDialogButtonBox, QLabel, QLineEdit
from PyQt6.uic.load_ui import loadUi

from src.models.db import Glue

from ..resources import ui_path
from ..utils.logger import error
from .icons import Icons


class GroupingDialog(QDialog):
    """A group creation/modification dialog."""

    def __init__(self, glue: Glue, i: int | None = None):
        """A group creation/modification dialog.

        Args:
            glue: A `Glue` object to interact with
            i: An existing group ID to modify. Creates a new one if `None`
        """
        super().__init__()
        loadUi(ui_path("group.ui"), self)

        self.glue = glue

        self.buttonBox: QDialogButtonBox
        self.groupNameEdit: QLineEdit
        self.iconGroup: QButtonGroup
        self.errorLabel: QLabel

        self.buttonBox.rejected.connect(self.reject)
        if i is None:
            self.buttonBox.accepted.connect(self.save)
        else:
            self.buttonBox.accepted.connect(lambda: self.apply(i))
            self._pull_up(i)

        self.setWindowIcon(Icons.app)

    def save(self) -> None:
        """Saves the configuration as a new group."""
        name = self.groupNameEdit.text()
        if not name:
            self.errorLabel.setText(self.tr("Please pick a name."))
            return
        icon = "key"
        for button in self.iconGroup.buttons():
            if button.isChecked():
                icon = button.objectName()[:-6]
                if not hasattr(Icons, icon):  # pretty sketchy but alr ig
                    icon = "key"
        self.glue.add_group(name, icon)
        self.accept()

    def apply(self, i: int) -> None:
        """Applies changes to an existing group by ID `i`."""
        name = self.groupNameEdit.text()
        if not name:
            self.errorLabel.setText(self.tr("Please pick a name."))
            return
        icon = "key"
        for button in self.iconGroup.buttons():
            if button.isChecked():
                icon = button.objectName()[:-6]
                if not hasattr(Icons, icon):  # pretty sketchy but alr ig
                    icon = "key"
        self.glue.edit_group(i, name, icon)
        self.accept()

    def _pull_up(self, i: int) -> None:
        res = self.glue.get_group(i)
        if res is None:
            error("Attempted to pull up a nonexistent group. Aborting...")
            self.reject()
            return
        name, icon_id = res
        self.groupNameEdit.setText(name)
        for button in self.iconGroup.buttons():
            if button.objectName().startswith(icon_id):
                button.setChecked(True)
