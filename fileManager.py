from Qt import QtWidgets
import utils

class Panel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Panel, self).__init__(parent)

        # Widgets
        self.filterInput = QtWidgets.QLineEdit()
        self.filterInput.setPlaceholderText("filter...")
        self.path = QtWidgets.QLineEdit()
        self.fileTree = QtWidgets.QTreeWidget()
        self.fileTree.setHeaderLabels(["", "Name", "Size", "Date"])

        # Layout
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.filterLayout = QtWidgets.QHBoxLayout()
        self.filterLayout.addStretch()
        self.filterLayout.addWidget(self.filterInput)

        self.mainLayout.addLayout(self.filterLayout)
        self.mainLayout.addWidget(self.path)
        self.mainLayout.addWidget(self.fileTree)

        self.setLayout(self.mainLayout)


