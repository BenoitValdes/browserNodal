from Qt import QtWidgets, QtGui, QtCore
import utils, os, random

class BaseNode(QtWidgets.QGraphicsItem):
    def __init__(self, path, bgColor="#4f7526", textColor="#ffffff"):
        self._path = path # The path that reprent this node
        self._inputKnob = QtCore.QPoint() # Position of the input knob
        self._outputKnob = QtCore.QPoint() # Position of the output knob
        self._connections = [] # List of the connections items (the path that link 2 nodes)
        self._childrenList = [] # List of the childrens of this node
        self._parent = None # The parent node
        self._rect = None # Represent the rect (the geometry) of this node
        self._sidePadding = 10 # Used to have a space each side of the name
        self._childrenVisibles = False # The status of the visibilit of the children
        self._seekChildren = True # If True, when double click on node, the script will look of the subfolder of this node
        self._reverted = False # Check if the knob input/output have been reverted

        super(BaseNode, self).__init__()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges, True)
        
        self.bgColor = bgColor # Background Color
        self.textColor = textColor # Text color
        self.nodeName = os.path.basename(self._path)

        self.colors = []#"#e74f4A", "#F5544E", "#CF4742", "#A83A36", "#692421"]
        baseColor = QtGui.QColor(self.bgColor).getHsv()
        for i in range(25, 101, 10):
            hsv = list(baseColor)
            hsv[2] = int(i*2.5)
            variation = QtGui.QColor().fromHsv(*hsv)
            self.colors.append(variation.name(QtGui.QColor.HexRgb))

        # Pen.
        self._pen = QtGui.QPen(QtCore.Qt.NoPen)

        self._selPen = QtGui.QPen(QtCore.Qt.NoPen)
        self._selPen.setStyle(QtCore.Qt.SolidLine)
        self._selPen.setWidth(int(utils.getCssValue("node", "border-width")))
        self._selPen.setColor(utils.getCssValue("node", "border-color"))

        self.defineNodeRect()
        self.setKnobsPosition()

        # self.setCursor(QtCore.Qt.OpenHandCursor)

    def save(self):        
        result = dict()
        for attr in ["_path", "bgColor", "textColor", "_childrenVisibles", "_seekChildren", "_reverted"]:
            result[attr] = getattr(self, attr)

        result["_rect"] = [self._rect.x(), self._rect.y(), self._rect.width(), self._rect.height()]

        result["pos"] = self.pos().toTuple()
        result["children"] = []
        for child in self._childrenList:
            result["children"].append(child.save())
        return result

    def load(self, data):
        for attr in ["_path", "bgColor", "textColor", "_childrenVisibles", "_seekChildren", "_reverted"]:
            if attr in data:
                setattr(self, attr, data[attr])

        self._rect = QtCore.QRect(*data["_rect"])
        self.setPos(*data["pos"])
        if self._reverted:
            self._reverted = False
            self.invertKnobPositions(False)

        for childData in data["children"]:
            new_node = self.scene().parent().createNode(BranchNode, args=[childData["_path"]])
            new_node.load(childData)
            self.scene().parent().connectNodes(self, new_node)
        
        self.updateChildrenVisibility()

    def invertKnobPositions(self, moveNode=True, affectChildren = True):
        # get delta with dad and apply it again       
        if moveNode: 
            parentPos = self._parent.getOutputPos()
            pos = self.getInputPos()
            deltaPos = pos-parentPos
            deltaPos.setX(deltaPos.x()/2.0)

        _in = self._inputKnob
        _out = self._outputKnob
        self._inputKnob = _out
        self._outputKnob = _in
        self._reverted = not self._reverted
        if moveNode:
            deltaInPos = self.getInputPos() - self.pos()
            newPos = parentPos-deltaPos-deltaInPos
            newPos.setY(self.pos().y())
            self.setPos(newPos)
            
        for child in self._childrenList:
            child.invertKnobPositions()
        self.updateConnections()

    def defineNodeRect(self, force=None):
        if isinstance(force, QtCore.QRect):
            self._rect = force

        return self._rect

    def setKnobsPosition(self):
        pass

    def addChildren(self, node):
        if not node in self._childrenList:
            self._childrenList.append(node)
            node._parent = self
            
        self.updateChildrenVisibility()

    def itemChange(self, change, value):
        # Revert the knobs position to avoid weird stuff when the node is on the left side of the Root
        if isinstance(self._parent, RootNode):
            if self.getCenterPos().x() < self._parent.getCenterPos().x() and not self._reverted:
                self.invertKnobPositions(False)

            elif self.getCenterPos().x() > self._parent.getCenterPos().x() and self._reverted:
                self.invertKnobPositions(False)
        if self.scene():
            if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemPositionChange:
                # Update the position of the children
                delta = QtCore.QPointF(value) - self.pos()
                if QtWidgets.QApplication.keyboardModifiers() != QtCore.Qt.AltModifier:
                    for node in self._childrenList:
                        node.moveBy(delta.x(), delta.y())

                # TODO: unselect the node after the move?
                
            # Update the line that connect the nodes
            self.updateConnections()
        return super(BaseNode, self).itemChange(change, value)

    def updateConnections(self):
        for connection in self._connections:
            connection.updatePath()
        pass

    def getInputPos(self):
        nodePos = self.pos()
        return nodePos + self._inputKnob

    def getOutputPos(self):
        nodePos = self.pos()
        return nodePos + self._outputKnob

    def getCenterPos(self):
        rect = self.boundingRect()
        return QtCore.QPointF(self.pos().x() + rect.width()/2.0, self.pos().y() + rect.height()/2.0)

    def boundingRect(self):
        return QtCore.QRectF(self._rect)

    def paint(self, painter, option, widget):
        painter.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing, True)

        painter.setPen(self._pen)

        # Draw the background
        self.paintBackground(painter)

        # Draw the name of the node
        self.paintText(painter)
        
        # Draw the selection of the node
        # Edit the pen when the node is selected  
        if self.isSelected():
            painter.setPen(self._selPen)
            painter.setBrush(QtGui.QColor(255, 255, 255, 0))
            self.paintSelection(painter)

    def paintBackground(self, painter):
        pass

    def paintText(self, painter):
        painter.setPen(QtGui.QColor(self.textColor))
        painter.drawText(self._rect, QtCore.Qt.AlignCenter, self.nodeName)

    def paintSelection(self, painter):
        painter.drawRoundedRect(self.boundingRect(), 3, 3)

    def updateChildrenVisibility(self):
        for node in self.getChildrens(True):
            value = node._parent._childrenVisibles
            if self._childrenVisibles == False:
                value = False
            node.setVisible(value)

    def getChildrens(self, recursive=False):
        result = []
        for node in self._childrenList:
            result.append(node)
            if recursive:
                result += node.getChildrens(recursive)

        return result

    def _fillData(self):
        color = self.bgColor
        counter = 0
        for folder in os.listdir(self._path):
            full_path = os.path.join(self._path, folder)
            if os.path.isdir(full_path):                
                if isinstance(self, RootNode):
                    color = self.colors[random.randint(0, len(self.colors)-1)]

                new_node = self.scene().parent().createNode(BranchNode, args=[full_path, color])
                new_node.setPos(self.pos())
                new_node.moveBy(self._rect.width() + 20, 20*counter)

                self.scene().parent().connectNodes(self, new_node)
                
                if self._reverted is True:
                    new_node.invertKnobPositions()
                counter += 1

        self._seekChildren = False

    def setVisible(self, visible=True):
        super(BaseNode, self).setVisible(visible)
        for conn in self._connections:
            conn.setVisible(visible)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            view = self.scene().parent()
            view.rightClickNode = self
        super(BaseNode, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.updateConnections()
        super(BaseNode, self).mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        super(BaseNode, self).mouseDoubleClickEvent(event)
        if self._seekChildren is True:
            self._fillData()
        self._childrenVisibles = not self._childrenVisibles
        self.updateChildrenVisibility()


class ConnectionPath(QtWidgets.QGraphicsPathItem):

    def __init__(self, srcNode, dstNode):
        super(ConnectionPath, self).__init__()
        self._waveFactor = 5
        self._srcNode = srcNode   
        self._dstNode = dstNode
        if not self in self._srcNode._connections:
            self._srcNode._connections.append(self)
        if not self in self._dstNode._connections:
            self._dstNode._connections.append(self)
        self.setZValue(-1)
        self.updatePath()


    def paint(self, painter, option, widget):
        color = QtGui.QColor(self._dstNode.bgColor)
        p1 = self.path().pointAtPercent(0)
        p2 = self.path().pointAtPercent(1)

        painter.setRenderHint(painter.Antialiasing, True)

        painter.setPen(QtGui.QPen(color, 3, QtCore.Qt.SolidLine))
        painter.drawPath(self.path())

    def updatePath(self):
        p1 = self._srcNode.getOutputPos()
        if isinstance(self._srcNode, RootNode):
            p1 = self._srcNode.getOutputPos(self._dstNode)
        p2 = self._dstNode.getInputPos()
        p3 = self._dstNode.getOutputPos()

        path = QtGui.QPainterPath()
        dx = (p2.x() - p1.x()) * 0.5
        dy = p2.y() - p1.y()
        ctrl1 = QtCore.QPointF(p1.x() + dx, p1.y() + dy * 0)
        ctrl2 = QtCore.QPointF(p1.x() + dx, p1.y() + dy * 1)

        if isinstance(self._srcNode, RootNode):
            ctrl1 = ctrl2

        path.moveTo(p1)
        path.cubicTo(ctrl1, ctrl2, p2)
        # path.lineTo(p3)
        self.setPath(path)


class RootNode(BaseNode):
    def __init__(self, name="Root", bgColor="#297286"):
        super(RootNode, self).__init__(name, bgColor)
        self._borderSize = self._rect.width()/10
        self._r = self._rect.width()/2

    def defineNodeRect(self):
        return super(RootNode, self).defineNodeRect(QtCore.QRect(0, 0, 80, 80))


    def setKnobsPosition(self):
        pos = QtCore.QPoint((self._rect.width() - self._rect.x())/2, (self._rect.height() - self._rect.y())/2)
        self._inputKnob = pos
        self._outputKnob = pos

    def paintBackground(self, painter):
        center = self.getOutputPos() - self.pos()
        bgColor = QtGui.QColor(self.bgColor)
        painter.setBrush(QtGui.QBrush(bgColor))
        if self.isSelected():
            painter.setBrush(QtGui.QBrush(bgColor.lighter()))

        for children in self.getChildrens():
            if self._childrenVisibles is True:
                painter.drawEllipse(self.getOutputPos(children) - self.pos(), self._borderSize, self._borderSize)

        painter.drawEllipse(center, self._r, self._r)
        painter.setBrush(QtGui.QBrush(bgColor.darker()))
        painter.drawEllipse(center, self._r-self._borderSize, self._r-self._borderSize)

    def getOutputPos(self, node=None):
        standard_pos = super(RootNode, self).getOutputPos()
        if node is None:
            return standard_pos
            
        dest_point = node.getInputPos()

        vec = utils.Vector(dest_point.x()-standard_pos.x(), dest_point.y()-standard_pos.y())
        vec = utils.Vector(standard_pos.x(), standard_pos.y()) + vec.normalize()*self._r
        return QtCore.QPointF(*vec.values)

    def paintText(self, painter):
        font = QtGui.QFont()
        font.setPixelSize(14)  
        painter.setFont(font)
        super(RootNode, self).paintText(painter)

    def paintSelection(self, painter):
        return
        painter.drawEllipse(self._rect)


class BranchNode(BaseNode):
    def __init__(self, name="Branch", bgColor="#297286"):
        super(BranchNode, self).__init__(name, bgColor)
        self._height = 3


    def defineNodeRect(self):
        label = QtWidgets.QLabel(self.nodeName)
        self._rect = QtCore.QRect(0,0,100,20)
        self._rect.setWidth(label.sizeHint().width() + 2*self._sidePadding)

    def setKnobsPosition(self):
        input_pos = QtCore.QPoint(self._rect.x(), self._rect.height()/2.0)
        output_pos = QtCore.QPoint(self._rect.width(), self._rect.height()/2.0)
        self._inputKnob = input_pos
        self._outputKnob = output_pos
