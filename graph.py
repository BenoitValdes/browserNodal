from Qt import QtCore, QtGui, QtWidgets, QtSvg
import nodalItems
import utils, sys, os
from hud import Hud
import subprocess
from collections import OrderedDict
import json

class View(QtWidgets.QGraphicsView):
    def __init__(self):
        super(View, self).__init__()
        # CSSS
        css = """
        QGraphicsView{
            border: None;
        }
        """
        self.setStyleSheet(css)

        # Init
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.setRubberBandSelectionMode(QtCore.Qt.IntersectsItemShape)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)

        self._connectionsItems = []
        self._rootsList = []
        self.rightClickNode = None
        self.currentProject = None

        self.colors = ["#e74f4A", "#f08235", "#e1da18", "#84bc3b", "#5976b9", "#554696"]

        self.menu = None

        self.hud = Hud(self)

        self._scene = Scene(self)
        self._scene.setSceneRect(-10000, -10000, 20000, 20000)
        self.setScene(self._scene)

        # Context Menu Buttons
        self.helpBtn = self.createMenuItem("Help", self,
                shortcut=QtGui.QKeySequence("Ctrl+H"),
                statusTip="Open in the explorer the path of the selected node",
                triggered=self.help)
        self.aboutBtn = self.createMenuItem("About", self,
                statusTip="Open in the explorer the path of the selected node",
                triggered=self.about)
        self.settingsBtn = self.createMenuItem("Settings", self,
                shortcut=QtGui.QKeySequence("Ctrl+P"),
                statusTip="Open in the explorer the path of the selected node",
                triggered=self.settings)

        self.openExplorerSelectedNodeBtn = self.createMenuItem("Open in explorer", self,
                statusTip="Open in the explorer the path of the selected node",
                triggered=self.openExplorerSelectedNode)

        self.addSeedBtn = self.createMenuItem("Add Seed", self,
                statusTip="Prompt a browser to load a seed in the software",
                triggered=self.addRoot)
        self.loadBtn = self.createMenuItem("Load", self,
                shortcut=QtGui.QKeySequence("Ctrl+O"),
                statusTip="Open in the explorer the path of the selected node",
                triggered=self.load)
        self.saveBtn = self.createMenuItem("Save", self,
                shortcut=QtGui.QKeySequence("Ctrl+S"),
                statusTip="Open in the explorer the path of the selected node",
                triggered=self.save)
        self.saveAsBtn = self.createMenuItem("Save As", self,
                shortcut=QtGui.QKeySequence("Ctrl+Shift+S"),
                statusTip="Open in the explorer the path of the selected node",
                triggered=self.saveAs)        
        self.closeBtn = self.createMenuItem("Close", self,
                shortcut=QtGui.QKeySequence("Ctrl+Q"),
                statusTip="Close the window",
                triggered=sys.exit)
    

    def createMenuItem(self, name, parent, shortcut=None, statusTip=None, triggered=None):
        """Create a QAction item and create also a QShortcut if needed.
        This function is here to don't have to create a shortcut item by hand
        when we register a QAction button.

        Args:
            name (str): Name of the button
            parent (QWidget): The parent widget of the button
            shortcut (QKeySequence, optional): The KeySequence to use to trigger the shortcut. Defaults to None.
            statusTip (str, optional): The tooltip of the button. Defaults to None.
            triggered (class method, optional): THe method to call when the button is clicked. Defaults to None.

        Returns:
            QtWidgets.QAction: The create button
        """
        actionButton = QtWidgets.QAction(name, parent,
                                        shortcut=shortcut,
                                        statusTip=statusTip,
                                        triggered=triggered)
        if shortcut:
            QtWidgets.QShortcut(shortcut, parent, triggered)
        
        return actionButton

    def addRoot(self, path=None):
        if path is None:
            path = QtWidgets.QFileDialog.getExistingDirectory()
        if not os.path.exists(path):
            return 
        root_node = self.createNode(nodalItems.RootNode, args=[path, self.colors[len(self._rootsList)%len(self.colors)]])
        self._rootsList.append(root_node)
        return root_node

    def clear(self):
        self._scene.clear()
        self._rootsList = []

    def connectNodes(self, src_node, dst_node):
        connectionItem = self.createNode(nodalItems.ConnectionPath, args=[src_node, dst_node])
        p1 = src_node._outputKnob
        p2 = dst_node._inputKnob
        self._connectionsItems.append(connectionItem)
        src_node.addChildren(dst_node)
        return connectionItem

    def createNode(self, classe, pos=None, args=[]):
        new_node = classe(*args)
        if pos is not None:
            new_node.setPos(pos)
        self._scene.addItem(new_node)

        return new_node  

    def openExplorerSelectedNode(self):
        os.startfile(self.scene().selectedItems()[0]._path)

    def _getSelectionBoundingbox(self):
        """
        Return the bounding box of the selection.
        """
        bbx_min = None
        bbx_max = None
        bby_min = None
        bby_max = None
        bbw = 0
        bbh = 0
        for item in self.scene().selectedItems():
            pos = item.scenePos()
            x = pos.x()
            y = pos.y()
            w = x + item.boundingRect().width()
            h = y + item.boundingRect().height()

            # bbx min
            if bbx_min is None:
                bbx_min = x
            elif x < bbx_min:
                bbx_min = x
            # end if

            # bbx max
            if bbx_max is None:
                bbx_max = w
            elif w > bbx_max:
                bbx_max = w
            # end if

            # bby min
            if bby_min is None:
                bby_min = y
            elif y < bby_min:
                bby_min = y
            # end if

            # bby max
            if bby_max is None:
                bby_max = h
            elif h > bby_max:
                bby_max = h
            # end if
        # end if
        bbw = bbx_max - bbx_min
        bbh = bby_max - bby_min
        return QtCore.QRectF(QtCore.QRect(bbx_min, bby_min, bbw, bbh))

    def about(self):
        pass

    def help(self):
        pass

    def settings(self):
        pass

    def load(self, file=None):
        if file is None:
            file = QtWidgets.QFileDialog.getOpenFileName(filter="Browser Files (*.browser)")
            if not file[0]:
                return
            file = file[0]
                
        if not os.path.exists(file) or not file.endswith(".browser"):
            print("ERROR: Unable to load this project")
            return

        self.clear()
        
        content = json.load(open(file, 'r'))
        for nodeData in content["nodes"]:
            node = self.addRoot(nodeData["_path"])
            node.load(nodeData)

        self.fitInView(QtCore.QRect(*content["scenePos"]), QtCore.Qt.KeepAspectRatio)

        self.setCurrentProject(file)
    
    def loadRecent(self):
        self.load(self.sender().text())
        
    def save(self):
        if self.currentProject is None:
            self.saveAs()
            return
        result = {"scenePos": None, "nodes":[]}
        for node in self._rootsList:
            result["nodes"].append(node.save())

        viewRect = self.mapToScene(self.rect()).boundingRect()
        
        
        result["scenePos"] = utils.rectToList(self.mapToScene(self.rect()).boundingRect())

        #TODO open a UI to pick the path of the 
        json.dump(result, open(self.currentProject, "w"), indent=4)
        # print(result)

    def saveAs(self):
        file = QtWidgets.QFileDialog.getSaveFileName(filter="Browser Files (*.browser)")
        if file[0]:
            self.setCurrentProject(file[0])
            self.save()

    def setCurrentProject(self, file):
        utils.settings.addRecentProject(file)
        self.currentProject = file

    # Override functions    
    def keyPressEvent(self,  event):
        """Override the mouse press event to allow the user to use shortcuts

        Args:
            event (QtCore.Event): Event sent by QT Framework
        """

        if event.key() == QtCore.Qt.Key_A:
            itemsArea = self.scene().itemsBoundingRect()
            self.fitInView(itemsArea, QtCore.Qt.KeepAspectRatio)

        elif event.key() == QtCore.Qt.Key_F:  
            itemsArea = self._getSelectionBoundingbox()
            center = QtCore.QPoint((itemsArea.x() + itemsArea.width())/2, (itemsArea.y() + itemsArea.height())/2)
            self.centerOn(center)
            # get selected ite
            # self.fitInView(itemsArea, QtCore.Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        """Override the mouse wheel to allow the user to zoom in the scene

        Args:
            event (QtCore.Event): Event sent by QT Framework
        """
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

        inFactor = 1.15
        outFactor = 1 / inFactor

        if event.delta() > 0:
            zoomFactor = inFactor
        else:
            zoomFactor = outFactor

        self.scale(zoomFactor, zoomFactor)

    def mousePressEvent(self, event):
        """Override the mouse Press event.
        Used to simulate the left press when we are dragging the scene with midleClick button

        Args:
            event (QtCore.Event): Event sent by QT Framework
        """
        if event.button() == QtCore.Qt.MidButton:
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

            self.viewport().setCursor(QtCore.Qt.ClosedHandCursor)  
            self.original_event = event
            handmade_event = QtGui.QMouseEvent(
                QtCore.QEvent.MouseButtonPress,
                QtCore.QPoint(event.pos()),
                QtCore.Qt.LeftButton,event.buttons(),
                QtCore.Qt.KeyboardModifiers()
            )

            self.mousePressEvent(handmade_event)

        super(View, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Override the mouse Release event.
        Used to simulate the left release when we are dragging the scene with midleClick button

        Args:
            event (QtCore.Event): Event sent by QT Framework
        """
        if self.menu is not None:
            self.menu.hide()
        if event.button() == QtCore.Qt.MidButton:            
            #for changing back to Qt.OpenHandCursor
            self.viewport().setCursor(QtCore.Qt.OpenHandCursor)
            handmade_event = QtGui.QMouseEvent(
                QtCore.QEvent.MouseButtonRelease,
                QtCore.QPoint(event.pos()),
                QtCore.Qt.LeftButton,event.buttons(),
                QtCore.Qt.KeyboardModifiers()            
            )

            self.mouseReleaseEvent(handmade_event)

        super(View, self).mouseReleaseEvent(event)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)

    def contextMenuEvent(self, event):
        """Override the context menu to pop up the menu we want

        Args:
            event (QtCore.Event): Event sent by QT Framework
        """
        menu = QtWidgets.QMenu(self)

        if len(self.scene().selectedItems()) > 0:
            menu.addAction(self.openExplorerSelectedNodeBtn)
            menu.addSeparator()
        
        menu.addAction(self.helpBtn)
        menu.addAction(self.aboutBtn)
        menu.addAction(self.settingsBtn)
        menu.addSeparator()
        menu.addAction(self.addSeedBtn)
        saveMenu = menu.addMenu("Save")
        saveMenu.addAction(self.saveBtn)
        saveMenu.addAction(self.saveAsBtn)
        loadMenu = menu.addMenu("Load")
        loadMenu.addAction(self.loadBtn)
        loadRecentMenu = loadMenu.addMenu("Load Recent")
        for file in utils.settings.recentProjects:
            loadRecentMenu.addAction(self.createMenuItem(file, self, triggered=self.loadRecent))
        # TODO: list all the recent loaded project  
        menu.addSeparator()
        menu.addAction(self.closeBtn)

        # Could fix the issue of semi transparent menu
        menu.show()
        menu.move(event.globalPos())
        # menu.exec_(event.globalPos())

    def show(self):
        """Override the show function to show the HUD when the application show up
        """
        super(View, self).show()
        if hasattr(self, "hud"):
            self.hud.show()
        
    def resizeEvent(self, event):
        """Override the resize function to send the resize to the HUD widget

        Args:
            event (QtCore.QEvent): The event sent by QT Framework
        """
        super(View, self).resizeEvent(event)
        if hasattr(self, "hud"):
            self.hud.resize(event.size().width(), event.size().height())



class Scene(QtWidgets.QGraphicsScene):
    def __init__(self, parent = None):
        super(Scene, self).__init__(parent)

    def drawBackground(self, painter = QtGui.QPainter(), rect = None):
        #view_rect = self.parent().mapToScene(self.parent().rect()).boundingRect()
        rect = self.sceneRect()
        darkLines = QtGui.QPen(QtGui.QColor(utils.getCssValue("backgroundGrid", "bigGrid-color")), 1, QtCore.Qt.SolidLine)
        lightLines = QtGui.QPen(QtGui.QColor(utils.getCssValue("backgroundGrid", "smallGrid-color")), 1, QtCore.Qt.SolidLine)
        painter.fillRect(rect, QtGui.QColor(utils.getCssValue("backgroundGrid", "background-color")))

        painter.setPen(lightLines)
        self.drawGrid(painter, rect, 15)

        painter.setPen(darkLines)
        self.drawGrid(painter, rect, 150)
        # self.update()

    def drawGrid(self, painter, rect, padding):
        y = rect.y()
        x = rect.x()
        while y <= rect.height():
            line = QtCore.QLineF(rect.x(), y, rect.width(), y)
            painter.drawLine(line)
            y += padding
        while x <= rect.width():
            line = QtCore.QLineF(x, rect.y(), x, rect.height())
            painter.drawLine(line)
            x += padding