from random import randint
from hashlib import md5
from http.client import HTTPConnection
import json
from urllib import parse


def baidu_translate(sentence, appid, secretKey, fromLang='auto', toLang='zh'):
    httpClient = None
    myurl = '/api/trans/vip/translate'

    salt = randint(32768, 65536)
    q = sentence
    sign = appid + q + str(salt) + secretKey
    sign = md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + parse.quote(q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
        salt) + '&sign=' + sign

    try:
        httpClient = HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)

        response = httpClient.getresponse()
        result_all = response.read().decode("utf-8")
        result = json.loads(result_all)

        string = ''
        for word in result['trans_result']:
            if word == result['trans_result'][-1]:
                string += word['dst']
            else:
                string += word['dst'] + '\n'

    except Exception:
        if result['error_code'] == '54003':
            string = "翻译：我抽风啦！"
        elif result['error_code'] == '52001':
            string = '翻译：请求超时，请重试'
        elif result['error_code'] == '52002':
            string = '翻译：系统错误，请重试'
        elif result['error_code'] == '52003':
            string = '翻译：APPID 或 密钥 不正确'
        elif result['error_code'] == '54001':
            string = '翻译：APPID 或 密钥 不正确'
        elif result['error_code'] == '54004':
            string = '翻译：账户余额不足'
        elif result['error_code'] == '54005':
            string = '翻译：请降低长query的发送频率，3s后再试'
        elif result['error_code'] == '58000':
            string = '翻译：客户端IP非法，注册时错误填入服务器地址，请前往开发者信息-基本信息修改，服务器地址必须为空'
        elif result['error_code'] == '90107':
            string = '翻译：认证未通过或未生效'
        else:
            string = '翻译：%s，%s' % (result['error_code'], result['error_msg'])
        raise Exception(string)
    
    finally:
        if httpClient:
            httpClient.close()

    return string
