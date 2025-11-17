"""This module provides a simple "about" dialog."""

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QPushButton
from PyQt6.uic.load_ui import loadUi

from .. import __version__
from ..resources import ui_path
from .icons import Icons


class AboutDialog(QDialog):
    """A simple "about" dialog."""

    def __init__(self):
        """A simple "about" dialog."""
        super().__init__()
        loadUi(ui_path("about.ui"), self)

        self.buttonBox: QDialogButtonBox
        self.authorButton: QPushButton
        self.sourceButton: QPushButton
        self.versionLabel: QLabel
        self.versionLabel.setText(f"v{__version__}")

        self.buttonBox.clicked.connect(self.close)
        self.authorButton.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://vladzodchey.ru/"))
        )
        self.sourceButton.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://github.com/vladzodchey/lockandkey/"))
        )

        self.setWindowIcon(Icons.app)
