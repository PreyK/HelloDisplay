from PyQt5 import QtWidgets, uic
import sys

#test2

import PyQt5.Qt
from PyQt5 import QtWidgets
from PyQt5 import Qt
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QMimeData
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene
from PyQt5.QtGui import QDrag, QPalette, QColor, QMouseEvent, QPaintEvent
import sys
import time

# EDID and RANDR stuff
# TODO: add edid as standalone module like RANDR
from PyQt5.uic.properties import QtCore

import randr
import pyedid.helpers
import pyedid
from pyedid import Registry


class DisplayWindow(QtWidgets.QMainWindow):
    DisplayWidgets = []
    def __init__(self):
        super(DisplayWindow, self).__init__()
        uic.loadUi('layout.ui', self)
        global MainWindow
        self.setAcceptDrops(True)
        self.applyButton.clicked.connect(self.applySettings)

        self.edidRegistry = Registry.from_csv('edid.csv')
        MainWindow = self

        self.initDisplayWidgets()

        self.show()
        self.selectPrimaryScreen()
        randr.ApplyEvent = self.requeryRandr


    def requeryRandr(self):
        self.close()
        self.__init__()

    def selectPrimaryScreen(self):
        for widget in self.DisplayWidgets:
            if(widget.randr_screen.primary):
                self.SelectScreen(widget)


    def initDisplayWidgets(self):
        print("INIDWIDGETS")
        for display in randr.connected_screens():
            if display.is_enabled():
                dv = self.AddScreenWidget(display)
                self.DisplayWidgets.append(dv)

    def resolutionChanged(self):
        print(self.resolutionBox.currentIndex())
        self.selectedDisplayWidget.setResolution(self.resolutionBox.currentIndex())

    def rotationChanged(self):
        print("rotation changed")
        print(self.RotationBox.currentIndex())
        self.selectedDisplayWidget.setRotation(self.RotationBox.currentIndex())

    def primaryChanged(self):
        print("primary display changed")
        self.selectedDisplayWidget.setPrimary(self.primaryDisplayCheckbox.isChecked())

    def applySettings(self):
        screens = []
        for dw in self.DisplayWidgets:
            screens.append(dw.randr_screen)
        randr.applyAllScreens(screens)


    def AddScreenWidget(self, screen):
        v = DisplayWidget()
        v.setParent(self.screenParent)
        v.SetScreen(screen)
        return v

    def SelectScreen(self, displayWidget):
        if self.resolutionBox.receivers(self.resolutionBox.currentIndexChanged) > 0:
            self.resolutionBox.currentIndexChanged.disconnect()

        if self.RotationBox.receivers(self.RotationBox.currentIndexChanged) > 0:
            self.RotationBox.currentIndexChanged.disconnect()

        if self.primaryDisplayCheckbox.receivers(self.primaryDisplayCheckbox.stateChanged) >0:
            self.primaryDisplayCheckbox.stateChanged.disconnect()


        self.selectedDisplayLabel.setText(displayWidget.displayName)
        self.selectedDisplayLabel.updateGeometry()
        self.RotationBox.clear()
        self.resolutionBox.clear()

        self.selectedDisplayWidget = displayWidget

        for mode in displayWidget.randr_screen.supported_modes:
            if mode:
                self.resolutionBox.addItem(randr.formatResolutionToString(mode.resolution()))



        current_resolution_index = 0

        if(displayWidget.randr_screen.get_current_resolution()):
            #this has unapplied settings, display it!
            current_resolution = randr.formatResolutionToString(displayWidget.randr_screen.get_current_resolution())
            current_resolution_index = self.resolutionBox.findText(current_resolution)
        else:
            current_mode = displayWidget.randr_screen.get_current_mode()
            current_resolution = randr.formatResolutionToString(current_mode.resolution())
            current_resolution_index = self.resolutionBox.findText(current_resolution)
            #self.resolutionBox.setCurrentIndex(current_resolution_index)


        self.resolutionBox.setCurrentIndex(current_resolution_index)
        self.resolutionBox.currentIndexChanged.connect(self.resolutionChanged)


        for i in range(1, 5):
            self.RotationBox.addItem(randr.rot_to_str(i))



        current_rot = randr.rot_to_str(displayWidget.randr_screen.rotation);
        current_rot_index = self.RotationBox.findText(current_rot)
        self.RotationBox.setCurrentIndex(current_rot_index)
        self.primaryDisplayCheckbox.setCheckState(displayWidget.randr_screen.primary * 2)

        self.RotationBox.currentIndexChanged.connect(self.rotationChanged)
        self.primaryDisplayCheckbox.stateChanged.connect(self.primaryChanged)

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        event.accept()
        for widget in self.DisplayWidgets:
            if widget.isDragged:
                widget.move(event.pos() - widget.initialPos)
                widget.isDragged = False
                widget.setDisplayPosition()

    def dragMoveEvent(self, event):
        event.accept()
        for widget in self.DisplayWidgets:
            if widget.isDragged:
                widget.move(event.pos() - widget.initialPos)


class DisplayWidget(QtWidgets.QWidget):
    def __init__(self):
        super(DisplayWidget, self).__init__()
        self.isChanged = False
        self.setGeometry(0, 0, 100, 100)
        self.manufacturerLabel = QtWidgets.QLabel(self)
        self.manufacturerLabel.setText("manufacturer")

        self.connectorLabel = QtWidgets.QLabel(self)
        self.connectorLabel.setText("connector")
        self.connectorLabel.move(0, 15)

        self.pal = QPalette()
        self.pal.setColor(QPalette.Background, QColor(255, 255, 255))
        self.setAutoFillBackground(True)
        self.setPalette(self.pal)
        self.setAcceptDrops(True)
        self.show()
        self.isDragged = False

    def applySettings(self):
        #if self.isChanged:
        self.randr_screen.apply_settings()

    def setResolution(self, resolutionIndex):
        self.wantedResolution = self.randr_screen.supported_modes[resolutionIndex]
        resw = self.wantedResolution.width
        resh = self.wantedResolution.height
        self.randr_screen.set_resolution(self.randr_screen.supported_modes[resolutionIndex].resolution())

    def setRotation(self, rotationIndex):
        print("SETROT")
        self.randr_screen.rotate(rotationIndex+1)

    def setRefreshRate(self, refreshRate):
        self.wantedRefreshRate = refreshRate

    def setPrimary(self, isPrimary):
        print(isPrimary)
        self.randr_screen.set_as_primary(isPrimary)

    def SetScreen(self, screen):
        mode = screen.get_current_mode()
        self.randr_screen = screen
        #print(screen.get_rotation())
        centerPoint = MainWindow.screenParent.geometry().center()
        #print(centerPoint)
        if (screen.rotation == 1 or screen.rotation == 3):
            self.setGeometry(centerPoint.x() + self.randr_screen.px / 15, self.randr_screen.py / 15, mode.width / 15,
                             mode.height / 15)
        else:
            self.setGeometry(centerPoint.x() + self.randr_screen.px / 15, self.randr_screen.py / 15, mode.height / 15,
                             mode.width / 15)

        # normal = 1
        # right = 4
        # inverted = 3
        # left = 2
        self.edid = pyedid.parse_edid(randr.get_edid_for_output(self.randr_screen.name), MainWindow.edidRegistry)

        self.displayName = self.edid.manufacturer.split(" ")[0] + " " + self.edid.name;
        self.manufacturerLabel.setText(self.edid.manufacturer.split(" ")[0] + " " + self.edid.name)
        self.connectorLabel.setText(screen.name)
        self.manufacturerLabel.adjustSize()
        self.connectorLabel.adjustSize()


    def setDisplayPosition(self):
        print("setpos")
        centerPoint = MainWindow.screenParent.geometry().center()
#        print(self.geometry().x() + self.mode.width)
 #       print(self.screen.px)
        # self.screen.px = 0

    def mousePressEvent(self, event: QMouseEvent):
        MainWindow.SelectScreen(self)

    def mouseMoveEvent(self, event: QMouseEvent):
        if (event.buttons() == Qt.LeftButton):
            self.initialPos = event.pos()
            self.isDragged = True
            mimeData = QMimeData()
            drag = QDrag(self)
            drag.setMimeData(mimeData)
            dropAction = drag.exec_(Qt.MoveAction)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = DisplayWindow()
    app.exec_()


main()
