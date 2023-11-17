import yaml
from translate.baidu import baidu_translate

with open('./config/secret.yaml', 'r',encoding="utf-8") as file:
    secret_data = yaml.safe_load(file)

def translate(sentence,server_name,fromLang='auto',toLang='zh') -> str:
    if server_name == "baidu":
        try:
            appid = secret_data["baidu"]["appid"]
            secretKey = secret_data["baidu"]["secretKey"]
        except:
            raise Exception("百度翻译密钥未配置")
        
        return baidu_translate(sentence, 
                               appid = appid, 
                               secretKey = secretKey, 
                               fromLang=fromLang, 
                               toLang=toLang
                
                )
    
    elif server_name == "chatgpt":
        return "未写"