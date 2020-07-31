from Qt import QtWidgets, QtCore, QtGui
from Qt import QtWidgets, QtGui, QtCore
import os, datetime, sys, threading, utils

class Hud(QtCore.QObject):
    def __init__(self, parent = None):
        super(Hud, self).__init__()
        self._parent = parent

        self.size = QtCore.QSize(100, 100)

        self.logo = QtWidgets.QLabel("Browther^3", parent=self._parent)
        self.logo.setPixmap(QtGui.QPixmap(os.path.join(os.path.dirname(__file__), "images/logo.png")))
        self.logo.setAlignment(QtCore.Qt.AlignRight)

        self.time = TimeWidget()
        self.time.setParent(self._parent)

        self.trayBtn = TrayBtn(self._parent)


        # self.mainLayout = QtWidgets.QVBoxLayout()
        # self.topHorizontalLayout = QtWidgets.QHBoxLayout()
        # self.bottomHorizontalLayout = QtWidgets.QHBoxLayout()
        # self.bookmarkLayout = QtWidgets.QVBoxLayout()
        # self.driveStatusLayout = QtWidgets.QVBoxLayout()
        # self.selHistoryLayout = QtWidgets.QHBoxLayout()

        # self.mainLayout.addWidget(self.logo)
        # self.mainLayout.addStretch()
        # self.mainLayout.addLayout(self.topHorizontalLayout)
        # self.mainLayout.addLayout(self.bottomHorizontalLayout)

        # self.topHorizontalLayout.addStretch()
        # self.topHorizontalLayout.addLayout(self.bookmarkLayout)

        # self.bottomHorizontalLayout.addLayout(self.driveStatusLayout)
        # self.bottomHorizontalLayout.addLayout(self.selHistoryLayout)
        # self.bottomHorizontalLayout.addStretch()


        # self.bookmarkLayout.addWidget(QtWidgets.QLabel("Bookmarks"))
        # colors = ["#e74f4a", "#f08234", "#5876b8", "#1fb5ae"]
        # for i in range(4):
        #     self.bookmarkLayout.addWidget(BookmarkPin(str(i+1), colors[i]))

        # self.driveStatusLayout.addWidget(self.time)

        # self.setLayout(self.mainLayout)
    def updateLayout(self):
        self.logo.move(self.size.width()-self.logo.sizeHint().width(), 0)
        self.time.move(0, self.size.height()-self.time.sizeHint().height())
        self.trayBtn.move((self.size.width()-self.trayBtn.sizeHint().width())/2, self.size.height()-self.trayBtn.sizeHint().height())

    def show(self):
        self.logo.show()
        self.time.show()
        self.trayBtn.show()

    def resize(self, w, h):
        self.size.setWidth(w)
        self.size.setHeight(h)
        self.updateLayout()

class BookmarkPin(QtWidgets.QLabel):
    def __init__(self, text=None, color="#ff0000"):
        super(BookmarkPin, self).__init__(text)        
        self.setStyleSheet("color: black;")
        self.color = color
        self._size = 20
        self.setFixedHeight(self._size)

        self.setAlignment(QtCore.Qt.AlignCenter)


    def paintEvent(self, event):
        center = QtCore.QPointF((self.rect().width() - self.rect().x())/2.0, (self.rect().height() - self.rect().y())/2.0)
        size = self._size/2.0
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QColor(self.color))
        painter.drawEllipse(center, size, size)
        super(BookmarkPin, self).paintEvent(event)

class BookmarkWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(BookmarkWidget, self).__init__(parent)

        # Widgets
        self.bookmarks = {}

        # Layout
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.addWidget(QtWidgets.QLabel("Bookmarks"))
        colors = ["#e74f4a", "#f08234", "#5876b8", "#1fb5ae"]
        for i in range(4):
            self.mainLayout.addWidget(BookmarkPin(str(i+1), colors[i]))

class TimeWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(TimeWidget, self).__init__(parent)

        self.signal = CustomSignal().signal

        # Widgets
        self.hour = QtWidgets.QLabel("00:00:00")
        self.hour.setStyleSheet("font-size: 18px;color: lightGrey")
        self.date = QtWidgets.QLabel("0000 00 00")
        self.date.setStyleSheet("color: grey")

        # Layout
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.addWidget(self.hour)
        self.mainLayout.addWidget(self.date)
        self.setLayout(self.mainLayout)

        # Connections
        self.signal.connect(self.updateTime)

        # Launch updater thread
        self.t = threading.Thread(target=utils.emitTimer, args=(self.signal, 1))
        self.t.setDaemon(True)
        self.t.start()

    def updateTime(self):
        if sys.version.startswith("3"):
            now = datetime.datetime.now()
        else:
            now = datetime.now()
        self.hour.setText(now.strftime("%H:%M:%S"))
        self.date.setText(now.strftime("%Y %m %d"))

class DriveStates(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(DriveStates, self).__init__(parent)

        self.mainLayout = QtWidgets.QHBoxLayout()
        self.column1Layout = QtWidgets.QVBoxLayout()
        self.column2Layout = QtWidgets.QVBoxLayout()
        self.column3Layout = QtWidgets.QVBoxLayout()

        self.mainLayout.addLayout(self.column1Layout)
        self.mainLayout.addLayout(self.column2Layout)
        self.mainLayout.addLayout(self.column3Layout)

        self.setLayout(self.mainLayout)

    def addRow(self, column1, column2, column3):
        self.column1Layout.addWidget(column1)
        self.column2Layout.addWidget(column2)
        self.column3Layout.addWidget(column3)

class TrayBtn(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(TrayBtn, self).__init__(parent)
        self._logo = QtWidgets.QLabel()
        self._logo.setFixedSize(128, 6)
        self._logo.setPixmap(QtGui.QPixmap(r"D:\dev\Python\MindNode\ui\images\tray_btn.png"))

        self.clicked = CustomSignal().signal

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self._logo)

        self.setCursor(QtCore.Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        super(TrayBtn, self).mousePressEvent(event)
        if event.buttons() == QtCore.Qt.LeftButton:
            self.clicked.emit()



class CustomSignal(QtCore.QObject):
    signal = QtCore.Signal()