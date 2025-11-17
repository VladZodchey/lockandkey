"""This module provides a helper dialog with credential QR codes."""

from io import BytesIO

import qrcode
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel
from PyQt6.uic.load_ui import loadUi

from ..resources import ui_path
from .icons import Icons


class ShareQRDialog(QDialog):
    """A dialog for displaying credential QR codes."""

    def __init__(self, website: str):
        """Spawn the QRCode dialog with passed values."""
        super().__init__()
        loadUi(ui_path("qr.ui"), self)
        self.qrLabel: QLabel
        self.linkLabel: QLabel
        self.buttonBox: QDialogButtonBox
        self.linkLabel.setText(website)

        self.qrLabel.setPixmap(self._get_qr(website))
        self.buttonBox.clicked.connect(self.close)
        self.setWindowIcon(Icons.app)

    def _get_qr(self, data: str) -> QPixmap:
        qr = qrcode.QRCode(border=4)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qimg = QImage()
        qimg.loadFromData(buffer.getvalue())
        return QPixmap.fromImage(qimg)
