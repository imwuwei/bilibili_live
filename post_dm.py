#coding:utf-8
import urllib
import urllib.request
import http.cookiejar
import json
import time
import os
import sys
import datetime
import time
import youtube_dl
import var_set
import _thread
import random
import numpy

path = var_set.path         #引入设置路径
roomid = var_set.roomid     #引入设置房间号
cookie = var_set.cookie     #引入设置cookie
csrf_token = var_set.csrf_token

dm_lock = False         #弹幕发送锁，用来排队
encode_lock = False     #视频渲染锁，用来排队

sensitive_word = ('64', '89') #容易误伤的和谐词汇表，待补充

#检查已使用空间是否超过设置大小
def check_free():
    files = os.listdir(path+'/downloads')  #获取下载文件夹下所有文件
    size = 0
    for f in files:          #遍历所有文件
        size += os.path.getsize(path+'/downloads/'+f)  #累加大小
    files = os.listdir(path+'/default_mp3')#获取缓存文件夹下所有文件
    for f in files:         #遍历所有文件
        size += os.path.getsize(path+'/default_mp3/'+f)#累加大小
    if(size > var_set.free_space*1024*1024):  #判断是否超过设定大小
        print("space size:"+str(size))
        return True
    else:
        return False

#检查已使用空间，并在超过时，自动删除缓存的视频
def clean_files():
    is_boom = True  #用来判断可用空间是否爆炸
    if(check_free()):  #检查已用空间是否超过设置大小
        files = os.listdir(path+'/default_mp3') #获取下载文件夹下所有文件
        files.sort()    #排序文件，以便按日期删除多余文件
        for f in files:
            if((f.find('.flv') != -1) & (check_free())):    #检查可用空间是否依旧超过设置大小，flv文件
                del_file_default_mp3(f)   #删除文件
            elif((f.find('.mp3') != -1) & (check_free())):    #检查可用空间是否依旧超过设置大小，mp3文件
                del_file_default_mp3(f)   #删除文件
                del_file_default_mp3(f.replace(".mp3",'')+'.ass')
                del_file_default_mp3(f.replace(".mp3",'')+'.info')
            elif(check_free() == False):    #符合空间大小占用设置时，停止删除操作
                is_boom = False
    else:
        is_boom = False
    return is_boom

#用于删除文件，防止报错
def del_file(f):
    try:
        print('delete'+path+'/downloads/'+f)
        os.remove(path+'/downloads/'+f)
    except:
        print('delete error')

#用于删除文件，防止报错
def del_file_default_mp3(f):
    try:
        print('delete'+path+'/default_mp3/'+f)
        os.remove(path+'/default_mp3/'+f)
    except:
        print('delete error')


#下载b站任意视频，传入值：网址、点播人用户名
def download_av(video_url,user):
    ydl_opts = {
        'outtmpl': 'path+/downloads/%(id)s.%(ext)s',        # outtmpl 格式化下载后的文件名,自定义文件保存路径
        'format': 'best'                                 #首选下载视频质量
        }
    if(clean_files()):  #检查空间是否在设定值以内，并自动删除多余视频缓存
        send_dm_long('空间已爆炸，请联系up')
        return
    
    print('[log]downloading bilibili video:'+str(video_url))
    send_dm('注意，视频下载十分费时，请耐心等待')
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    send_dm_long('下载完成，已加入播放列表')
    #send_dm('注意，视频下载十分费时，请耐心等待')



#获取赠送过的瓜子数量
def get_coin(user):
    gift_count = 0
    try:
        gift_count = numpy.load('users/'+user+'.npy')
    except:
        gift_count = 0
    return gift_count

#扣除赠送过的瓜子数量
def take_coin(user, take_sum):
    gift_count = 0
    try:
        gift_count = numpy.load('users/'+user+'.npy')
    except:
        gift_count = 0
    gift_count = gift_count - take_sum
    try:
        numpy.save('users/'+user+'.npy', gift_count)
    except:
        print('create error')

#检查并扣除指定数量的瓜子
def check_coin(user, take_sum):
    if get_coin(user) >= take_sum:
        take_coin(user, take_sum)
        return True
    else:
        return False

#给予赠送过的瓜子数量
def give_coin(user, give_sum):
    gift_count = 0
    try:
        gift_count = numpy.load('users/'+user+'.npy')
    except:
        gift_count = 0
    gift_count = gift_count + give_sum
    try:
        numpy.save('users/'+user+'.npy', gift_count)
    except:
        print('create error')


#切歌请求次数统计
jump_to_next_counter = 1
rp_lock = False
def pick_msg(s, user):
    global jump_to_next_counter #切歌请求次数统计
    global encode_lock  #视频渲染任务锁
    global rp_lock
    
    if((user == '酷瓦酷吧') | rp_lock):  #防止自循环
        return

    elif (s.find('喵') > -1):
        replay = ["喵？？", "喵喵！", "喵。。喵？", "喵喵喵~", "喵！"]
        send_dm_long(replay[random.randint(0, len(replay)-1)])  #用于测试是否崩掉
    elif (s == '切歌'):   #切歌请求

        if(user=='南冥以南'): #debug使用，请自己修改
            jump_to_next_counter=5
        if(jump_to_next_counter < 5):   #次数未达到五次
            send_dm_long('已收到'+str(jump_to_next_counter)+'次切歌请求，达到五次将切歌')
            jump_to_next_counter = jump_to_next_counter + 1
        else:   #次数达到五次
            jump_to_next_counter = 0    #次数统计清零
            send_dm_long('已执行切歌动作')
            os.system('killall ffmpeg') #强行结束ffmpeg进程
    elif (s == 'hello'):      
            send_dm_long('下一刻，更精彩')
            
    elif (s.find('av') == 0):
        s = s.replace(' ', '')   #剔除弹幕中的所有空格
        try:
            if(s.find('p') == -1):
                send_dm_long('已收到'+user+'的指令')
                #视频网址格式：https://www.bilibili.com/video/avxxxxx
                ture_url=s.replace('av','https://www.bilibili.com/video/av')
                print(ture_url)
                _thread.start_new_thread(download_av, (ture_url,user))
            else:
                send_dm_long('已收到'+user+'的指令')
                #视频网址格式：https://www.bilibili.com/video/avxxxx/#page=x
                ture_url=s.replace('p','/#page=')
                ture_url=ture_url.replace('av','https://www.bilibili.com/video/av')
                _thread.start_new_thread(download_av, (ture_url,user))
        except:
            print('[log]video not found')
    elif (s.find('查询') == 0):
        send_dm_long(user+'的瓜子余额还剩'+str(get_coin(user))+'个')
    # else:
    #     print('not match anything')





#发送弹幕函数，通过post完成，具体可以自行使用浏览器，进入审查元素，监控network选项卡研究
def send_dm(s):
    global cookie
    global roomid
    global dm_lock
    global csrf_token
    while (dm_lock):
        #print('[log]wait for send dm')
        time.sleep(1)
    dm_lock = True
    try:
        url = "https://api.live.bilibili.com/msg/send"
        postdata =urllib.parse.urlencode({
        'color':'16777215',
        'fontsize':'25',
        'mode':'1',
        'msg':s,
        'rnd':str(int(time.time())),
        'roomid':roomid,
        'csrf_token':csrf_token,
        'csrf':csrf_token
        }).encode('utf-8')
        header = {
        "Accept":"application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding":"utf-8",
        "Accept-Language":"zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3",
        "Connection":"keep-alive",
        "Cookie":cookie,
        "Host":"api.live.bilibili.com",
        "Referer":"http://live.bilibili.com/"+roomid,
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36 Vivaldi/2.2.1388.37"
        }
        req = urllib.request.Request(url,postdata,header)
        dm_result = json.loads(urllib.request.urlopen(req,timeout=3).read().decode('utf-8'))
        if len(dm_result['msg']) > 0:
            print('[error]弹幕发送失败：'+s)
            print(dm_result)
        else:
            print('[log]发送弹幕：'+s)
    except Exception as e:
        print('[error]send dm error')
        print(e)
    time.sleep(1.5)
    dm_lock = False

#每条弹幕最长只能发送20字符，过长的弹幕分段发送
def send_dm_long(s):
    n=var_set.dm_size
    for hx in sensitive_word:                  #处理和谐词，防止点播机的回复被和谐
        if (s.find(hx) > -1):
            s = s.replace(hx, hx[0]+"-"+hx[1:])    #在和谐词第一个字符后加上一个空格
    for i in range(0, len(s), n):
        send_dm(s[i:i+n])

#获取原始弹幕数组
#本函数不作注释，具体也请自己通过浏览器审查元素研究
def get_dm():
    global temp_dm
    global roomid
    global csrf_token
    url = "http://api.live.bilibili.com/ajax/msg"
    postdata =urllib.parse.urlencode({
    'token:':'',
    'csrf_token:':csrf_token,
    'roomid':roomid
    }).encode('utf-8')
    header = {
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding":"utf-8",
    "Accept-Language":"zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3",
    "Connection":"keep-alive",
    "Host":"api.live.bilibili.com",
    "Referer":"http://live.bilibili.com/"+roomid,
    "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:32.0) Gecko/20100101 Firefox/32.0"
    }
    req = urllib.request.Request(url,postdata,header)
    dm_result = json.loads(urllib.request.urlopen(req,timeout=1).read().decode('utf-8'))
    #for t_get in dm_result['data']['room']:
        #print('[log]['+t_get['timeline']+']'+t_get['nickname']+':'+t_get['text'])
    return dm_result

#检查某弹幕是否与前一次获取的弹幕数组有重复
def check_dm(dm):
    global temp_dm
    for t_get in temp_dm['data']['room']:
        if((t_get['text'] == dm['text']) & (t_get['timeline'] == dm['timeline'])):
            return False
    return True

#弹幕获取函数，原理为不断循环获取指定直播间的初始弹幕，并剔除前一次已经获取到的弹幕，余下的即为新弹幕
def get_dm_loop():
    global temp_dm
    temp_dm = get_dm()
    while True:
        dm_result = get_dm()
        for t_get in dm_result['data']['room']:
            if(check_dm(t_get)):
                print('[log]['+t_get['timeline']+']'+t_get['nickname']+':'+t_get['text'])
                #send_dm('用户'+t_get['nickname']+'发送了'+t_get['text']) #别开，会死循环
                text = t_get['text']
                pick_msg(text,t_get['nickname'])   #新弹幕检测是否匹配为命令
        temp_dm = dm_result
        time.sleep(1)

def test():
    print('ok')

print('程序已启动，连接房间id：'+roomid)
send_dm_long('弹幕监控已启动，可以点歌了')
# while True: #防炸
#     try:
#         get_dm_loop()   #开启弹幕获取循环函数
#     except Exception as e:  #防炸
#         print('shit')
#         print(e)
#         dm_lock = False #解开弹幕锁，以免因炸了而导致弹幕锁没解开，进而导致一直锁着发不出弹幕
