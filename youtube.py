# -*- coding: utf-8 -*-
import os
import pafy
import youtube_dl
import configparser
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
pafy.set_api_key("AIzaSyDRltTioQ75l_55v9aPVvUrNO-4seYm55M")

config = configparser.ConfigParser()
config.read('Config.ini')
playlists_url = config['DEFAULT']['playlists_url'].split(";")
video_urls = config['DEFAULT']['video_urls'].split(";")
download_path = config['DEFAULT']['download_path']
qual = config['DEFAULT']['Enter the video quality (4k,1080,720,480,360,240,144)']


def get_videos(url):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument('log-level=3')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')
    options.add_argument("--user-agent=" + user_agent)
    options.add_argument('window-size=1920,1080')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome('chromedriver', options=options)
    #    driver = webdriver.Chrome(options=options,service_log_path='NUL')
    #    driver = webdriver.Chrome(options=options,service_log_path='/dev/null')
    driver.get(url)

    time.sleep(3)
    done = False
    while True:
        html_page = driver.page_source
        soup = BeautifulSoup(html_page, "html.parser")
        videos = []
        old_len = len(soup.findAll('a'))
        for link in soup.findAll('a'):
            video = link.get('href')
            try:
                if "watch?v=" in video and link not in videos:
                    videos.append(video)
            except:
                continue
        num = 0
        if done:
            break
        while True:
            html_page = driver.page_source
            soup = BeautifulSoup(html_page, "html.parser")
            if len(soup.findAll('a')) - 1 > old_len:
                num = 0
                break
            driver.execute_script("window.scrollBy(0, 1000000)")
            num += 1
            if num == 5:
                done = True
                break

    driver.close()
    driver.quit()
    return videos

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
                                   cookiefile="cookies.txt",
                                    nooverwrites=True,
                                    source_address='0.0.0.0',
                                    ignoreerrors=True,
                                   retries=9999
                                    # quiet=True
                                    ))
        except youtube_dl.utils.DownloadError:
            print(f'download error: {cur_url} | {fmt_name}')
            try:
                download(cur_url, dict(format='bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio',
                                       outtmpl=os.path.join(download_path, f'%(title)s-best.mp4'),
                                       cookiefile="cookies.txt",
                                        nooverwrites=True,
                                        source_address='0.0.0.0',
                                       ignoreerrors=True,
                                        retries=9999
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
                               cookiefile="cookies.txt",
                               nooverwrites=True,
                               source_address='0.0.0.0',
                                retries=9999,
                               ignoreerrors=True,
                               # quiet=True
                               ))
    except youtube_dl.utils.DownloadError:
        print(f'download error: {cur_url} | {fmt_name}')
        try:
            download(cur_url, dict(format='bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio',
                                   outtmpl=os.path.join(download_path, f'%(title)s-best.mp4'),
                                   cookiefile = "cookies.txt",
                                    nooverwrites=True,
                               source_address='0.0.0.0',
                                   ignoreerrors=True,
                                   retries=9999
                                   # quiet=True
                                   ))
        except:
            pass

for i in playlists_url:
    if i == "":
        break
    download_playlist(i, download_path)

for i in video_urls:
    if i == "":
        break
    videos = get_videos(i)
    path = os.path.join(download_path, i.replace("https://www.youtube.com/c/", "").replace("/videos", ""))
    # create dir
    try:
        os.mkdir(path)
    except:
        pass
    download_path = path
    for url in videos:
        download_video("https://www.youtube.com/" + url, download_path)