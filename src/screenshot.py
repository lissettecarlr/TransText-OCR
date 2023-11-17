# 该文件用于截图图片，坐标来源于setting.json文件

from loguru import logger 
from PyQt5.QtWidgets import QApplication
from numpy import fromstring, uint8
from time import strftime,localtime
from cv2 import imwrite
from config.settin import settinRead
from PIL import Image
import io
import numpy as np

def pixmap_to_array(pixmap, channels_count=4):
    size = pixmap.size()
    width = size.width()
    height = size.height()

    image = pixmap.toImage()
    s = image.bits().asstring(width * height * channels_count)
    img = fromstring(s, dtype=uint8).reshape((height, width, channels_count))
    img = img[:, :, :3]
    #print("1111 : {}".format(type(img)))
    return img.astype(uint8)


def array_to_pixmap(arr):
    '''
    将numpy数组转换为字节流
    '''
    # 将numpy数组转换为PIL图像
    img = Image.fromarray(np.uint8(arr))
    # 创建一个BytesIO对象
    byte_io = io.BytesIO()
    # 保存图像到BytesIO对象
    img.save(byte_io, 'PNG')
    # 获取字节流
    byte_io.seek(0)
    byte_data = byte_io.read()

    return byte_data

def image_cut():
    data = settinRead()
    x1 = data["range"]['X1'] + 2  # 不截虚线框
    y1 = data["range"]['Y1'] + 2
    x2 = data["range"]['X2'] - 2
    y2 = data["range"]['Y2'] - 2

    image = None
    try:
        screen = QApplication.primaryScreen()
        pix = screen.grabWindow(QApplication.desktop().winId(), x1, y1, x2 - x1, y2 - y1)
        image = pixmap_to_array(pix)

        #imgPath = array_to_pixmap(image)
        # 将截图保存在本地
        # root = os.path.dirname(os.path.realpath(sys.argv[0]))
        # temp_files_path = os.path.join(root, "temp")

        # if not os.path.exists(temp_files_path):
        #     os.makedirs(temp_files_path)

        # t = strftime("%Y_%m_%d_%H_%M_%S", localtime())
        # imgPath = os.path.join(temp_files_path, t + '_' + str(random.randint(1000, 9999)) + '.jpg')
        # imwrite(imgPath, image)

        #print("保存截图: {}".format(imgPath))
        #print("22222 : {}".format(type(image)))
        #return image,imgPath
        return image

    except Exception as ex:
        logger.error("错误信息："+str(ex))
        raise Exception(f"截图错误: {str(ex)}")

    