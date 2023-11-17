# -*- coding: utf-8 -*-

from re import findall

from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget
from PyQt5.QtGui import QPen, QBitmap, QPainter, QBrush
from PyQt5.QtCore import QRect, QPoint, Qt


from config.settin import settinRead,settinSet


class WScreenShot(QWidget):

    def __init__(self, chooseRange, parent=None):

        super(WScreenShot, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # | Qt.Tool)
        self.setWindowState(Qt.WindowFullScreen | Qt.WindowActive)
        self.setStyleSheet('''background-color:black; ''')
        self.setWindowOpacity(0.6)
        desktopRect = QDesktopWidget().screenGeometry()
        self.setGeometry(desktopRect)
        self.setCursor(Qt.CrossCursor)
        self.blackMask = QBitmap(desktopRect.size())
        self.blackMask.fill(Qt.black)
        self.mask = self.blackMask.copy()
        self.isDrawing = False
        self.startPoint = QPoint()
        self.endPoint = QPoint()
        self.chooseRange = chooseRange

    def paintEvent(self, event):

        try:
            if self.isDrawing:
                self.mask = self.blackMask.copy()
                pp = QPainter(self.mask)
                pen = QPen()
                pen.setStyle(Qt.NoPen)
                pp.setPen(pen)
                brush = QBrush(Qt.white)
                pp.setBrush(brush)
                pp.drawRect(QRect(self.startPoint, self.endPoint))
                self.setMask(QBitmap(self.mask))
        except Exception as ex:
            print("错误信息："+str(ex))

    def mousePressEvent(self, event):

        try:
            if event.button() == Qt.LeftButton:
                self.startPoint = event.pos()
                self.endPoint = self.startPoint
                self.isDrawing = True
        except Exception as ex:
            print("错误信息："+str(ex))

    def mouseMoveEvent(self, event):

        try:
            if self.isDrawing:
                self.endPoint = event.pos()
                self.update()
        except Exception as ex:
            print("错误信息："+str(ex))

    def getRange(self):

        start = findall(r'(\d+), (\d+)', str(self.startPoint))[0]
        end = findall(r'\d+, \d+', str(self.endPoint))[0]
        end = end.split(', ')

        X1 = int(start[0])
        Y1 = int(start[1])
        X2 = int(end[0])
        Y2 = int(end[1])

        if X1 > X2:
            tmp = X1
            X1 = X2
            X2 = tmp

        if Y1 > Y2:
            tmp = Y1
            Y1 = Y2
            Y2 = tmp

        data = settinRead()
        data["range"]["X1"] = X1
        data["range"]["Y1"] = Y1
        data["range"]["X2"] = X2
        data["range"]["Y2"] = Y2
        settinSet(data)

        self.chooseRange.setGeometry(X1, Y1, X2 - X1, Y2 - Y1)
        self.chooseRange.Label.setGeometry(0, 0, X2 - X1, Y2 - Y1)
        self.chooseRange.show()
 
    def mouseReleaseEvent(self, event):

        try:
            if event.button() == Qt.LeftButton:
                self.endPoint = event.pos()
                self.getRange()

                self.close()

        except Exception as ex:
            print("错误信息："+str(ex))

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Escape:
            self.close()
