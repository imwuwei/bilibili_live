import os
import youtube_dl
import ffmpegService
from queue import deque
import time
import ass_maker
from ffmpy3 import FFmpeg
from config import path



# 设置下载列表为DOWNLOADLST,并设置为全局变量
# 将DOWNLOADLST设置为队列
DOWNLOADlIST = deque()
# 全局渲染锁
ENCODE_LOOK=False

# 设置播放列表为play_list
play_list = deque()



def videoDL(url):
    try:
        ydl_opts = {
            # outtmpl 格式化下载后的文件名,自定义文件保存路径
            'outtmpl': path + 'downloads/av%(id)s-%(title)s.%(ext)s',
            # 首选下载视频质量
            'format': 'best'
        }
        print(url)
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(e)


def downloader(avid1, user1):
    # 设置全局变量ENCODE_LOOK为渲染锁，默认值为False，保证同一时间只有一个视频在渲染
    global ENCODE_LOOK
    # 下载列表 DOWNLOADlIST 
    global DOWNLOADlIST
    # 播放列表
    global play_list
    try:
        DOWNLOADlIST.append(tuple([avid1, user1]))
        while DOWNLOADlIST:
            # 检查全局渲染锁是否上锁
            while ENCODE_LOOK:
                time.sleep(5)
            lst = DOWNLOADlIST.popleft()
            avid = lst[0]
            user = lst[1]
            
            # 构造url，调用videoDL下载视频
            url = "https://www.bilibili.com/video/" + str(avid)
            videoDL(url)
            print(url+"\n视频下载完成")

            # 因为不知道视频标题，所以暂时只能通过遍历文件列表，然后通过avid匹配
            video_list = os.listdir(path + "downloads/")
            # 遍历文件列表，获取下载完成的视频文件名，然后渲染
            for filename in video_list:
                if filename.find(avid) == 0:
                    ENCODE_LOOK = True
                    print("视频加入渲染列表")
                    # 调用ffmpegService.videoRender，渲染视频
                    ffmpegService.videoRender(filename, avid, user)
                    ENCODE_LOOK = False
                    print(filename+"渲染完成")
                    # 视频渲染完成后加入播放列表
                    play_list.append("ok"+avid+".flv")
                    break
                    
    except Exception as e:
        print(e)
        