"""The application entrypoint."""

import sys

from PyQt6.QtCore import QCoreApplication, Qt
from PyQt6.QtWidgets import QApplication

from . import __version__
from .ui.main import MainWindow
from .utils.logger import info


def main() -> int:
    """>> THE application entrypoint. <<"""  # noqa: D415
    info(f"Starting up Lock and Key with version {__version__}")

    QCoreApplication.setApplicationName("Lock and key")
    QCoreApplication.setOrganizationName("VIDEVSYS")
    QCoreApplication.setOrganizationDomain("videvsys.ru")
    QCoreApplication.setApplicationVersion(__version__)

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    app.aboutToQuit.connect(window._close_event)

    return app.exec()


if __name__ == "__main__":
    main()
