import cv2
from time import sleep
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from io import BytesIO
import requests
from PIL import Image, ImageDraw, ImageFont
import os.path
import tkinter
import pygame
from pygame.locals import *



CLIENT_ID="2b8c0c3f3f5e4f7b928669eef98a3702"
CLIENT_SECRET="b6066b1890f84964a3276a872bef4593"


lastUrl = ""
lastSong = ""
LOCAL_PATH = "C:/Users/kirby/OneDrive/Documents/JavaScript/NodeJs/wallpaperTest/PiTest"

pygame.init()
WIDTH = 2560
HEIGHT = 1440
windowSurface = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
backgroundImage = pygame.image.load("background.png")

# cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
# cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
# if not None is None:
#     cv2.imshow("window", cv2.imread('background.png', 0))
# else:
#     cv2.imshow("window", cv2.imread('background.png', 0))
# if cv2.waitKey(1) == 27:
#     cv2.destroyAllWindows()
#     pass

# img = cv2.imread('wallpaperNew.jpg', 0)

def showImage():
    global backgroundImage
    # img = cv2.imread('wallpaperNew.jpg')
    # pass
    # cv2.waitKey(0)
    backgroundImage = pygame.image.load("wallpaperNew.jpg")

def getImg(url):
    res = requests.get(url)
    return Image.open(BytesIO(res.content))

def isInRange(color1, color2, target):
    return abs(color1[0] - color2[0]) >= target or abs(color1[1] - color2[1]) >= target or abs(color1[2] - color2[2]) >= target

def sortSecond(val):
    return val[1]

def isBright(color, threshold):
    return color[0] > threshold or color[1] > threshold or color[2] > threshold

def getImgColor(img):
    try:
        colors = []
        pixels = img.load()
        width, height = img.size
        for y in range(round(height/5)):
            for x in range(round(width/5)):
                r, g, b = pixels[round(x*5), round(y*5)]
                curColors = [r, g, b]
                if len(colors) == 0 and isBright(curColors, 150):
                    colors.append([[r, g, b], 1])
                else:
                    count = 0
                    for i in range(len(colors)):
                        if isInRange(curColors, colors[i][0], 70):
                            count += 1
                        else: 
                            colors[i][1] += 1
                    if count == len(colors) and isBright(curColors, 90):
                        colors.append([[r, g, b], 1])
        colors.sort(key=sortSecond, reverse=True)
        if (len(colors) == 0): return (120, 120, 120)
        return colors[0][0]
    except Exception as e:
        pass

def changeImage(url, smallUrl, songName, albumName, artistName):
    img = getImg(url)
    defaultImage = Image.open('./background.png')
    widthD, heightD = defaultImage.size
    widthI, heightI = img.size

    offsetHeight = (heightD / 2) - (heightI / 2)
    offsetWidth = (widthD / 2) - (widthI / 2)

    pixels = img.load()
    color = getImgColor(getImg(smallUrl))

    rTest, gTest, bTest, aTest = defaultImage.split()
    rTest = rTest.point(lambda i: i * (color[0]/220))
    gTest = gTest.point(lambda i: i * (color[1]/220))
    bTest = bTest.point(lambda i: i * (color[2]/220))
    defaultImage = Image.merge('RGB', (rTest, gTest, bTest))

    savePixels = defaultImage.load()
    for x in range(widthI):
        for y in range(heightI):
            savePixels[x + offsetWidth, y + offsetHeight] = pixels[x, y]
    
    defaultImage.save('wallpaperNew.jpg', compression_level=0)
    sleep(1)
    showImage()




while True:

    try: 
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                       client_secret=CLIENT_SECRET,
                                                       redirect_uri="http://localhost/redirect",
                                                       scope=["user-read-currently-playing", "user-read-playback-state"]))
        while True:
            events = pygame.event.get()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    # sys.exit()
            windowSurface.blit(backgroundImage, (0, 0)) #Replace (0, 0) with desired coordinates
            pygame.display.flip()

            songInfo = sp.current_user_playing_track()

            artists = songInfo["item"]["artists"]
            artistNames = []
            for i in range(len(artists)):
                artistNames.append(artists[i]["name"])
            artistName = ', '.join(artistNames)

            albumName = songInfo["item"]["album"]["name"]

            songName = songInfo["item"]["name"]

            albumCover = songInfo["item"]["album"]["images"]
            albumCoverUrl = albumCover[0]["url"]
            isPlaying = sp.current_playback()["is_playing"]
            # print(songName)

            if ((albumCoverUrl != lastUrl) or (songName != lastSong)) and isPlaying:
                print(songName, albumName, artistNames)
                changeImage(albumCoverUrl, albumCover[2]["url"], songName, albumName, artistName)
                lastUrl = albumCoverUrl
                lastSong = songName
                print("|---------------------|")
            elif lastUrl != "paused" and not isPlaying:
                lastUrl = "paused"
                # subprocess.call(["powershell.exe", '-ExecutionPolicy', 'Unrestricted', "-File", LOCAL_PATH + "wallpaperChange.ps1", LOCAL_PATH + "dualWallpaper/dualMonitorPaused.png"])
                # ctypes.windll.user32.SystemParametersInfoW(20, 0, LOCAL_PATH + "dualWallpaper/dualMonitorPaused.png", 3)
            sleep(0.5)

    except Exception as e:
        pass