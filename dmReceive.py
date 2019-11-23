import os
import urllib.request
import json
import config
import time
import getVideo
import threading
from dmSend import send_dm



roomid = config.roomid
csrf_token = config.csrf_token
dm_temp = ""

# 调用官方api获取直播间弹幕
def getDm():
    global roomid
    global csrf_token
    try:
        url = "http://api.live.bilibili.com/ajax/msg"
        postdata = urllib.parse.urlencode({
            'token:': '',
            'csrf_token:': csrf_token,
            'roomid': roomid
        }).encode('utf-8')
        header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "utf-8",
            "Accept-Language": "zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Host": "api.live.bilibili.com",
            "Referer": "http://live.bilibili.com/"+roomid,
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:32.0) Gecko/20100101 Firefox/32.0"
        }

        req = urllib.request.Request(url, postdata, header)
        dm_result = json.loads(urllib.request.urlopen(
            req, timeout=2).read().decode('utf-8'))
        return dm_result
    except Exception as e:
        print(e)
        
# 弹幕消息匹配
def pick_msg(msg, user):
    
    if msg.find("点歌") == 0:
        pass
    elif msg.find("切歌") == 0:
        # 强行结束ffmpeg进程以达到切歌效果
        if getVideo.ENCODE_LOOK:
            print("还有视频正在渲染中...... O.O\n")
        else:
            os.system(command="taskkill /F /IM ffmpeg.exe")
            send_dm("切歌完成(*^_^*)")     
    elif msg.find("av") & msg.find("AV") == 0:
        # 将用户名和msg添加到下载队列中 
        # DOWNLOADLST.append([msg, user]) 
        threading.Thread(target=getVideo.downloader, args=(msg,user)).start()

        
# 获取最新弹幕
def checkDm(target):
    global dm_temp
    for t_get in dm_temp['data']['room']:
        if((t_get['text'] == target['text']) & (t_get['timeline'] == target['timeline'])):
            return False
    return True


# 实时抓取直播间弹幕
def getDmLoop():
    global dm_temp
    dm_temp = getDm()
    while True:
        try:
            dm_result = getDm()
            for arry in dm_result["data"]["room"]:
                if checkDm(arry):
                    print("[log] " + arry["timeline"] + " " +
                          arry["nickname"] + "说：" + arry["text"])
                    pick_msg(arry["text"], arry["nickname"])

            dm_temp = dm_result
            time.sleep(2)
        except Exception as e:
            print(e)
