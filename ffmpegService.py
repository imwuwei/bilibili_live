from ffmpy3 import FFmpeg
import ass_maker
import os
import config
import time

rtmpUrl = config.rtmp_url + config.live_code
path = config.path



# 视频推流
def ffmpegPush(filename):
    videoPath = path + "downloads/" + filename
    # Format = "-pix_fmt yuv420p -preset ultrafast -acodec copy -c:v h264  -s 1280x720  -f flv"
    Format = "-acodec copy -vcodec copy -f flv"
    try:
        ff = FFmpeg(
            inputs={videoPath: "-re"},
            outputs={rtmpUrl: Format}
        )
        print(ff.cmd)
        ff.run()
    except Exception as e:
        print(e)


# 视频渲染
def videoRender(filename, avid, user):
    print("正在生成字幕......")
    # 生成字幕并返回字幕地址
    assPath = ass_maker.make_ass(
        filename, "avid：" + str(avid) + "\\N点播人：" + user, avid=str(avid))
    print(assPath+"\n字幕生成完毕，开始渲染视频")
    videoIn = path + "downloads/" + filename
    videoOut = path + "downloads/ok" + avid + ".flv"
    Format = ['-vf', 'ass='+assPath,  '-preset', 'faster', '-c:v', 'libx264', '-vcodec', 'libx264', '-profile:v',
              'high', '-b:v', '2550k', '-maxrate', '2550k', '-bufsize', '1500k', '-acodec', 'aac', '-s', '1920x1080']
    try:
        ff = FFmpeg(
            inputs={videoIn: "-threads 1"},
            outputs={videoOut: Format}
        )
        print(ff.cmd)
        ff.run()
    except Exception as e:
        print(e)
        print("videoRender Error")
