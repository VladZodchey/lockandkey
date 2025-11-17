"""This module provides the Secrets page widget."""

from contextlib import suppress

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFrame,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)
from PyQt6.uic.load_ui import loadUi

from src.ui.group import GroupingDialog
from src.ui.qr import ShareQRDialog

from ..models.db import Glue
from ..resources import ui_path
from ..utils.logger import info
from .entry import EnterDialog
from .generation import GenerateDialog
from .icons import Icons
from .settings import SettingDialog


class SecretsWidget(QWidget):
    """The secrets page widget."""

    changed = pyqtSignal()

    def __init__(self, root):  # this is a very chonky constructor.
        """Spawns the widget and populates it if possible.

        The Secrets table assumes a lot about its parent, so reuse is practically impossible.
        """
        super().__init__()
        loadUi(ui_path("secrets.ui"), self)

        self.root = root
        self.glue: Glue = self.root.glue

        self.secretsTable: QTableWidget

        self.openDbButton: QPushButton
        self.saveDbButton: QPushButton
        self.lockDbButton: QPushButton

        self.addEntryButton: QPushButton
        self.editEntryButton: QPushButton
        self.deleteEntryButton: QPushButton

        self.searchEdit: QLineEdit

        self.searchButton: QPushButton
        self.shareButton: QPushButton
        self.keyButton: QPushButton
        self.settingsButton: QPushButton

        self.clipboardFrame: QFrame
        self.clipboardProgress: QProgressBar

        self.clipboardFrame.hide()

        self.groupCombo: QComboBox
        self.groupCombo.currentIndexChanged.connect(self.select_group)

        self.clear_timer = QTimer(self)
        self.clear_timer.setSingleShot(True)
        self.clear_timer.timeout.connect(self._clear_clipboard)
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self._update_progress)
        self.clipboard = QApplication.clipboard()

        self.secretsTable.currentCellChanged.connect(self.selected)

        self.openDbButton.clicked.connect(lambda: self.root.open_db())
        self.saveDbButton.clicked.connect(self._save)
        self.changed.connect(lambda: self.saveDbButton.setEnabled(True))
        self.lockDbButton.clicked.connect(lambda: self.root.lock_db())

        self.saveShortcut = QShortcut(QKeySequence.StandardKey.Save, self)
        self.saveShortcut.activated.connect(self._save)

        self.copyShortcut = QShortcut(QKeySequence.StandardKey.Copy, self.secretsTable)
        self.copyShortcut.activated.connect(self._copy_from_table)

        self._set_up_buttons()

        self.update_groups()
        self.groupCombo.setCurrentIndex(0)
        self.display()

    def _set_up_buttons(self) -> None:
        self.addEntryButton.clicked.connect(self.new_entry)
        self.editEntryButton.clicked.connect(self.edit_entry)
        self.deleteEntryButton.clicked.connect(self.delete_entry)

        self.searchButton.clicked.connect(self.search)
        self.searchEdit.returnPressed.connect(self.search)
        self.keyButton.clicked.connect(lambda: GenerateDialog().exec())
        self.settingsButton.clicked.connect(lambda: SettingDialog().exec())

        self.root.actionCreate_entry.setEnabled(True)
        self.root.actionCreate_entry.triggered.connect(self.new_entry)
        self.root.actionEdit_entry.triggered.connect(self.edit_entry)
        self.root.actionDelete_entry.triggered.connect(self.delete_entry)

        self.root.actionCreate_group.setEnabled(True)
        self.root.actionCreate_group.triggered.connect(self.new_group)
        self.root.actionEdit_group.triggered.connect(self.edit_group)
        self.root.actionDelete_group.triggered.connect(self.delete_group)

    def display(self, query: str | None = None) -> None:
        """Load values in to the table."""
        self.secretsTable.clear()
        self.secretsTable.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.secretsTable.setColumnCount(6)
        self.secretsTable.setHorizontalHeaderLabels(
            (
                self.tr("Group"),
                self.tr("Name"),
                self.tr("Secret"),
                self.tr("Login"),
                self.tr("Website"),
                self.tr("Last accessed"),
            )
        )
        if self.glue is None:
            return
        group = self.groupCombo.currentData()
        if group == "all":
            group = None
        values = self.glue.entries(text=query, group=group)
        if not values:
            self.secretsTable.setRowCount(0)
            return
        self.secretsTable.setRowCount(len(values))
        for x, row in enumerate(values):
            icon_id, group_name, secret_id, name, secret, login, website, last_access = row
            if icon_id and group_name:
                group_item = QTableWidgetItem(getattr(Icons, icon_id, Icons.key), str(group_name))
                self.secretsTable.setItem(x, 0, group_item)

            name_item = QTableWidgetItem(name)
            name_item.setData(Qt.ItemDataRole.UserRole, secret_id)
            self.secretsTable.setItem(x, 1, name_item)
            secret_item = QTableWidgetItem("*" * len(secret))
            secret_item.setData(Qt.ItemDataRole.UserRole, secret)
            self.secretsTable.setItem(x, 2, secret_item)
            self.secretsTable.setItem(x, 3, QTableWidgetItem(str(login)))
            self.secretsTable.setItem(x, 4, QTableWidgetItem(str(website)))
            self.secretsTable.setItem(x, 5, QTableWidgetItem(str(last_access)))
        self.secretsTable.resizeColumnsToContents()
        self.secretsTable.resizeColumnToContents(-1)
        header = self.secretsTable.horizontalHeader()
        for i in range(self.secretsTable.columnCount()):
            mode = (
                QHeaderView.ResizeMode.Stretch
                if i == self.secretsTable.columnCount() - 1
                else QHeaderView.ResizeMode.ResizeToContents
            )
            if header:
                header.setSectionResizeMode(i, mode)

    def selected(self) -> None:
        """Handles cells being selected."""
        i = self.get_id()
        if i is None:
            self.editEntryButton.setEnabled(False)
            self.deleteEntryButton.setEnabled(False)
            self.root.actionEdit_entry.setEnabled(False)
            self.root.actionDelete_entry.setEnabled(False)
            self.shareButton.setEnabled(False)
            return
        self.editEntryButton.setEnabled(True)
        self.deleteEntryButton.setEnabled(True)
        self.root.actionEdit_entry.setEnabled(True)
        self.root.actionDelete_entry.setEnabled(True)
        res = self.glue.get_entry(i)
        if not res:
            return
        website = res[3]
        if not website:
            self.shareButton.setEnabled(False)
            return
        self.shareButton.setEnabled(True)
        with suppress(TypeError):
            self.shareButton.clicked.disconnect()
        self.shareButton.clicked.connect(lambda: self.share_qr(website))

    def get_id(self) -> int | None:
        """Get the DB ID of a selected entry.

        Returns:
            The ID in `int` if some entry is selected, `None` otherwise.
        """
        if self.glue is None:
            return None
        row = self.secretsTable.currentRow()
        if row == -1:
            return None
        item = self.secretsTable.item(row, 1)
        if item is None:
            return None
        try:
            return int(item.data(Qt.ItemDataRole.UserRole))
        except ValueError:
            return None

    def new_entry(self) -> None:
        """Prompts the new entry creation."""
        if self.glue is None:
            return
        dialog = EnterDialog(self.glue)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.display()
            self.changed.emit()

    def edit_entry(self) -> None:
        """Prompts an existing entry modification."""
        i = self.get_id()
        if i is None:
            return

        dialog = EnterDialog(self.glue, i)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.display()
            self.changed.emit()

    def delete_entry(self) -> None:
        """Prompts entry deletion."""
        i = self.get_id()
        if i is None:
            return
        res = QMessageBox.question(
            self, "Achtung!", self.tr("Are you sure you want to delete an entry?")
        )
        if res == QMessageBox.StandardButton.Yes:
            self.glue.delete_entry(i)
            self.display()
            self.changed.emit()

    def _save(self) -> None:
        self.root.save_db()
        self.saveDbButton.setEnabled(False)

    def share_qr(self, website: str) -> None:
        """Open a dialog with selected row's data as QR codes."""
        dialog = ShareQRDialog(website)
        dialog.exec()

    def search(self) -> None:
        """Performs a search for entries with a name similar to query."""
        query = self.searchEdit.text()
        self.display(query)

    def new_group(self) -> None:
        """Prompts group creation."""
        dialog = GroupingDialog(self.glue)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.update_groups()
            self.changed.emit()

    def edit_group(self) -> None:
        """Prompts group modification."""
        group = self.groupCombo.currentData()
        if isinstance(group, int):
            dialog = GroupingDialog(self.glue, group)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.update_groups()
                self.changed.emit()

    def delete_group(self) -> None:
        """Prompts group deletion."""
        group = self.groupCombo.currentData()
        if isinstance(group, int):
            res = QMessageBox.question(
                self,
                "Achtung!",
                self.tr("""
                Are you sure you want to delete a group?
                Your entries live on, just without a group.
                """),
            )
            if res == QMessageBox.StandardButton.Yes:
                self.glue.delete_group(group)
                self.display()
                self.update_groups()
                self.changed.emit()

    def update_groups(self) -> None:
        """Populates the group combo box with data."""
        if self.glue is None:
            return
        groups = self.glue.groups()
        self.groupCombo.clear()
        self.groupCombo.addItem(Icons.all, self.tr("All"), "all")
        for i, name, icon in groups:
            if icon:
                self.groupCombo.addItem(QIcon(getattr(Icons, icon)), name, i)
        self.groupCombo.addItem(Icons.add, self.tr("New group..."), "new")

    def select_group(self, i: int) -> None:
        """Handles group being re-selected."""
        match self.groupCombo.currentData():
            case "new":
                self.new_group()
            case "all":
                self.root.actionEdit_group.setEnabled(False)
                self.root.actionDelete_group.setEnabled(False)
            case _:
                self.root.actionEdit_group.setEnabled(True)
                self.root.actionDelete_group.setEnabled(True)
        self.display()

    def _copy_from_table(self) -> None:
        if self.clipboard is None:
            return
        column = self.secretsTable.currentColumn()
        item = self.secretsTable.currentItem()
        if item is None:
            return
        if column != 2:  # noqa: PLR2004
            self._clear_clipboard()
            self.clipboard.setText(item.text())
            return
        value = item.data(Qt.ItemDataRole.UserRole)
        self.clipboard.setText(value)
        if self.root.do_clear:
            self.clipboardFrame.show()
            self.clear_timer.start(self.root.clear_delay * 1000)
            self.progress_timer.start(1000)
            self.clipboardProgress.setValue(self.root.clear_delay)
            self.clipboardProgress.setMaximum(self.root.clear_delay)

    def _clear_clipboard(self) -> None:
        if self.clipboard is None:
            return
        self.clipboard.clear()
        self.clipboardFrame.hide()
        self.progress_timer.stop()
        self.clear_timer.stop()
        info("Cleared secret from clipboard.")

    def _update_progress(self) -> None:
        self.clipboardProgress.setValue(max(0, self.clipboardProgress.value() - 1))
