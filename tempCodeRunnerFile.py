        confirm = QMessageBox.question(self, "Hapus", "Yakin hapus?")
        if confirm == QMessageBox.Yes:
            self.tasks.pop(row)
            self.saveData()
            self.refresh()