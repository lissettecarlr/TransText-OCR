from json import load, dump
import os,sys

base_path = os.path.dirname(os.path.realpath(sys.argv[0]))

def settinRead():
    settin = os.path.join(base_path, "config/settin.json")
    with open(settin,encoding="utf-8") as file:
        data = load(file)
    return data


def settinSet(data):
    settin = os.path.join(base_path, "config/settin.json")
    with open(settin, 'w',encoding="utf-8") as file:
        dump(data, file, indent=2)
    
def settinInit():
    data = settinRead()
    data["mode"] = "once"
    data["lockSign"] = "False"
    data["play"] = "OFF"
    settinSet(data)

def settinSetPlay(sta):
    data = settinRead()
    if(sta == "OFF" or sta == "ON"):
        data["play"] = sta
    else:
        print("sta 输入错误")
    settinSet(data)
