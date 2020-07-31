from Qt import QtWidgets, QtCore
import sys, utils, mainWIndow, graph

if __name__ == "__main__":
    #QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(utils.css)
    window = mainWIndow.MainWindow()
    window.show()
    sys.exit(app.exec_())