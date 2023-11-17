import requests
import json
from loguru import logger
from base64 import b64encode
from cv2 import imencode


def image_to_base64(image_np):
    #压缩
    image = imencode('.jpg', image_np)[1]
    image_code = str(b64encode(image))[2:-1]
    return image_code

class httpOcr:
    def __init__(self):
        self.url = "http://127.0.0.1:6666/ocr/server"

    def ocr(self,imagePath,language,timeout = 20):
        #外面直接转入图片数组
        image = imagePath
        #image =cv2.imread(imagePath)
        #print(type(image))
        img = image_to_base64(image)
        proxies = {"http": None, "https": None}
        try:
            response = requests.post(self.url, data={"image": img,"language": language}, proxies=proxies,timeout=timeout)
            if response:
                response.encoding = "utf-8"
                responseText = json.loads(response.text)
                #print("responseText={}".format(responseText))
                result = responseText["Data"]
                # for one_ann in result:
                #     text = one_ann["Words"]
                #     print("text={}".format(text))
            return result
        except Exception as ex:
            logger.warning("ocr 请求失败：{}".format(ex))
            return []

       


# [{'Coordinate': {'LowerLeft': 0, 'LowerRight': 0, 'UpperLeft': 0, 'UpperRight': 0}, 'Score': 0, 'Words': '9'}]            
if __name__ == "__main__" :
    test = httpOcr()
    re = test.ocr("D:\\code\\ggggg\\paddleOcr-server\\test\\9.jpg","write")
    print(re)