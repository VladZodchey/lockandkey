"""This module provides a dialog to generate secure passwords."""

from PyQt6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QProgressBar,
    QSlider,
    QSpinBox,
    QToolButton,
)
from PyQt6.uic.load_ui import loadUi

from ..resources import ui_path
from ..utils.characters import DIGITS, EN_LOWERCASE, EN_UPPERCASE, EXTRA, RU_LOWERCASE, RU_UPPERCASE
from ..utils.logger import info
from ..utils.passwords import Security, evaluate_password, generate_password
from .icons import Icons


class GenerateDialog(QDialog):
    """The dialog for generating secure passwords."""

    def __init__(self) -> None:
        """The dialog for generating secure passwords."""
        super().__init__()
        loadUi(ui_path("generate.ui"), self)

        self.buttonBox: QDialogButtonBox
        self.passwordEdit: QLineEdit
        self.regenerateButton: QToolButton
        self.copyButton: QToolButton
        self.symbolPick: QButtonGroup
        self.lengthSpin: QSpinBox
        self.lengthSlider: QSlider
        self.entropyLevel: QProgressBar
        self.entropyLevelLabel: QLabel

        self.buttonBox.rejected.connect(lambda: self.reject())
        self.buttonBox.accepted.connect(lambda: self._accept())

        self.regenerateButton.clicked.connect(self.generate)
        self.copyButton.clicked.connect(self.copy)

        self.lengthSlider.valueChanged.connect(self.lengthSpin.setValue)
        self.lengthSpin.valueChanged.connect(self.lengthSlider.setValue)

        self.passwordEdit.textEdited.connect(self.evaluate)

        self.password: str

        self.setWindowIcon(Icons.app)

        self.generate()

    def _accept(self) -> None:
        self.password = self.passwordEdit.text()
        self.accept()

    def generate(self) -> None:
        """Generate a password with selected settings and set it into passwordEdit."""
        table = {
            "enUpperCheck": EN_UPPERCASE,
            "enLowerCheck": EN_LOWERCASE,
            "ruUpperCheck": RU_UPPERCASE,
            "ruLowerCheck": RU_LOWERCASE,
            "digitsCheck": DIGITS,
            "specialCheck": EXTRA,
        }
        s = set()
        for button in self.symbolPick.buttons():
            if button.isChecked():
                s |= table[button.objectName()]
        length = self.lengthSpin.value()
        self.passwordEdit.setText(generate_password(s, length))
        self.evaluate()

    def copy(self) -> None:
        """Put the passwordEdit value into the clipboard indefinitely."""
        clipboard = QApplication.clipboard()
        if clipboard is None:
            return
        clipboard.setText(self.passwordEdit.text())

    def evaluate(self) -> None:
        """Evaluates the passwords strength and displays it."""
        password = self.passwordEdit.text()
        level, entropy = evaluate_password(password)
        self.entropyLevel.setValue(int(min(entropy, 100.0)))
        self.entropyLevelLabel.setText(f"({self.tr(str(level))})")
