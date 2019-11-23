#!/usr/bin/python3
import os
import threading
import time
import getVideo
import ffmpegService
from queue import deque
from dmReceive import getDmLoop
from config import path

play_list = getVideo.play_list

def push_video():
    """
        直播推流模块，主要是将渲染完成和缓存的视频文件通过ffmpegService.ffmpegPush推送到直播服务器
        通过检查队列play_list是否为空来判断播放列表含有新的点播
        视频渲染完成后自动加入play_list
    """
    global play_list
    while 1:
        while play_list:
            Current_play = play_list.popleft()
            ffmpegService.ffmpegPush(Current_play)
        else:
            filename = os.listdir(path+"downloads/")
            for video in filename:
                if play_list:
                    break
                elif os.path.splitext(video)[-1] == ".flv":
                    ffmpegService.ffmpegPush(video)

                   
if __name__ == "__main__":
    threading.Thread(target=getDmLoop).start()
    threading.Thread(target=push_video).start()

    
 