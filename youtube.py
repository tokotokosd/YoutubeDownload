# -*- coding: utf-8 -*-
import os
import pafy
import youtube_dl
import configparser

pafy.set_api_key("AIzaSyDRltTioQ75l_55v9aPVvUrNO-4seYm55M")

config = configparser.ConfigParser()
config.read('Config.ini')
playlists_url = config['DEFAULT']['playlists_url'].split(";")
video_urls = config['DEFAULT']['video_urls'].split(";")
download_path = config['DEFAULT']['download_path']
qual = config['DEFAULT']['Enter the video quality (4k,1080,720,480,360,240,144)']


def download(url: str, options: dict):
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([url])

def download_playlist(url, download_path):
    playlist = []

    try:
        playlist1 = pafy.get_playlist2(url)
    except:
        print("An exception occured while downloading the playlist. Error: Unable to fetch data from the error or the link is not valid.")
        exit()

    path = os.path.join(download_path, playlist1.title)
    # create dir
    try:
        os.mkdir(path)
    except:
        pass
    download_path = path

    for links in playlist1:
        y_url = links.watchv_url
        playlist.append(y_url)

    vquality=  {'audio' :'140', '144' : '160', '240' : '133', '360' : '134', '480' : '135', '720' : '136', '1080' : '137','4k':'313'}
    playlist = sorted(set(playlist), key = playlist.index)
    tuple_format = vquality[qual]

    for cur_data in playlist:
        cur_url = cur_data
        fmt_name, fmt = qual, tuple_format
        try:
            download(cur_url, dict(format=fmt+'+140',
                                    outtmpl=os.path.join(download_path, f'%(title)s-{fmt_name}.%(ext)s'),
                                    # ignoreerrors=True,
                                    # quiet=True
                                    ))
        except youtube_dl.utils.DownloadError:
            print(f'download error: {cur_url} | {fmt_name}')
            try:
                download(cur_url, dict(format='bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio',
                                       outtmpl=os.path.join(download_path, f'%(title)s-best.mp4'),
                                       # ignoreerrors=True,
                                       # quiet=True
                                       ))
            except:
                pass

def download_video(url, download_path):
    vquality=  {'audio' :'140', '144' : '160', '240' : '133', '360' : '134', '480' : '135', '720' : '136', '1080' : '137','4k':'313'}
    tuple_format = vquality[qual]
    cur_url = url
    fmt_name, fmt = qual, tuple_format
    try:
        download(cur_url, dict(format=fmt + '+140',
                               outtmpl=os.path.join(download_path, f'%(title)s-{fmt_name}.%(ext)s'),
                               # ignoreerrors=True,
                               # quiet=True
                               ))
    except youtube_dl.utils.DownloadError:
        print(f'download error: {cur_url} | {fmt_name}')
        try:
            download(cur_url, dict(format='bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio',
                                   outtmpl=os.path.join(download_path, f'%(title)s-best.mp4'),
                                   # ignoreerrors=True,
                                   # quiet=True
                                   ))
        except:
            pass

for i in playlists_url:
    if i == "":
        break
    download_playlist(i, download_path)

for i in video_urls:
    download_video(i, download_path)