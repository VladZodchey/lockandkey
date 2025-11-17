"""The application entrypoint."""

import sys

from PyQt6.QtCore import QCoreApplication, QLocale, QSettings, Qt, QTranslator
from PyQt6.QtWidgets import QApplication

from . import __version__
from .resources import tr_path
from .ui.main import MainWindow
from .utils.logger import info, warning


def main() -> None:
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

    settings = QSettings("VIDEVSYS", "lockandkey")
    lang = settings.value("language", "en", str)

    translator = QTranslator(app)

    locale = QLocale(lang)
    QLocale.setDefault(locale)

    if translator.load(str(tr_path(f"{lang}.qm"))):
        app.installTranslator(translator)
        info("Language install success.")
    else:
        warning("Failed to install languages.")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
