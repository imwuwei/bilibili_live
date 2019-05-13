import os
import youtube_dl

def download(video_url):
    ydl_opts = {
        'outtmpl': '\downloads\%(title)s.%(ext)s',        # outtmpl 格式化下载后的文件名,自定义文件保存路径
        'format': 'best'                                    #首选下载视频质量
        
    }
    print(video_url)


    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

if __name__ == '__main__':
    avid = input('请输入av号：')
    download('https://www.bilibili.com/video/'+avid)
    