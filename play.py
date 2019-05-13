#coding:utf-8
import os
import sys
import time
import var_set
import shutil


path = var_set.path                             #引入设置路径
rtmp = var_set.rtmp                             #引入设置的rtmp网址
live_code = var_set.live_code                   #引入设置rtmp参数


while True:
    try:   
        files = os.listdir(path+'/downloads')   #获取download下的所有文件
        files_defvideo = os.listdir(path+'/default_video')   

        if not os.listdir(path+'/downloads'):
            files_defvideo.sort()
            #print(files_defvideo)
            for f in files_defvideo:
                if  os.listdir(path+'/downloads'):
                        break
                elif((f.find('.flv') != -1) and (f.find('.default_video') == -1)): #如果是flv文件
                    #print('ffmpeg  -re -i "'+path+"/default_video/"+f+'" -vcodec copy -acodec copy -f flv "'+rtmp+live_code+'"')
                    #print(path+'/default_video/'+f)
                    #time.sleep(5)
                    os.system('ffmpeg -re -i "'+path+"/default_video/"+f+'" -vcodec copy -acodec copy -f flv "'+rtmp+live_code+'"')
                    

        else: 
            files.sort()
            #print(files)
            for f in files: 
                if((f.find('.flv') != -1) and (f.find('.download') == -1)): #如果是flv文件
                    print(path+'/downloads/'+f)
                    time.sleep(5)
                    #print('ffmpeg  -re -i "'+path+"/downloads/"+f+'" -vcodec copy -acodec copy -f flv "'+rtmp+live_code+'"')
                    os.system('ffmpeg -re -i "'+path+"/downloads/"+f+'" -vcodec copy -acodec copy -f flv "'+rtmp+live_code+'"')
                    shutil.move( path+'/downloads/'+f, path+'/default_video/')


    except Exception as e:
        print(e)