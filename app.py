import sys
from qtawesome import icon as qticon

from PyQt5.QtWidgets import QApplication
from loguru import logger

from mainWin import MainInterface
from src.screenRate import get_screen_rate
from src.settingWin import SettinInterface
from config.settin import settinRead,settinSet,settinInit,settinSetPlay
from ocr import ocrThread,close_engine
from config import Config
config = Config()

class app():

    # 退出程序
    def close(self):
        close_engine()
        settinInit()
        self.mainWin.close()

    # 进入设置页面
    def gotoSettin(self):
        data = settinRead()
        if data["play"] == "ON":
            settinSetPlay("OFF")
            self.mainWin.StartButton.setIcon(qticon('fa.play', color='white'))
        self.setWin.show()
 
    # 刷新主界面
    def updataMainUi(self):
        self.setWin.saveSettin()
        data = settinRead()
        horizontal = data["horizontal"] /100
        self.setWin.close()

        # 刷新翻译界面的背景透明度
        if horizontal == 0:
            horizontal = 0.01
        self.mainWin.translateText.setStyleSheet("border-width:0;\
                                               border-style:outset;\
                                               border-top:0px solid #e8f3f9;\
                                               color:white;\
                                               font-weight: bold;\
                                               background-color:rgba(62, 62, 62, %s)"
                                              % (horizontal))

    #识别后的回调
    def ocrOver(self,resText):
        # 如果OCR失败结果为空则啥都不干
        if(resText == ""):
            logger.info("识别结果为空")
            return

        logger.info("完成识别：{}".format(resText))
        self.mainWin.translateText.clear()

        data = settinRead()
        if data["showOriginal"] =="True":
            self.mainWin.createThreadDisplay(resText)

        ## 翻译
        if data["translate"] == "True":
            from translate import translate
            import time
            strat_time = time.time()
            try:
                transalte_text = translate(
                    sentence = resText,
                    server_name = data["translateServer"],
                    fromLang = config.translate_from_language,
                    toLang = config.translate_to_language
                    )
                logger.info("翻译完成，耗时：{}，{},".format(time.time()-strat_time,transalte_text))
                self.mainWin.createThreadDisplay(transalte_text,"translate")

            except Exception as ex:
                logger.warning("翻译失败：{}".format(ex))
            
            

    def startBt(self):
        data = settinRead()
        #如果是单次执行则不改变按钮状态
        if(data["mode"] == "loop"):
            if(data["play"] == "OFF"): #按键开始
                self.mainWin.StartButton.setIcon(qticon('fa.pause', color='white'))
                thread = ocrThread("loop")
                thread.ocrOverSignal.connect(self.ocrOver)
                thread.start()
                thread.exec()
            
            else:#按键停止
                data["play"] = "OFF"
                settinSet(data)
                self.mainWin.StartButton.setIcon(qticon('fa.play', color='white'))

        if(data["mode"] == "once"):
            if(data["play"] == "OFF"): #按键开始
                thread = ocrThread("once")
                thread.ocrOverSignal.connect(self.ocrOver)
                thread.start()
                thread.exec()  
            else: #此情况发生在 开始了连续识别，但是先切换了模式再点击开关按钮
                data["play"] = "OFF"
                settinSet(data)  
                self.mainWin.StartButton.setIcon(qticon('fa.play', color='white'))     
 
    # 主循环
    def main(self):

        App = QApplication(sys.argv)
        self.screen_scale_rate = get_screen_rate()
        self.mainWin = MainInterface(self.screen_scale_rate) #主界面
        self.setWin = SettinInterface(self.screen_scale_rate)

        self.mainWin.StartButton.clicked.connect(self.startBt)
        self.mainWin.QuitButton.clicked.connect(self.close)
        self.mainWin.SettinButton.clicked.connect(self.gotoSettin)

        self.setWin.SaveButton.clicked.connect(self.updataMainUi)
        self.setWin.CancelButton.clicked.connect(self.setWin.close)

        # self.mainWin.exFunctionButton.clicked.connect(self.exFunction)
        # self.mainWin.diceButton.clicked.connect(self.diceButtonFunction)
        self.mainWin.show()
        data = settinRead()
        # if(data["speeckAck"]=="True"):
        #     self.textAck = communication()
        App.exit(App.exec_())


if __name__ == '__main__':
    win = app()
    win.main()
