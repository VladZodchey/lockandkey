"""This module provides a settings dialog."""

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QCheckBox, QComboBox, QDialog, QDialogButtonBox, QSpinBox
from PyQt6.uic.load_ui import loadUi

from ..resources import ui_path


class SettingDialog(QDialog):
    """A self-contained setting dialog."""

    def __init__(self):
        """Spawn the setting dialog."""
        super().__init__()
        loadUi(ui_path("settings.ui"), self)

        self.clearDelaySpin: QSpinBox
        self.clearCheck: QCheckBox
        self.buttonBox: QDialogButtonBox
        self.langCombo: QComboBox

        self.buttonBox.clicked.connect(lambda button: self.apply(button))

        self.settings = QSettings("VIDEVSYS", "lockandkey")

        self.clearDelaySpin.setValue(self.settings.value("clear_delay", 15, int))
        self.clearCheck.setChecked(self.settings.value("clear", True, bool))

        self.clearCheck.checkStateChanged.connect(
            lambda: self.clearDelaySpin.setEnabled(self.clearCheck.isChecked())
        )

    def apply(self, button) -> None:
        """Saves the settings."""
        match button.text():
            case "&Close":
                self.reject()
            case "Apply":
                language = self.langCombo.currentText()[-3:-1].lower()
                do_clear = self.clearCheck.isChecked()
                clear_delay = self.clearDelaySpin.value()
                self.settings.setValue("language", language)
                self.settings.setValue("clear", do_clear)
                self.settings.setValue("clear_delay", clear_delay)
                self.accept()
