#NAMA : WIWIK  PUTRI
#NIM : F1D02310096

import sys, json, os
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor


class TaskDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Task Form")

        layout = QFormLayout()

        self.title = QLineEdit()

        self.priority = QComboBox()
        self.priority.addItems(["High", "Medium", "Low"])

        self.status = QComboBox()
        self.status.addItems(["Todo", "In Progress", "Done"])

        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDate(QDate.currentDate())

        layout.addRow("Judul", self.title)
        layout.addRow("Prioritas", self.priority)
        layout.addRow("Status", self.status)
        layout.addRow("Due Date", self.date)

        btn = QPushButton("💾 Save")
        btn.clicked.connect(self.accept)
        layout.addRow(btn)

        self.setLayout(layout)

        self.setStyleSheet("""
        QDialog { background: white; }
        QLabel { color: black; font-weight: bold; }

        QLineEdit, QComboBox, QDateEdit {
            background: white;
            color: black;
            padding: 6px;
            border: 1px solid #ccc;
            border-radius: 6px;
        }

        QPushButton {
            background: #3498db;
            color: white;
            padding: 6px;
            border-radius: 6px;
        }

        QPushButton:hover { background: #2980b9; }

        QComboBox QAbstractItemView {
            background: white;
            color: black;
            selection-background-color: #3498db;
            selection-color: white;
        }

        QCalendarWidget {
            background: white;
            color: black;
        }
        """)

        if data:
            self.title.setText(data["title"])
            self.priority.setCurrentText(data["priority"])
            self.status.setCurrentText(data["status"])
            self.date.setDate(QDate.fromString(data["date"], "yyyy-MM-dd"))

    def getData(self):
        return {
            "title": self.title.text(),
            "priority": self.priority.currentText(),
            "status": self.status.currentText(),
            "date": self.date.date().toString("yyyy-MM-dd")
        }


class TaskManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Manager")
        self.resize(900, 500)

        self.file = "tasks.json"
        self.tasks = []

        self.initUI()
        self.loadData()

    def initUI(self):
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["No", "Judul Task", "Prioritas", "Status", "Due Date"]
        )

        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)

        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.setCentralWidget(self.table)

        toolbar_widget = QWidget()
        layout = QHBoxLayout()

        add_btn = QPushButton("+ Add Task")
        add_btn.setStyleSheet("background:#2ecc71;color:white;padding:6px;border-radius:6px;")
        add_btn.clicked.connect(self.addTask)

        edit_btn = QPushButton("✏ Edit")
        edit_btn.setStyleSheet("background:#3498db;color:white;padding:6px;border-radius:6px;")
        edit_btn.clicked.connect(self.editTask)

        del_btn = QPushButton("🗑 Delete")
        del_btn.setStyleSheet("background:#e74c3c;color:white;padding:6px;border-radius:6px;")
        del_btn.clicked.connect(self.deleteTask)

        self.filterBox = QComboBox()
        self.filterBox.addItems(["Semua", "Todo", "In Progress", "Done"])
        self.filterBox.currentTextChanged.connect(self.applyFilter)

        self.searchBox = QLineEdit()
        self.searchBox.setPlaceholderText("🔍 Cari task...")
        self.searchBox.textChanged.connect(self.applyFilter)

        layout.addWidget(add_btn)
        layout.addWidget(edit_btn)
        layout.addWidget(del_btn)
        layout.addSpacing(20)
        layout.addWidget(QLabel("Filter:"))
        layout.addWidget(self.filterBox)
        layout.addWidget(self.searchBox)

        layout.setContentsMargins(10, 5, 10, 5)
        toolbar_widget.setLayout(layout)

        toolbar = QToolBar()
        toolbar.addWidget(toolbar_widget)
        self.addToolBar(toolbar)

        menubar = self.menuBar()
        menubar.addMenu("File")
        menubar.addMenu("Task")
        menubar.addMenu("Help")

        self.statusBar()

        self.setStyleSheet("""
        QMainWindow { background:#ecf0f1; }
        QToolBar { background:#ecf0f1; border:none; }

        QMenuBar {
            background-color: #34495e;
            color: white;
        }

        QMenuBar::item { padding: 5px 10px; }
        QMenuBar::item:selected { background: #2c3e50; }

        QTableWidget {
            background:white;
            alternate-background-color:#f2f2f2;
            color: black;
        }

        QHeaderView::section {
            background:#34495e;
            color:white;
            padding:6px;
        }

        QLabel { color: black; font-weight: bold; }

        QComboBox, QLineEdit {
            background: white;
            color: black;
            padding: 5px;
        }

        QStatusBar {
            background: #bdc3c7;
            color: #2c3e50;
            padding: 4px;
            font-weight: bold;
        }
        """)

    def addTask(self):
        dialog = TaskDialog(self)
        if dialog.exec():
            self.tasks.append(dialog.getData())
            self.saveData()
            self.refresh()

    def editTask(self):
        row = self.table.currentRow()
        if row < 0:
            return

        dialog = TaskDialog(self, self.tasks[row])
        if dialog.exec():
            self.tasks[row] = dialog.getData()
            self.saveData()
            self.refresh()

    def deleteTask(self):
        row = self.table.currentRow()
        if row < 0:
            return

        confirm = QMessageBox.question(self, "Hapus", "Yakin hapus?")
        if confirm == QMessageBox.Yes:
            self.tasks.pop(row)
            self.saveData()
            self.refresh()

    def refresh(self):
        self.table.setRowCount(0)

        for i, task in enumerate(self.tasks):
            self.table.insertRow(i)

            status_map = {
                "Done": "Done ✓",
                "In Progress": "In Progress",
                "Todo": "Todo"
            }

            if task["priority"] == "High":
                row_color = QColor("#f8d7da")
            elif task["priority"] == "Medium":
                row_color = QColor("#fff3cd")
            else:
                row_color = QColor("#d4edda")

            values = [
                i + 1,
                task["title"],
                task["priority"],
                status_map[task["status"]],
                task["date"]
            ]

            for j, val in enumerate(values):
                item = QTableWidgetItem(str(val))
                item.setBackground(row_color)

                if j == 2:
                    item.setForeground(Qt.white)
                    item.setTextAlignment(Qt.AlignCenter)

                    if task["priority"] == "High":
                        item.setBackground(QColor("#e74c3c"))
                    elif task["priority"] == "Medium":
                        item.setBackground(QColor("#f39c12"))
                    else:
                        item.setBackground(QColor("#27ae60"))

                self.table.setItem(i, j, item)

        self.updateStatus()

    def applyFilter(self):
        keyword = self.searchBox.text().lower()
        filter_val = self.filterBox.currentText()

        for row in range(self.table.rowCount()):
            title = self.table.item(row, 1).text().lower()
            status = self.table.item(row, 3).text()

            show = True

            if keyword not in title:
                show = False

            if filter_val != "Semua" and filter_val not in status:
                show = False

            self.table.setRowHidden(row, not show)

    def updateStatus(self):
        total = len(self.tasks)
        done = sum(1 for t in self.tasks if t["status"] == "Done")
        progress = sum(1 for t in self.tasks if t["status"] == "In Progress")
        todo = sum(1 for t in self.tasks if t["status"] == "Todo")

        self.statusBar().showMessage(
            f"Total: {total} | Done: {done} | In Progress: {progress} | Todo: {todo}"
        )

    def saveData(self):
        with open(self.file, "w") as f:
            json.dump(self.tasks, f, indent=4)

    def loadData(self):
        if os.path.exists(self.file):
            with open(self.file, "r") as f:
                self.tasks = json.load(f)
        self.refresh()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskManager()
    window.show()
    sys.exit(app.exec())