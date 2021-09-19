import threading

import PyQt5.Qt
from PyQt5 import QtWidgets
from PyQt5 import Qt
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QMimeData
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene
from PyQt5.QtGui import QDrag, QPalette, QColor, QMouseEvent, QPaintEvent
import sys

import pyedid.helpers
import pyedid
from pyedid import Registry
import randr

class DisplayWindow(QMainWindow):
    DisplayWidgets = []
    def __init__(self):
        super(DisplayWindow, self).__init__()
        self.setGeometry(200, 200, 300, 300)
        self.setWindowTitle("Display")
        self.setAcceptDrops(True)
        global MainWindow
        MainWindow = self
        self.edidRegistry = Registry.from_csv('edid.csv')
        self.InitUi()
        
    def InitUi(self):

        for display in randr.connected_screens():
            if display.is_enabled():
                dv = self.AddScreenWidget(display)
                self.DisplayWidgets.append(dv)
        self.selectedDisplayName = QtWidgets.QLabel(self)
        self.selectedDisplayName.move(100, 150)
        self.selectedDisplayName.setText("Display")
        self.selectedresolutionSelector = QtWidgets.QComboBox(self)
        self.selectedresolutionSelector.move(100, 170)
        self.primaryDisplayCheckbox = QtWidgets.QCheckBox("Primary Display",self)
        self.primaryDisplayCheckbox.move(100, 190)
        self.primaryDisplayCheckbox.updateGeometry()

        #self.scene = QGraphicsScene(self)
        #prox = self.scene.addWidget(self.DisplayWidgets[0])
        #prox.setRotation(45)

        #label = QtWidgets.QLabel()
        #label.setText("ASDASD")
#
        #graphicsview = QtWidgets.QGraphicsView()
        #scene = QtWidgets.QGraphicsScene(graphicsview)
        #graphicsview.setScene(scene)
#
        #proxy = QtWidgets.QGraphicsProxyWidget()
        #proxy.setWidget(label)
        #proxy.setTransformOriginPoint(proxy.boundingRect().center())
        #scene.addItem(proxy)
        #proxy.setRotation(45)
        
        self.SelectScreen(self.DisplayWidgets[0])
        self.applyButton = QtWidgets.QPushButton(self)
        self.applyButton.setText("Apply")
        self.applyButton.move(0, 250)

    def AddScreenWidget(self, screen):
        v = DisplayWidget()
        v.setParent(self)
        v.SetScreen(screen)
        return v
    def SelectScreen(self, displayWidget):

        self.selectedDisplayName.setText(displayWidget.randr_screen.name)
        self.selectedDisplayName.updateGeometry()
        self.selectedresolutionSelector.clear()
        for asd in displayWidget.randr_screen.supported_modes:
            if(asd):
                self.selectedresolutionSelector.addItem(str(asd.resolution()))

    def dragEnterEvent(self, event):
        event.accept()
        #print("I AM DRAGGED")

    def dropEvent(self, event):
        event.accept()
        #print("I AM DROP")
        for widget in self.DisplayWidgets:
            if(widget.isDragged):
                widget.move(event.pos()-widget.initialPos)
                widget.isDragged = False
                
        
    def dragMoveEvent(self, event):
        event.accept()
        for widget in self.DisplayWidgets:
            if(widget.isDragged):
                widget.move(event.pos()-widget.initialPos)
                
        
        
class DisplayWidget(QtWidgets.QWidget):
    def __init__(self):
        super(DisplayWidget, self).__init__()
        self.setGeometry(0, 0, 100, 100)
        self.manufacturerLabel = QtWidgets.QLabel(self)
        self.manufacturerLabel.setText("manufacturer")

        self.nameLabel = QtWidgets.QLabel(self)
        self.nameLabel.setText("model")
        self.nameLabel.move(0, 15)

        self.connectorLabel = QtWidgets.QLabel(self)
        self.connectorLabel.setText("connector")
        self.connectorLabel.move(0, 15)

        self.pal = QPalette()
        self.pal.setColor(QPalette.Background, QColor(200, 200, 200))
        self.setAutoFillBackground(True)
        self.setPalette(self.pal)
        self.setAcceptDrops(True)
        self.show()
        self.isDragged=False
        
    def SetScreen(self, screen):


        # print(screen.rotation)
        #rint(screen.current)
        self.mode = screen.get_current_mode()
        self.screen = screen
        print(screen)
        print(self.mode)

        #set colorspace
        #xrandr --output HDMI-1 --set "Colorspace" "DCI-P3_RGB_D65"
        #get rot
        #xrandr --query --verbose | grep "LVDS-1"
        #self.SetRotation(45)

        print(screen.get_rotation())
        if(screen.rotation == 1 or screen.rotation == 3):
            self.setGeometry(self.screen.px/15, self.screen.py/15, self.mode.width/15, self.mode.height/15)
        else:
            self.setGeometry(self.screen.px/15, self.screen.py/15, self.mode.height / 15, self.mode.width / 15)

        #self.setGeometry(self.screen.px/15, self.screen.py/15)
        #normal = 1
        #right = 4
        #inverted = 3
        #left = 2
        self.edid = pyedid.parse_edid(randr.get_edid_for_output(self.screen.name), MainWindow.edidRegistry)

        #print(self.edid)

        self.manufacturerLabel.setText(self.edid.manufacturer.split(" ")[0]+" "+self.edid.name)
        self.nameLabel.setText("")
        self.connectorLabel.setText("Display Port")
        self.nameLabel.adjustSize()
        self.manufacturerLabel.adjustSize()
        self.connectorLabel.adjustSize()
    
    def mousePressEvent(self, event: QMouseEvent):
        MainWindow.SelectScreen(self)

    def mouseMoveEvent(self, event:QMouseEvent):
        if(event.buttons() == Qt.LeftButton):
            #print(333)
            self.initialPos = event.pos()
            self.isDragged = True
            mimeData = QMimeData()
            drag = QDrag(self)
            drag.setMimeData(mimeData)
            dropAction = drag.exec_(Qt.MoveAction)
        
def main():
    app = QApplication(sys.argv)
    win = DisplayWindow()
    win.show()
    sys.exit(app.exec_())
main()
