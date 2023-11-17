# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QLabel, QPushButton, QApplication, QWidget, QColorDialog, QTabWidget, QComboBox, \
    QCheckBox, QSpinBox, QFontComboBox, QToolButton, QSlider, QLineEdit
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import QSize, QRect, Qt

from src.screenRate import get_screen_rate
#from screenRate import get_screen_rate


from config.settin import settinRead,settinSet
from loguru import logger

from config import Config
config = Config()
# 这里要注意的是对配置文件的读取只有程序启动的那一次
# 所有如果其他地方对配置文件修改，这里是不会知道的

class SettinInterface(QWidget):
    def __init__(self, screen_scale_rate):
        super(SettinInterface, self).__init__()

        if 1.01 <= screen_scale_rate <= 1.49:
            self.rate = 1.25
            self.px = 80
            self.image_sign = 2
        else:
            self.rate = 1
            self.px = 75
            self.image_sign = 1

        self.getSettin()
        self.setupUi()

    def setupUi(self):
        # 窗口尺寸及不可拉伸
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.resize(404 * self.rate, 576 * self.rate)
        self.setMinimumSize(QSize(404 * self.rate, 576 * self.rate))
        self.setMaximumSize(QSize(404 * self.rate, 576 * self.rate))
        self.setWindowFlags(Qt.WindowMinimizeButtonHint)

        # 窗口标题
        self.setWindowTitle("设置")

        # 窗口样式
        # self.setStyleSheet("QWidget {""font: 9pt \"华康方圆体W7\";"
        #                    "background-image: url(./config/Background%d.jpg);"
        #                    "background-repeat: no-repeat;"
        #                    "background-size:cover;""}" % self.image_sign)
        self.setStyleSheet("QWidget {""font: 9pt \"微软雅黑\"};")  # 华康方圆体W7

        # 窗口图标
        self.icon = QIcon()
        self.icon.addPixmap(QPixmap("./config/logo.ico"), QIcon.Normal, QIcon.On)
        self.setWindowIcon(self.icon)

        # 顶部工具栏
        self.tabWidget = QTabWidget(self)
        self.tabWidget.setGeometry(QRect(-2, 0, 410 * self.rate, 580 * self.rate))
        self.tabWidget.setCurrentIndex(0)

        # 工具栏样式
        self.tabWidget.setStyleSheet("QTabBar::tab {""min-width:%dpx;"
                                     "background: rgba(255, 255, 255, 1);"
                                     "}"
                                     "QTabBar::tab:selected {""border-bottom: 2px solid #4796f0;""}"
                                     "QLabel{""background: transparent;""}"
                                     "QCheckBox{""background: transparent;""}" % (self.px)
                                     )

        # 工具栏2
        # self.tab_2 = QWidget()
        # self.tabWidget.addTab(self.tab_2, "")
        # self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), "设置")

        # 原语言标签
        self.translateSource_label_6 = QLabel(self)
        self.translateSource_label_6.setGeometry(
            QRect(30 * self.rate, 20 * self.rate, 151 * self.rate, 16 * self.rate))
        self.translateSource_label_6.setText("OCR识别语言：")

        # 原语言comboBox
        self.language_comboBox = QComboBox(self)
        self.language_comboBox.setGeometry(
            QRect(190 * self.rate, 20 * self.rate, 150 * self.rate, 22 * self.rate))
        

        for idx, language_name in enumerate(config.language_list):
            self.language_comboBox.addItem("")
            self.language_comboBox.setItemText(idx, language_name)
            if language_name == self.data["language"]:
                pos = idx
        
        self.language_comboBox.setStyleSheet("background: rgba(255, 255, 255, 0.4);")
        self.language_comboBox.setCurrentIndex(pos)

        # 是否显示识别结果checkBox
        self.showOriginal_checkBox = QCheckBox(self)
        self.showOriginal_checkBox.setGeometry(
            QRect(30 * self.rate, 52 * self.rate, 300 * self.rate, 16 * self.rate))
        self.showOriginal_checkBox.setChecked(self.showOriginal)
        self.showOriginal_checkBox.setText("是否显示OCR识别结果")


        self.translate_checkBox = QCheckBox(self)
        self.translate_checkBox.setGeometry(
            QRect(30 * self.rate, 80 * self.rate, 300 * self.rate, 16 * self.rate))
        self.translate_checkBox.setChecked(self.translate)
        self.translate_checkBox.setText("是否对识别结果翻译成中文")


        # 翻译服务
        self.translateSource_label_6 = QLabel(self)
        self.translateSource_label_6.setGeometry(
            QRect(30 * self.rate, 110 * self.rate, 150 * self.rate, 16 * self.rate))
        self.translateSource_label_6.setText("选择翻译器：")

        self.translate_server_comboBox = QComboBox(self)
        self.translate_server_comboBox.setGeometry(
            QRect(190 * self.rate, 110 * self.rate, 150 * self.rate, 22 * self.rate))
        for idx, translate_name in enumerate(config.translate_engine_list):
            self.translate_server_comboBox.addItem("")
            self.translate_server_comboBox.setItemText(idx, translate_name)
            if translate_name == self.data["translateServer"]:
                pos = idx
        self.translate_server_comboBox.setStyleSheet("background: rgba(255, 255, 255, 0.4);")
        self.translate_server_comboBox.setCurrentIndex(pos)

        # self.speeckAck_checkBox = QCheckBox(self)
        # self.speeckAck_checkBox.setGeometry(
        #     QRect(30 * self.rate, 110 * self.rate, 300 * self.rate, 16 * self.rate))
        # self.speeckAck_checkBox.setChecked(self.speeckAck)
        # self.speeckAck_checkBox.setText("识别后进行应答")

 
        # 字体大小设定标签
        # self.fontSize_label = QLabel(self.tab_2)
        # self.fontSize_label.setGeometry(QRect(30 * self.rate, 120 * self.rate, 145 * self.rate, 16 * self.rate))
        # self.fontSize_label.setText("显示文字大小：")

        # 字体大小设定
        # self.fontSize_spinBox = QSpinBox(self.tab_2)
        # self.fontSize_spinBox.setGeometry(
        #     QRect(190 * self.rate, 120 * self.rate, 50 * self.rate, 25 * self.rate))
        # self.fontSize_spinBox.setMinimum(10)
        # self.fontSize_spinBox.setMaximum(30)
        # self.fontSize_spinBox.setStyleSheet("background: rgba(255, 255, 255, 0)")
        # self.fontSize_spinBox.setValue(self.fontSize)

        # 字体样式设定标签
        # self.translate_label = QLabel(self.tab_2)
        # self.translate_label.setGeometry(QRect(30 * self.rate, 145 * self.rate, 145 * self.rate, 20 * self.rate))
        # self.translate_label.setText("显示字体类型：")

        # 字体样式设定
        # self.fontComboBox = QFontComboBox(self.tab_2)
        # self.fontComboBox.setGeometry(QRect(190 * self.rate, 145 * self.rate, 151 * self.rate, 25 * self.rate))
        # self.fontComboBox.setStyleSheet("background: rgba(255, 255, 255, 0.4)")
        # self.fontComboBox.activated[str].connect(self.get_fontType)
        # self.ComboBoxFont = QFont(self.fontType)
        # self.fontComboBox.setCurrentFont(self.ComboBoxFont)

        # 字体颜色设定标签
        # self.colour_label = QLabel(self.tab_2)
        # self.colour_label.setGeometry(QRect(30 * self.rate, 172 * self.rate, 340 * self.rate, 25 * self.rate))
        # self.colour_label.setText("显示文字颜色：")

        # 字体颜色按钮
        # self.originalColour_toolButton = QToolButton(self.tab_2)
        # self.originalColour_toolButton.setGeometry(
        #     QRect(190 * self.rate, 175 * self.rate, 71 * self.rate, 25 * self.rate))
        # self.originalColour_toolButton.setStyleSheet(
        #     "background: rgba(255, 255, 255, 0.4); color: {};".format(self.originalColor))
        # self.originalColour_toolButton.clicked.connect(lambda: self.get_font_color())
        # self.originalColour_toolButton.setText("选择颜色")

        # 显示颜色样式checkBox
        # self.showColorType_checkBox = QCheckBox(self.tab_2)
        # self.showColorType_checkBox.setGeometry(
        #     QRect(30 * self.rate, 200 * self.rate, 340 * self.rate, 20 * self.rate))
        # self.showColorType_checkBox.setChecked(self.showColorType)
        # self.showColorType_checkBox.setText("是否使用实心字体样式（不勾选则显示描边字体样式）")


        #翻译框透明度设定标签1
        self.tab4_label_1 = QLabel(self)
        self.tab4_label_1.setGeometry(QRect(30 * self.rate, 380 * self.rate, 211 * self.rate, 16 * self.rate))
        self.tab4_label_1.setText("调节显示界面的透明度（0~100）")

        #翻译框透明度设定
        self.horizontalSlider = QSlider(self)
        self.horizontalSlider.setGeometry(
            QRect(30 * self.rate, 420 * self.rate, 347 * self.rate, 22 * self.rate))
        self.horizontalSlider.setStyleSheet("background: transparent;")
        self.horizontalSlider.setMaximum(100)
        self.horizontalSlider.setOrientation(Qt.Horizontal)
        self.horizontalSlider.setValue(self.horizontal)
        self.horizontalSlider.valueChanged.connect(self.get_horizontal)

        # 设置保存按钮
        self.SaveButton = QPushButton(self)
        self.SaveButton.setGeometry(QRect(85 * self.rate, 515 * self.rate, 90 * self.rate, 30 * self.rate))
        self.SaveButton.setStyleSheet("background: rgba(255, 255, 255, 0.4);font: 12pt;")
        self.SaveButton.setText("保存")

        # 设置返回按钮
        self.CancelButton = QPushButton(self)
        self.CancelButton.setGeometry(QRect(232 * self.rate, 515 * self.rate, 90 * self.rate, 30 * self.rate))
        self.CancelButton.setStyleSheet("background: rgba(255, 255, 255, 0.4);font: 12pt")
        self.CancelButton.setText("退出")

    def get_horizontal(self):  # 文本框透明度
        self.horizontal = self.horizontalSlider.value()
        self.data["horizontal"] = self.horizontal


    def getSettin(self):  # 获取所有预设值

        self.data  = settinRead()
        # print(self.data["range"])

        # 是否显示OCR识别结果
        self.showOriginal = self.data["showOriginal"]
        if self.showOriginal == "True":
            self.showOriginal = True
        else:
            self.showOriginal = False

        # 是否进行翻译
        self.translate = self.data.get("translate", False)
        if self.translate == "True":
            self.translate = True
        else:
            self.translate = False
        # 翻译服务
        self.translateServer = self.data.get("translateServer", "baidu")

        # 获取文本框透明度预设值
        self.horizontal = self.data["horizontal"]

        # OCR识别文本
        self.language = self.data["language"]
    

    def saveSettin(self):

        #是否显示识别文本
        if self.showOriginal_checkBox.isChecked():
            self.showOriginal = "True"
        else:
            self.showOriginal = "False"
            
        self.data["showOriginal"] = self.showOriginal

        #是否进行翻译
        if self.translate_checkBox.isChecked():
            self.translate = "True"
        else:
            self.translate = "False"
        self.data["translate"] = self.translate

        #翻译服务
        self.data["translateServer"] = config.translate_engine_list[self.translate_server_comboBox.currentIndex()]

        #识别语言
        self.data["language"] =  config.language_list[self.language_comboBox.currentIndex()] 

        #透明度
        self.horizontal = self.horizontalSlider.value()
        self.data["horizontal"] = self.horizontal

        #print(self.data["range"])
        # 更新其他参数
        newData  = settinRead()
        self.data["lockSign"] = newData["lockSign"]
        self.data["mode"] = newData["mode"]
        self.data["play"] = newData["play"]
        self.data["range"] = newData["range"]        

        settinSet(self.data)
     

if __name__ == "__main__":
    import sys

    screen_scale_rate = get_screen_rate()
    APP = QApplication(sys.argv)
    Settin = SettinInterface(screen_scale_rate)
    Settin.SaveButton.clicked.connect(Settin.saveSettin)
    Settin.show()
    sys.exit(APP.exec_())
