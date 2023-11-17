# -*- coding: utf-8 -*-

#https://fontawesome.com/search?q=fa&o=r 图标
from qtawesome import icon as qticon
from loguru import logger
from threading import Thread
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtCore import QObject, pyqtSignal, QSize, QRect, QPoint, Qt, QUrl
from PyQt5.QtGui import QIcon, QPixmap, QFont, QTextCharFormat, QPen, QColor, QCursor, QMouseEvent
from PyQt5.QtWidgets import QSystemTrayIcon, QLabel, QTextBrowser, QPushButton, QStatusBar, QFileDialog, QApplication, \
    QMainWindow
import os,sys
from config.settin import settinRead,settinSet,settinSetPlay

from src.screenRate import get_screen_rate
from src.switch import SwitchBtn
from src.range import WScreenShot
from src.chooseRange import Range

# from src.screenshot import image_cut

class displayThread(QObject):
    displaySignal = pyqtSignal(str,str)
    def __init__(self , text,showType):
        self.text = text
        self.showType = showType
        super(displayThread, self).__init__()
    def run(self):
        self.displaySignal.emit(self.text,self.showType)


class MainInterface(QMainWindow):
    def __init__(self, screen_scale_rate):
        super(MainInterface, self).__init__()
        self.data = settinRead()
        self.rate = screen_scale_rate  # 屏幕缩放比例
        self.base_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        #self.lockSign = data["lockSign"]  # False  True
        self.lockSign = "False"
        self.mode = "once"  #分为单次运行和循环 once loop
        self.runStatus = "OFF"
        self.horizontal = self.data["horizontal"] / 100. # 透明度

        if self.horizontal == 0:
            self.horizontal = 0.01 

        #logger.debug(self.horizontal)
        self.thread_state =0
        self.init_ui()
        self._padding = 5  # 设置边界宽度为5
        self._isTracking = False
        self._startPos = None
        self._endPos = None

        self.chooseRange = Range(self.data["range"]['X1'], self.data["range"]['Y1'], self.data["range"]['X2'],
                                self.data["range"]['Y2'])


    def init_ui(self):

        # 窗口尺寸
        self.resize(int(800 * self.rate), int(120 * self.rate))
        self.setMouseTracking(True)  # 设置widget鼠标跟踪

        # 窗口无标题栏、窗口置顶、窗口透明
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 窗口图标
        self.icon = QIcon()
        
        self.icon.addPixmap(QPixmap(os.path.join(self.base_path,"config/logo.ico")), QIcon.Normal, QIcon.On)
        self.setWindowIcon(self.icon)

        # 系统托盘
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.icon)
        self.tray.activated.connect(self.show)
        self.tray.show()

        # 工具栏标签
        self.titleLabel = QLabel(self)
        self.titleLabel.setGeometry(0, 0, int(800 * self.rate), int(30 * self.rate))
        self.titleLabel.setStyleSheet("background-color:rgba(62, 62, 62, 0.01)")

        self.Font = QFont()
        self.Font.setFamily("华康方圆体W7")
        self.Font.setPointSize(15)

        # 翻译框
        self.translateText = QTextBrowser(self)
        self.translateText.setGeometry(0, int(30 * self.rate), int(1500 * self.rate), int(90 * self.rate))
        self.translateText.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.translateText.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.translateText.setStyleSheet("border-width:0;\
                                          border-style:outset;\
                                          border-top:0px solid #e8f3f9;\
                                          color:white;\
                                          font-weight: bold;\
                                          background-color:rgba(62, 62, 62, %s)"
                                         % (self.horizontal))
        self.translateText.setFont(self.Font)

        # 翻译框加入描边文字
        self.format = QTextCharFormat()
        self.format.setTextOutline(QPen(QColor('#1E90FF'), 0.7, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.translateText.mergeCurrentCharFormat(self.format)
        self.translateText.append("这是示例界面")

        # 翻译框根据内容自适应大小
        self.document = self.translateText.document()
        self.document.contentsChanged.connect(self.textAreaChanged)

        # 此Label用于当鼠标进入界面时给出颜色反应
        self.dragLabel = QLabel(self)
        self.dragLabel.setObjectName("dragLabel")
        self.dragLabel.setGeometry(0, 0, int(4000 * self.rate), int(2000 * self.rate))

        # 截屏范围按钮
        self.RangeButton = QPushButton(qticon('fa.crop', color='white'), "", self)
        self.RangeButton.setIconSize(QSize(20, 20))
        self.RangeButton.setGeometry(QRect(int(193 * self.rate), int(5 * self.rate), int(20 * self.rate), int(20 * self.rate)))
        self.RangeButton.setToolTip('<b>选框 ScreenShot Range</b><br>框选要识别的区域')
        self.RangeButton.setStyleSheet("background-color:rgba(62, 62, 62, 0);")
        self.RangeButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.RangeButton.clicked.connect(self.rangeBt)
        #self.RangeButton.hide()

        # 运行按钮
        self.StartButton = QPushButton(qticon('fa.play', color='white'), "", self)
        self.StartButton.setIconSize(QSize(20, 20))
        self.StartButton.setGeometry(QRect(int(233 * self.rate), int(5 * self.rate), int(20 * self.rate), int(20 * self.rate)))
        self.StartButton.setToolTip('<b>开始 Recognize</b><br>点击开始/停止（手动）<br>开始/停止（自动）')
        self.StartButton.setStyleSheet("background: transparent")
        #self.StartButton.clicked.connect(self.startBt)
        self.StartButton.setCursor(QCursor(Qt.PointingHandCursor))
        #self.StartButton.hide()

        # 额外功能按钮
        # self.exFunctionButton = QPushButton(qticon('fa.star', color='white'), "", self)
        # self.exFunctionButton.setIconSize(QSize(20, 20))
        # self.exFunctionButton.setGeometry(QRect(int(273 * self.rate), int(5 * self.rate), int(20 * self.rate), int(20 * self.rate)))
        # self.exFunctionButton.setToolTip('如果开启了回答模式，则变成自己喷射机')
        # self.exFunctionButton.setStyleSheet("background: transparent")
        # self.exFunctionButton.setCursor(QCursor(Qt.PointingHandCursor))

        # self.diceButton = QPushButton(qticon('fa.comment',color='white'), "", self)
        # self.diceButton.setIconSize(QSize(20, 20))
        # self.diceButton.setGeometry(QRect(int(313 * self.rate), int(5 * self.rate), int(20 * self.rate), int(20 * self.rate)))
        # self.diceButton.setToolTip('随机垃圾话')
        # self.diceButton.setStyleSheet("background: transparent")
        # self.diceButton.setCursor(QCursor(Qt.PointingHandCursor))


        # 模式按钮
        self.switchBtn = SwitchBtn(self)
        self.switchBtn.setGeometry(int(393 * self.rate), int(5 * self.rate), int(50 * self.rate), int(20 * self.rate))
        self.switchBtn.setToolTip('<b>模式 Mode</b><br>A/B')
        self.switchBtn.checkedChanged.connect(self.modeChange)
        self.switchBtn.setCursor(QCursor(Qt.PointingHandCursor))
        #self.switchBtn.hide()
 
        # 设置按钮
        self.SettinButton = QPushButton(qticon('fa.cog', color='white'), "", self)
        self.SettinButton.setIconSize(QSize(20, 20))
        self.SettinButton.setGeometry(QRect(int(518 * self.rate), int(5 * self.rate), int(20 * self.rate), int(20 * self.rate)))
        self.SettinButton.setToolTip('<b>设置 Settin</b>')
        self.SettinButton.setStyleSheet("background-color:rgba(62, 62, 62, 0);")
        self.SettinButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.SettinButton.hide()

        #锁按钮
        self.LockButton = QPushButton(qticon('fa.lock', color='white'), "", self)
        self.LockButton.setIconSize(QSize(20, 20))
        self.LockButton.setGeometry(QRect(int(562 * self.rate), int(5 * self.rate), int(20 * self.rate), int(20 * self.rate)))
        self.LockButton.setToolTip('<b>锁定界面 Lock</b>')
        self.LockButton.setStyleSheet("background-color:rgba(62, 62, 62, 0);")
        self.LockButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.LockButton.clicked.connect(self.lock)
        #self.LockButton.hide()

        # 最小化按钮
        self.MinimizeButton = QPushButton(qticon('fa.minus', color='white'), "", self)
        self.MinimizeButton.setIconSize(QSize(20, 20))
        self.MinimizeButton.setGeometry(QRect(int(602 * self.rate), int(5 * self.rate), int(20 * self.rate), int(20 * self.rate)))
        self.MinimizeButton.setToolTip('<b>最小化 Minimize</b>')
        self.MinimizeButton.setStyleSheet("background-color:rgba(62, 62, 62, 0);")
        self.MinimizeButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.MinimizeButton.clicked.connect(self.showMinimized)
        self.MinimizeButton.hide()

        # 退出按钮
        self.QuitButton = QPushButton(qticon('fa.times', color='white'), "", self)
        self.QuitButton.setIconSize(QSize(20, 20))
        self.QuitButton.setGeometry(QRect(int(642 * self.rate), int(5 * self.rate), int(20 * self.rate), int(20 * self.rate)))
        self.QuitButton.setToolTip('<b>退出程序 Quit</b>')
        self.QuitButton.setStyleSheet("background-color:rgba(62, 62, 62, 0);")
        self.QuitButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.QuitButton.hide()

        # 右下角用于拉伸界面的控件 mac系统应该注释掉
        self.statusbar = QStatusBar(self)
        self.statusbar.setStyleSheet("background-color:rgba(62, 62, 62, 0);")
        self.setStatusBar(self.statusbar)


    # 根据文本内容调整大小
    def textAreaChanged(self):
        newHeight = self.document.size().height()
        width = self.width()
        self.resize(int(width), int(newHeight + 30 * self.rate))
        self.translateText.setGeometry(0, int(30 * self.rate), int(width), int(newHeight))

    def update(self):
        data = settinRead()

        if(data["play"] == "OFF"):
            self.StartButton.setIcon(qticon('fa.play', color='white'))
        else:
            self.StartButton.setIcon(qticon('fa.pause', color='white'))

    def modeChange(self,checked):
        if checked:
            self.mode = "loop"
        else:
            self.mode = "once"

        data = settinRead()
        data["mode"] = self.mode
        settinSet(data)

    def resizeEvent(self, QResizeEvent):  
        # 重新调整边界范围以备实现鼠标拖放缩放窗口大小，采用三个列表生成式生成三个列表
        self._right_rect = [QPoint(x, y) for x in range(self.width() - self._padding, self.width() + 1)
                            for y in range(1, self.height() - self._padding)]
        self._bottom_rect = [QPoint(x, y) for x in range(1, self.width() - self._padding)
                             for y in range(self.height() - self._padding, self.height() + 1)]
        self._corner_rect = [QPoint(x, y) for x in range(self.width() - self._padding, self.width() + 1)
                             for y in range(self.height() - self._padding, self.height() + 1)]

    # 在面板上显示
    def displayText(self,text,showType="ocr"):
        if(showType == "ocr"):
            color = self.data["ocrFontColor"]
        elif(showType == "translate"):
            color = self.data["translateFontColor"]

        try:
            if self.data["showColorType"] == "False":
                self.format.setTextOutline(
                    QPen(QColor(color), 0.7, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                self.translateText.mergeCurrentCharFormat(self.format)
                self.translateText.append(text)
            else:
                self.translateText.append("<font color={}>{}</font>".format(color,text))
                print(self.data[color])
            self.thread_state -= 1  # 线程结束，减少线程数
        except Exception as ex:
            logger.error("错误信息："+str(ex))

    #使用线程进行显示
    def createThreadDisplay(self,text,showType ="ocr"):
        self.thread_state += 1  # 线程开始，增加线程数
        dThread = displayThread(text,showType)
        thread = Thread(target=dThread.run)
        thread.setDaemon(True)
        dThread.displaySignal.connect(self.displayText)
        thread.start()

    # 鼠标进入控件事件
    def enterEvent(self, QEvent):
        try:
            # 显示所有顶部工具栏控件
            self.QuitButton.show()
            self.MinimizeButton.show()
            self.LockButton.show()
            self.SettinButton.show()
            self.setStyleSheet('QLabel#dragLabel {background-color:rgba(62, 62, 62, 0.3)}')

        except Exception as ex:
            logger.error("错误信息："+str(ex))

    # 鼠标移动事件
    def mouseMoveEvent(self, e: QMouseEvent):

        if self.lockSign == "True":
            return
        if(self._startPos ==None):
            return 
        try:
            self._endPos = e.pos() - self._startPos
            self.move(self.pos() + self._endPos)
            
        except Exception as ex:
            logger.error("错误信息："+str(ex))

    # # 鼠标按下事件
    def mousePressEvent(self, e: QMouseEvent):
        if self.lockSign == "True":
            return
        try:
            if e.button() == Qt.LeftButton:
                self._isTracking = True
                self._startPos = QPoint(e.x(), e.y())
        except Exception as ex:
            logger.error("错误信息："+str(ex))

    #鼠标松开事件        
    def mouseReleaseEvent(self, e: QMouseEvent):

        if self.lockSign == "True":
            return

        try:
            if e.button() == Qt.LeftButton:
                self._isTracking = False
                self._startPos = None
                self._endPos = None
        except Exception as ex:
            logger.error("错误信息："+str(ex))

    # 鼠标离开控件事件
    def leaveEvent(self, QEvent):
        try:
            # 隐藏所有顶部工具栏控件
            self.QuitButton.hide()
            self.MinimizeButton.hide()
            self.LockButton.hide()
            self.SettinButton.hide()
            self.setStyleSheet('QLabel#dragLabel {background-color:none}')
        except Exception as ex:
            logger.error("错误信息："+str(ex))

    # 锁定界面
    def lock(self):

        try:
            if self.lockSign == "False":
                self.LockButton.setIcon(qticon('fa.unlock', color='white'))
                self.dragLabel.hide()
                self.lockSign = "True"

                if self.horizontal == 0.01:
                    self.horizontal = 0
            else:
                self.LockButton.setIcon(qticon('fa.lock', color='white'))
                self.LockButton.setStyleSheet("background-color:rgba(62, 62, 62, 0);")
                self.dragLabel.show()
                self.lockSign = "False"

                if self.horizontal == 0:
                    self.horizontal = 0.01

            self.translateText.setStyleSheet("border-width:0;\
                                              border-style:outset;\
                                              border-top:0px solid #e8f3f9;\
                                              color:white;\
                                              font-weight: bold;\
                                              background-color:rgba(62, 62, 62, %s)"
                                             % (self.horizontal))
        except Exception as ex:
            print("错误信息："+str(ex))

    def rangeBt(self):
        try:
            self.Range = WScreenShot(self.chooseRange)  # 范围界面
            # 如果当前处于运行状态则停止
            if self.runStatus == "ON":
                self.runStatus = "OFF"
                settinSetPlay(self.runStatus)
                # 改变翻译键的图标
                self.StartButton.setIcon(qticon('fa.play', color='white'))

            self.Range.show()  # 打开范围界面
            self.show()  # 主界面会被顶掉，再次打开

        except Exception as ex:
            logger.error("错误信息："+str(ex))

    
    # def startBt(self):
    #     if(self.runStatus == "ON"):
    #         self.runStatus = "OFF"
    #         self.StartButton.setIcon(qticon('fa.play', color='white'))
    #     else:
    #         self.runStatus = "ON"
    #         self.StartButton.setIcon(qticon('fa.pause', color='white'))
    #     settinSetPlay(self.runStatus)
    #     self.display_text("测试，点击了开关")
    #     # logger.info(image_cut())
        


if __name__ == '__main__':
    import sys

    screen_scale_rate = get_screen_rate()
    App = QApplication(sys.argv)
    Init = MainInterface(screen_scale_rate)

    Init.QuitButton.clicked.connect(Init.close)
    Init.show()
    App.exit(App.exec_())
