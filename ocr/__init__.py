from difflib import SequenceMatcher
from cv2 import cvtColor, COLOR_BGR2GRAY, calcHist, resize,imwrite
from config.settin import settinRead,settinSet,settinSetPlay
from loguru import logger
from PyQt5.QtCore import QThread, pyqtSignal
import time,os

from ocr.ocrCh import localOcr
ocr = localOcr()
from src.screenshot import image_cut,array_to_pixmap
from config import Config
config = Config()
# 判断原文相似度
def get_equal_rate(str1, str2):
    score = SequenceMatcher(None, str1, str2).quick_ratio()
    return score

# 计算单通道的直方图的相似值
def calculate(image1, image2):
    hist1 = calcHist([image1], [0], None, [256], [0.0, 255.0])
    hist2 = calcHist([image2], [0], None, [256], [0.0, 255.0])
    # 计算直方图的重合度
    degree = 0
    for i in range(len(hist1)):
        if hist1[i] != hist2[i]:
            degree = degree + (1 - abs(float(hist1[i]) - float(hist2[i])) / max(float(hist1[i]), float(hist2[i])))
        else:
            degree = degree + 1
    degree = degree / float(len(hist1))
    return degree

# 判断图片相似度
def compare_image(imageA, imageB):
    if imageA is None or imageB is None:
        return 0.2
    grayA = cvtColor(imageA, COLOR_BGR2GRAY)
    grayB = cvtColor(imageB, COLOR_BGR2GRAY)

    if grayA.shape != grayB.shape:
        new_shape = [(grayA.shape[0] + grayB.shape[0]) // 2, (grayA.shape[1] + grayB.shape[1]) // 2]
        grayA = resize(grayA, (new_shape[1], new_shape[0]))
        grayB = resize(grayB, (new_shape[1], new_shape[0]))
    else:
        if (imageA == imageB).all():
            return 1.

    score = calculate(grayA, grayB)
    return score

def close_engine():
    ocr.exit()

class ocrThread(QThread):
    ocrOverSignal = pyqtSignal(str)

    def __init__(self, mode):
        self.mode = mode #传入运行模式，once loop
        super(ocrThread, self).__init__()
        self.run_flag = True

    def exit(self):
        self.run_flag = False

    def run(self):
        data = settinRead()
        logger.debug(self.mode)
        if self.mode == "once":
            image = image_cut()
            image_bytes = array_to_pixmap(image)
            ocr_start_time = time.time()

            try:
                restext = ocr.run(image_bytes,config.ocr_break_line)
                logger.debug("ocr耗时：{}".format(time.time() - ocr_start_time))
                self.ocrOverSignal.emit(restext)
            except:
                logger.warning("ocr识别失败")

            #os.unlink(image_path)
        else:
            settinSetPlay("ON")
            logger.info("开始连续识别")
            # try:
            last_time = time.time()
            last_img = None

            first_ocr = True #首次识别标志
            while self.run_flag:
                data = settinRead()
                #logger.debug(data["play"])
                if(data["play"] == "OFF"):
                    last_img = None
                    logger.info("退出连续识别")
                    break

                now_time = time.time()
                #logger.info("lastTime:{},nowTime:{},c:{}".format(lastTime,nowTime,lastTime - nowTime))
                # try:

                # 如果两次识别间隔小于设置的间隔时间，则休眠
                if now_time - last_time < config.ocr_interval :#defaultConfig.ocrInterval:
                    sleepTime = config.ocr_interval - (now_time - last_time)
                    #logger.debug("休眠：{}".format(sleepTime))
                    time.sleep(sleepTime)
                    last_time = time.time()
                    
                #orcStartTime = time() 
                image = image_cut()  
                image_bytes = array_to_pixmap(image)  
                # 首次识别，不判断图片是否重复
                if(first_ocr):
                    try:
                        restext = ocr.run(image_bytes,config.ocr_break_line)
                        self.ocrOverSignal.emit(restext)
                        first_ocr = False
                    except Exception as e:
                        logger.warning("ocr识别失败: {}".format(e))
                        
                else:
                    score = compare_image(last_img,image)
                    #logger.info("图片相似性: {}, 设置的阈值: {}".format(score, defaultConfig.imgSimilarityScore))
                    if score <= config.img_similarity_score:
                        try:
                            restext = ocr.run(image_bytes,config.ocr_break_line)
                            self.ocrOverSignal.emit(restext)
                            last_img = image
                        except Exception as e:
                            logger.warning("ocr识别失败: {}".format(e))

                #os.unlink(image_path)

