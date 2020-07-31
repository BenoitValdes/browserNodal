from Qt import QtWidgets, QtGui, QtCore
import graph, utils

class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # Init        
        self.resize(500, 500)
        if hasattr(utils.settings, "geometry"):
            self.setGeometry(*utils.settings.geometry)
        self.setObjectName("self")

        # CSS
        css = """
        #self{
            background-color: #131313;
        }
        """
        self.setStyleSheet(css)


        # Widgets
        self._graph = graph.View()
        self.trayBtn = QtWidgets.QPushButton("^^")

        # Layout
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        self.trayLayout = QtWidgets.QHBoxLayout()
        self.trayLayout.addStretch()
        self.trayLayout.addWidget(self.trayBtn)
        self.trayLayout.addStretch()

        self.mainLayout.addWidget(self._graph)
        # self.mainLayout.addLayout(self.trayLayout)

        self.setLayout(self.mainLayout)

    def show(self):
        """Add the autoload part (to be sure that the UI already popup and do not break the zoom)
        """
        super(MainWindow, self).show()        
        # Autoload the last project opened
        if len(utils.settings.recentProjects) > 0 and utils.settings.autoloadLastProject is True:
            self._graph.load(utils.settings.recentProjects[0])

    def closeEvent(self, event):
        """
        When we exit the software, we have to save differents thing before that.
        We have to save the data in the software (when we are not in debug mode)
        and also save the position of the software UI.
        """
        utils.settings.geometry = utils.rectToList(self.geometry())
        utils.settings.save()
        super(MainWindow, self).closeEvent(event)

