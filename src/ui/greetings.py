"""A simple greetings page widget for the MainWindow."""

from PyQt6.QtWidgets import QLabel, QPushButton, QWidget
from PyQt6.uic.load_ui import loadUi

from .. import __version__
from ..resources import ui_path


class GreetingsWidget(QWidget):
    """The greetings page widget class."""

    def __init__(self, parent) -> None:
        """Create and bind the greetings page."""
        super().__init__()
        loadUi(ui_path("greeting.ui"), self)

        self.root = parent

        self.versionLabel: QLabel
        self.openButton: QPushButton
        self.newButton: QPushButton

        self.versionLabel.setText(f"v{__version__}")
        self.openButton.clicked.connect(lambda: self.root.open_db())
        self.newButton.clicked.connect(lambda: self.root.new_db())
