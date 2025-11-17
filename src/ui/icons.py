"""Defines a dataclass of prechached QIcons."""

from dataclasses import dataclass

from PyQt6.QtGui import QIcon

from ..resources import icon_path


@dataclass(frozen=True)
class Icons:
    """The dataclass of icons."""

    app = QIcon(icon_path("app.svg"))
    visible = QIcon(icon_path("visible.svg"))
    invisible = QIcon(icon_path("invisible.svg"))
    qrcode = QIcon(icon_path("qrcode.svg"))
    add = QIcon(icon_path("add.svg"))
    all = QIcon(icon_path("all.svg"))

    key = QIcon(icon_path("key.svg"))
    controller = QIcon(icon_path("controller.svg"))
    database = QIcon(icon_path("database.svg"))
    domino = QIcon(icon_path("domino.svg"))
    globe = QIcon(icon_path("globe.svg"))
    mail = QIcon(icon_path("mail.svg"))
    percent = QIcon(icon_path("percent.svg"))
    person = QIcon(icon_path("person.svg"))
    terminal = QIcon(icon_path("terminal.svg"))
