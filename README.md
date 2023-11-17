# ocr_client

ocr识别客户端，可打包，能够离线本地运行，使用paddleocr模型。识别后可对接多类翻译器，目前支持百度和chatgpt。

## 使用

* 到[Releases](https://github.com/lissettecarlr/TransText-OCR/releases)下载最新版本`ocr.zip`
* 如果需要翻译则要在解压后的`config`文件中添加`secret.yaml`文件并填入相关密匙，格式如下
    ```yaml
    baidu:
        appid : ""
        secretKey : ""

    chatgpt : 
        key : ""
    ```
    百度翻译密匙获取：[百度翻译开放平台](https://fanyi-api.baidu.com/manage/developer)，在开发者信息中可以看到appid和密匙，标准版免费调用量为5万字符/月，高级版免费调用量为100万字符/月。
    
* 双击`ocr识别器.exe`运行



* 一些可能修改的设置被放在了`config/cfg.yaml`中，至于为啥没在运行界面中的设置中，主要是懒，之后再弄进去吧。
    * ocrInterval ：ocr识别间隔，单位为秒，主要电脑性能调节，默认1秒
    * ocrBreakLine : 识别文本是否和原图一样有换行，默认false，即不换行。


## 打包

* Python 3.10.13

* 依赖
    ```base
    pip install -r requirements.txt
    ```
* 打包
    ```base
    pyinstaller -F -w -i config/logo.ico -n "ocr识别器" app.py
    ```

* 将下列文件至于exe目录

    ```
    │   ocr识别器.exe
    │
    ├───config
    │       cfg.yaml
    │       settin.json
    │
    └───ocr
        └───PaddleOCR-json
    ```
