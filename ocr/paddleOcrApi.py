import os
import subprocess  # 进程，管道
from json import loads as jsonLoads, dumps as jsonDumps
from sys import platform as sysPlatform  # popen静默模式
from base64 import b64encode

class OcrApi:
    def __init__(self, exePath: str, argument: dict = None):
        """初始化识别器。\n
        `exePath`: 识别器`PaddleOCR_json.exe`的路径。\n
        `argument`: 启动参数，字典`{"键":值}`。
            指定不同语言的配置文件路径，识别多国语言
            {'config_path':"./PaddleOCR-json/models/config_chinese.txt"}
            启用cls方向分类，识别方向不是正朝上的图片。默认false
            {'cls':false}
            启用方向分类，必须与cls值相同。
            {'use_angle_cls':false}
            启用CPU推理加速，关掉可以减少内存占用，但会降低速度。默认true
            {'enable_mkldnn':true}
            对图像边长进行限制，降低分辨率，加快速度。
            {'limit_side_len':960}
        """
        cwd = os.path.abspath(os.path.join(exePath, os.pardir))  # 获取exe父文件夹
        # 处理启动参数
        if not argument == None:
            for key, value in argument.items():
                if isinstance(value, str):  # 字符串类型的值加双引号
                    exePath += f' --{key}="{value}"'
                else:
                    exePath += f" --{key}={value}"
        # 设置子进程启用静默模式，不显示控制台窗口
        startupinfo = None
        if "win32" in str(sysPlatform).lower():
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        self.ret = subprocess.Popen(  # 打开管道
            exePath, cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,  # 丢弃stderr的内容
            startupinfo=startupinfo  # 开启静默模式
        )
        # 启动子进程
        while True:
            if not self.ret.poll() == None:  # 子进程已退出，初始化失败
                raise Exception(f"OCR init fail.")
            initStr = self.ret.stdout.readline().decode("utf-8", errors="ignore")
            if "OCR init completed." in initStr:  # 初始化成功
                break

    def run_dict(self, writeDict: dict):
        """传入指令字典，发送给引擎进程。\n
        `writeDict`: 指令字典。\n
        `return`:  {"code": 识别码, "data": 内容列表或错误信息字符串}\n"""
        # 检查子进程
        if not self.ret.poll() == None:
            return {"code": 901, "data": f"子进程已崩溃。"}
        # 输入信息
        writeStr = jsonDumps(writeDict, ensure_ascii=True, indent=None)+"\n"
        try:
            self.ret.stdin.write(writeStr.encode("utf-8"))
            self.ret.stdin.flush()
        except Exception as e:
            return {"code": 902, "data": f"向识别器进程传入指令失败，疑似子进程已崩溃。{e}"}
        # 获取返回值
        try:
            getStr = self.ret.stdout.readline().decode("utf-8", errors="ignore")
        except Exception as e:
            return {"code": 903, "data": f"读取识别器进程输出值失败。异常信息：[{e}]"}
        try:
            return jsonLoads(getStr)
        except Exception as e:
            return {"code": 904, "data": f"识别器输出值反序列化JSON失败。异常信息：[{e}]。原始内容：[{getStr}]"}

    def run(self, imgPath: str):
        """对一张本地图片进行文字识别。\n
        `exePath`: 图片路径。\n
        `return`:  {"code": 识别码, "data": 内容列表或错误信息字符串}\n"""
        writeDict = {"image_path": imgPath}
        return self.run_dict(writeDict)


    def runClipboard(self):
        """立刻对剪贴板第一位的图片进行文字识别。\n
        `return`:  {"code": 识别码, "data": 内容列表或错误信息字符串}\n"""
        return self.run("clipboard")

    def runBase64(self, imageBase64: str):
        """对一张编码为base64字符串的图片进行文字识别。\n
        `imageBase64`: 图片base64字符串。\n
        `return`:  {"code": 识别码, "data": 内容列表或错误信息字符串}\n"""
        writeDict = {"image_base64": imageBase64}
        return self.run_dict(writeDict)

    def runBytes(self, imageBytes):
        """对一张图片的字节流信息进行文字识别。\n
        `imageBytes`: 图片字节流。\n
        `return`:  {"code": 识别码, "data": 内容列表或错误信息字符串}\n"""
        imageBase64 = b64encode(imageBytes).decode('utf-8')
        return self.runBase64(imageBase64)

    def exit(self):
        """关闭引擎子进程"""
        self.ret.kill()  # 关闭子进程

    @staticmethod
    def print_result(res: dict):
        """用于调试，格式化打印识别结果。\n
        `res`: OCR识别结果。"""

        # 识别成功
        if res["code"] == 100:
            index = 1
            for line in res["data"]:
                print(f"{index}-置信度：{round(line['score'], 2)}，文本：{line['text']}")
                index+=1
        elif res["code"] == 100:
            print("图片中未识别出文字。")
        else:
            print(f"图片识别失败。错误码：{res['code']}，错误信息：{res['data']}")


    def __del__(self):
        self.exit()


if __name__ == "__main__":
    # 测试图片路径
    TestImagePath = r"I:\code\ocr_client\temp\test2.png"

    exePath = r"./PaddleOCR-json/PaddleOCR-json.exe"
    argument = {"config_path": "./PaddleOCR-json/models/config_chinese.txt"} 

    ocr = OcrApi(r"./PaddleOCR-json/PaddleOCR-json.exe")
    print(f'初始化OCR成功，进程号为{ocr.ret.pid}')
    print(f'\n测试图片路径：{TestImagePath}')

    res = ocr.run(TestImagePath)
    print(f'\n示例1-图片路径识别结果（原始信息）：\n{res}')
    print(f'\n示例1-图片路径识别结果（格式化输出）：')
    ocr.print_result(res)
    ocr.exit()

