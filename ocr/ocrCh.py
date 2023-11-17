from ocr.paddleOcrApi import OcrApi
from config import Config
import os
from loguru import logger

class localOcr():
    def __init__(self, language=None ,cls=False,limit_side_len=960):
        config = Config()
        self.ocrHander = None
        
        if language == None:
            language = config.default_language

        if language not in config.language_list:
            raise Exception("language not in language_list")
        
        self.engine_path = config.local_ocr_engine_path
        self.engine_root_path =  os.path.abspath(os.path.join(self.engine_path, os.pardir))

        argument = self.engine_argument(language,cls,limit_side_len)
        logger.info(f"ocr engine path: {self.engine_path}")
        logger.info(f"ocr engine argument: {argument}")
        self.engine = OcrApi(self.engine_path,argument)
    
    def engine_argument(self,language,cls=False,limit_side_len=960):
        argument = {}
        # 指定不同语言的配置文件路径
        if language == "ch":
            argument["config_path"] = os.path.join(self.engine_root_path, "models/config_chinese.txt")
        elif language == "en":
            argument["config_path"] = os.path.join(self.engine_root_path, "models/config_en.txt")
        elif language == "jp":
            argument["config_path"] = os.path.join(self.engine_root_path, "models/config_japan.txt")
        else:
            raise Exception("language not in language_list")
        
        # 启用cls方向分类，识别方向不是正朝上的图片
        if cls == True:
            argument["cls"] = True
            argument["use_angle_cls"] = True
        else:
            argument["cls"] = False
            argument["use_angle_cls"] = False

        # 对图像边长进行限制，降低分辨率，加快速度。
        argument["limit_side_len"] = limit_side_len    
        return argument
    
    def run(self,image_path,break_line=False):
        '''
        break_line: 是否根据实际识别换行，默认不换行，返回一行字符串
        '''
        #print(type(image_path))

        if isinstance(image_path, str):
            res = self.engine.run(image_path)
        else:
            res = self.engine.runBytes(image_path)

        logger.debug(f"ocr result: {res}")
        #self.engine.print_result(res)

        if not res["code"] == 100:
            raise Exception("ocr error ,code={},data={}".format(res["code"],res["data"]))
        
        return_text = ""
        if break_line:
            for line in res["data"]:
                return_text += line["text"]+"\n"
        else:
            for line in res["data"]:
                return_text += line["text"]

        return return_text.strip()
                

    def reboot(self,language,cls,limit_side_len):
        if self.engine:
            self.engine.exit()

        argument = self.engine_argument(language,cls,limit_side_len)
        logger.info(f"ocr reboot")
        logger.info(f"ocr engine path: {self.engine_path}")
        logger.info(f"ocr engine argument: {argument}")
        self.engine = OcrApi(self.engine_path,argument)

    def exit(self):
        if self.engine:
            self.engine.exit()
    
    def __del__(self):
        if self.engine:
            self.engine.exit()