# -*- coding: utf-8 -*-


from PyQt5.QtWidgets import QMainWindow, QLabel, QStatusBar, QPushButton, QApplication
from PyQt5.QtGui import QFont, QCursor, QMouseEvent
from PyQt5.QtCore import Qt, QPoint, QRect

from config.settin import settinRead,settinSet

class Range(QMainWindow):

    def __init__(self, X1, Y1, X2, Y2):

        try:
            super(Range, self).__init__()
            self.setGeometry(X1, Y1, X2 - X1, Y2 - Y1)

            # 窗口无标题栏、窗口置顶、窗口透明
            self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
            self.setAttribute(Qt.WA_TranslucentBackground)

            self.Label = QLabel(self)
            self.Label.setObjectName("dragLabel")
            self.Label.setGeometry(0, 0, X2 - X1, Y2 - Y1)
            self.Label.setStyleSheet("border-width:1;\
                                  border:2px dashed #1E90FF;\
                                  background-color:rgba(62, 62, 62, 0.01)")

            # 此Label用于当鼠标进入界面时给出颜色反应
            self.dragLabel = QLabel(self)
            self.dragLabel.setObjectName("dragLabel")
            self.dragLabel.setGeometry(0, 0, 4000, 2000)

            self.Font = QFont()
            self.Font.setFamily("华康方圆体W7")
            self.Font.setPointSize(12)

            # 隐藏按钮
            self.Button = QPushButton(self)
            self.Button.setGeometry(QRect(X2 - X1 - 40, 0, 40, 30))
            self.Button.setStyleSheet("background-color:rgba(62, 62, 62, 0.3);"
                                      "color:#1E90FF")
            self.Button.setFont(self.Font)
            self.Button.setText("隐藏")
            self.Button.setCursor(QCursor(Qt.PointingHandCursor))
            self.Button.clicked.connect(self.close)
            self.Button.hide()

            # 右下角用于拉伸界面的控件
            self.statusbar = QStatusBar(self)
            self.setStatusBar(self.statusbar)
            self._startPos = None
        except Exception as ex:
            print("错误信息："+str(ex))

    # 鼠标移动事件
    def mouseMoveEvent(self, e: QMouseEvent):
        try:
            if self._startPos is not None:
                self._endPos = e.pos() - self._startPos
                self.move(self.pos() + self._endPos)
        except Exception as ex:
            print("错误信息："+str(ex))

    # 鼠标按下事件
    def mousePressEvent(self, e: QMouseEvent):
        try:
            if e.button() == Qt.LeftButton:
                self._isTracking = True
                self._startPos = QPoint(e.x(), e.y())
        except Exception as ex:
            print("错误信息："+str(ex))

    # 鼠标松开事件
    def mouseReleaseEvent(self, e: QMouseEvent):  
        try:
            rect = self.geometry()
            X1 = rect.left()
            Y1 = rect.top()
            X2 = rect.left() + rect.width()
            Y2 = rect.top() + rect.height()
            #存入json
            data = settinRead()
            data["range"]["X1"] = X1
            data["range"]["Y1"] = Y1
            data["range"]["X2"] = X2
            data["range"]["Y2"] = Y2
            settinSet(data)

            if e.button() == Qt.LeftButton:
                self._isTracking = False
                self._startPos = None
                self._endPos = None
        except Exception as ex:
            print("错误信息："+str(ex))

    # 鼠标进入控件事件
    def enterEvent(self, QEvent):
        try:
            rect = self.geometry()
            X1 = rect.left()
            Y1 = rect.top()
            X2 = rect.left() + rect.width()
            Y2 = rect.top() + rect.height()
            self.Button.setGeometry(QRect(X2 - X1 - 40, 0, 40, 30))
            self.Button.show()
            self.dragLabel.setStyleSheet("background-color:rgba(62, 62, 62, 0.3)")
        except Exception as ex:
            print("错误信息："+str(ex))

    # 鼠标离开控件事件
    def leaveEvent(self, QEvent):
        try:
            self.dragLabel.setStyleSheet("background-color:none")
            self.Label.setGeometry(0, 0, self.width(), self.height())
            self.Button.hide()

            rect = self.geometry()
            X1 = rect.left()
            Y1 = rect.top()
            X2 = rect.left() + rect.width()
            Y2 = rect.top() + rect.height()
            #存入json
            data = settinRead()
            data["range"]["X1"] = X1
            data["range"]["Y1"] = Y1
            data["range"]["X2"] = X2
            data["range"]["Y2"] = Y2
            settinSet(data)

        except Exception as ex:
            print("错误信息："+str(ex))



if __name__ == '__main__':
    import sys

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    win = Range(500, 500, 1000, 600)
    win.show()
    app.exec_()
