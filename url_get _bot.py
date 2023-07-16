import requests
import websocket
import base64
import json
import threading
import time
import queue
import traceback
import random
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter


null=None#为了替换返回中的信息，测试用
false=False
lingpai='0f2de7ac66727cd9fcec1ee43559c561f6abf3f1e202c5ab795fbfd311a18ad1ff314388d1c'#换为你自己的机器人令牌
si=['目前只支持图片、视频、文件，支持类型以外可能会导致获取错误','体验机器人、网站、软件，欢迎加入服务器：https://fanbook.mobi/LmgLJF3N ','如遇到消息没有正常显示或者没有反应，可稍等重试\n此服务仅在中午以后，晚上10点以前可用，如果仍然不能使用，请私信:${@!389320179948986368}','如获取不成功，可尝试更换文件','手动获取图片链接:https://fanbookwdg3.zmidc.eu.org/']#随机提示，可自己改，记得在消息文本那里改随机数
data_queue = queue.Queue()
sc=0#统计变量
cwc=0


def colorize_json(smg2,pcolor=''):#JSON高亮，如果你的终端软件显示不正常，可直接改为print(json_data)
    json_data=smg2
    try:
        parsed_json = json.loads(json_data)  # 解析JSON数据
        formatted_json = json.dumps(parsed_json, indent=4)  # 格式化JSON数据

        # 使用Pygments库进行语法高亮
        colored_json = highlight(formatted_json, JsonLexer(), TerminalFormatter())

        print(colored_json)
    except json.JSONDecodeError as e:
        print(json_data)

def on_message(ws, message):
    # 处理接收到的消息
    colorize_json(message)
    global sc
    global cwc
    # 在这里添加收到消息后你希望执行的操作
    if len(message) > 100:#筛选有效信息
        try:
            data=message
            data = json.loads(data)
            # 解析数据中的content字段，它是一个json字符串
            content = json.loads(data["data"]["content"])
            if data['data']['guild_id'] == null:
                    try:
                        url='https://a1.fanbook.mobi/api/bot/'+lingpai+'/sendMessage'
                        headers = {'content-type':"application/json;charset=utf-8"}
                        jsonfile=json.dumps({
                        "chat_id":int(data['data']['channel_id']),
                        "text": '获取成功，图片/视频链接：\n'+content["url"]+'\n欢迎下次使用\n提示：'+si[random.randint(0,4)]#这里的随机数需要按照你的提示数量修改
                        })
                        postreturn=requests.post(url,data=jsonfile,headers=headers)
                        colorize_json(postreturn.text)
                        sc+=1
                        print('使用次数：',sc)
                    except Exception as e:
                        try:
                            url='https://a1.fanbook.mobi/api/bot/'+lingpai+'/sendMessage'
                            headers = {'content-type':"application/json;charset=utf-8"}
                            jsonfile=json.dumps({
                            "chat_id":int(data['data']['channel_id']),
                            "text": '获取成功，文件链接：\n'+content["file_url"]+'\n欢迎下次使用\n提示：'+si[random.randint(0,4)]
                            })
                            postreturn=requests.post(url,data=jsonfile,headers=headers)
                            colorize_json(postreturn.text)
                            sc+=1
                            print('使用次数：',sc)
                        except Exception as e:
                                try:
                                    print(traceback.format_exc())
                                    url='https://a1.fanbook.mobi/api/bot/'+lingpai+'/sendMessage'
                                    headers = {'content-type':"application/json;charset=utf-8"}
                                    jsonfile=json.dumps({
                                    "chat_id":int(data['data']['channel_id']),
                                    "text": '获取失败，发生错误：\n'+traceback.format_exc()+'\n目前只支持图片、视频、文件，文本内容可能会导致错误，请直接发送图片、视频、文件\n如果你的输入没有问题，但是不能获取，可以将此消息复制给${@!389320179948986368}，会尽快修复'
                                    })
                                    postreturn=requests.post(url,data=jsonfile,headers=headers)
                                    colorize_json(postreturn.text)
                                    cwc+=1
                                    print('错误次数：',cwc)
                                except Exception as e:
                                    print(traceback.format_exc())
            else:
                if '${@!448828939389894656}' in data["data"]["content"]:#也可以增加在频道使用功能
                    url='https://a1.fanbook.mobi/api/bot/'+lingpai+'/sendMessage'
                    headers = {'content-type':"application/json;charset=utf-8"}
                    jsonfile=json.dumps({
                    "chat_id":int(data['data']['channel_id']),
                    "text": '请私聊直接发送图片使用获取图片链接功能'
                    })
                    postreturn=requests.post(url,data=jsonfile,headers=headers)
                    colorize_json(postreturn.text)
                    cwc+=1
                    print('错误次数：',cwc)
        except Exception as e:
            print(traceback.format_exc())
def on_error(ws, error):
    # 处理错误
    print("发生错误:", error)

def on_close(ws):
    # 连接关闭时的操作
    print("连接已关闭")

def on_open(ws):
    # 连接建立时的操作
    print("连接已建立")
    # 发送心跳包
    def send_ping():#此处不太正常，忽略
        print('发送：{"type":"ping"}')
        ws.send('{"type":"ping"}')

    send_ping()  # 发送第一个心跳包

    # 定时发送心跳包
    def schedule_ping():
        send_ping()
        # 每25秒发送一次心跳包
        websocket._get_connection()._connect_time = 0  # 重置连接时间，避免过期
        ws.send_ping()
        websocket._get_connection().sock.settimeout(70)
        ws.send('{"type":"ping"}')
    websocket._get_connection().run_forever(ping_interval=25, ping_payload='{"type":"ping"}', ping_schedule=schedule_ping)#定时发送有问题，忽略，已在第二线程中实现

# 替换成用户输入的BOT令牌
lingpai = lingpai
url = f"https://a1.fanbook.mobi/api/bot/{lingpai}/getMe"

# 发送HTTP请求获取基本信息
response = requests.get(url)
data = response.json()

def send_data_thread():
    while True:#多线程自动发送心跳包，互不干扰
        # 在这里编写需要发送的数据
        time.sleep(25)
        ws.send('{"type":"ping"}')
        print('发送心跳包：{"type":"ping"}')

if response.ok and data.get("ok"):
    user_token = data["result"]["user_token"]
    device_id = "your_device_id"
    version_number = "1.6.60"
    super_str = base64.b64encode(json.dumps({
        "platform": "bot",
        "version": version_number,
        "channel": "office",
        "device_id": device_id,
        "build_number": "1"
    }).encode('utf-8')).decode('utf-8')
    ws_url = f"wss://gateway-bot.fanbook.mobi/websocket?id={user_token}&dId={device_id}&v={version_number}&x-super-properties={super_str}"
    threading.Thread(target=send_data_thread, daemon=True).start()
    # 建立WebSocket连接
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(ws_url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
else:
    print("无法获取BOT基本信息，请检查令牌是否正确。")
