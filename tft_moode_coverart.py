#!/bin/env python3

from PIL import Image, ImageDraw, ImageColor, ImageFont, ImageStat
import subprocess
import time
import musicpd
import os
import os.path
# import RPi.GPIO as GPIO
from mediafile import MediaFile
from io import BytesIO
from numpy import mean
import ST7789
from PIL import ImageFilter
import yaml

# set default config for pirate audio

__version__ = "0.0.7"

# get the path of the script
script_path = os.path.dirname(os.path.abspath( __file__ ))
# set script path as current directory
os.chdir(script_path)

OVERLAY=3
TIMEBAR=1
TEXT=1
SHADOW=3
EMBCOVERPRIO=1
MODE=0
BLANK=0

confile = "config.yml"

# Read config.yml for user config
if os.path.exists(confile):

    with open(confile) as config_file:
        data = yaml.load(config_file, Loader=yaml.FullLoader)
        displayConf = data["display"]
        OVERLAY = displayConf["overlay"]
        TIMEBAR = displayConf["timebar"]
        TEXT = displayConf["text"]
        SHADOW = displayConf["shadow"]
        EMBCOVERPRIO = displayConf["embcoverprio"]
        MODE = displayConf["mode"]
        BLANK = displayConf["blank"]


# Standard SPI connections for ST7789
# Create ST7789 LCD display class
if MODE == 3:
    disp = ST7789.ST7789(
        port=0,
        cs=ST7789.BG_SPI_CS_FRONT,  # GPIO 8, Physical pin 24
        dc=9,
        rst=22,
        backlight=13,
        mode=3,
        rotation=0,
        spi_speed_hz=80 * 1000 * 1000
    )
else:
    disp = ST7789.ST7789(
        port=0,
        cs=ST7789.BG_SPI_CS_FRONT,  # GPIO 8, Physical pin 24
        dc=9,
        backlight=13,
        spi_speed_hz=80 * 1000 * 1000
    )

# FIXME: this prevents MPD from detecting buttons state, so we cannot use it
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(6, GPIO.IN)
# GPIO.setup(24, GPIO.IN)

WIDTH = 240
HEIGHT = 240
font_s = ImageFont.truetype(script_path + "/fonts/Roboto-Medium.ttf", 20)
font_m = ImageFont.truetype(script_path + "/fonts/Roboto-Medium.ttf", 24)
font_l = ImageFont.truetype(script_path + "/fonts/Roboto-Medium.ttf", 28)

img = Image.new("RGB", (240, 240), color=(0, 0, 0, 25))
draw = ImageDraw.Draw(img, "RGBA")

play_icons = Image.open(script_path + "/images/controls-play.png").resize((240,240), resample=Image.LANCZOS).convert("RGBA")
play_icons_dark = Image.open(script_path + "/images/controls-play-dark.png").resize((240,240), resample=Image.LANCZOS).convert("RGBA")

pause_icons = Image.open(script_path + "/images/controls-pause.png").resize((240,240), resample=Image.LANCZOS).convert("RGBA")
pause_icons_dark = Image.open(script_path + "/images/controls-pause-dark.png").resize((240,240), resample=Image.LANCZOS).convert("RGBA")

vol_icons = Image.open(script_path + "/images/controls-vol.png").resize((240,240), resample=Image.LANCZOS).convert("RGBA")
vol_icons_dark = Image.open(script_path + "/images/controls-vol-dark.png").resize((240,240), resample=Image.LANCZOS).convert("RGBA")

df_back = Image.open(script_path + "/images/default-cover-v6.jpg")  # resized later
bt_back = Image.open(script_path + "/images/bta.png").resize((240,240), resample=Image.LANCZOS).convert("RGBA")
ap_back = Image.open(script_path + "/images/airplay.png").resize((240,240), resample=Image.LANCZOS).convert("RGBA")
sp_back = Image.open(script_path + "/images/spotify.png").resize((240,240), resample=Image.LANCZOS).convert("RGBA")
sq_back = Image.open(script_path + "/images/squeeze.png").resize((240,240), resample=Image.LANCZOS).convert("RGBA")
jp_back = Image.open(script_path + "/images/jack.png").resize((240,240), resample=Image.LANCZOS).convert("RGBA")


def is_service_active(service):

    waiting = True
    count = 0
    active = False

    while (waiting == True):

        process = subprocess.run(["systemctl", "is-active", service], check=False, stdout=subprocess.PIPE, universal_newlines=True)
        output = process.stdout
        stat = output[:6]

        if stat == "active":
            waiting = False
            active = True

        if count > 14:
            waiting = False

        count += 1
        time.sleep(2)

    return active


def get_moode_metadata(filename):

    metaDict = {}

    if os.path.exists(filename):
        # add each line to a list removing newline
        nowplayingmeta = [line.rstrip("\n") for line in open(filename)]
        i = 0
        while i < len(nowplayingmeta):
            # traverse list converting to a dictionary
            (key, value) = nowplayingmeta[i].split("=", 1)
            metaDict[key] = value
            i += 1

    return metaDict


def get_cover_filepath(metaDict):

    result = "default"

    if "source" in metaDict:
        if metaDict["source"] == "radio":
            if "coverurl" in metaDict:
                result = "/var/local/www/" + metaDict["coverurl"]
        elif metaDict["source"] == "bluetooth":
            result = "bluetooth"
        elif metaDict["source"] == "airplay":
            result = "airplay"
        elif metaDict["source"] == "spotify":
            result = "spotify"
        elif metaDict["source"] == "squeeze":
            result = "squeeze"
        elif metaDict["source"] == "input":
            result = "input"
        else:  # source: library
            if "file" in metaDict:
                if len(metaDict["file"]) > 0:
                    result = "/var/lib/mpd/music/" + metaDict["file"]

    return result


def get_cover(metaDict):

    result = df_back
    covers = ["Cover.jpg", "cover.jpg", "Cover.jpeg", "cover.jpeg", "Cover.png", "cover.png", "Cover.tif", "cover.tif", "Cover.tiff", "cover.tiff",
            "Folder.jpg", "folder.jpg", "Folder.jpeg", "folder.jpeg", "Folder.png", "folder.png", "Folder.tif", "folder.tif", "Folder.tiff", "folder.tiff"]

    if "source" in metaDict:
        if metaDict["source"] == "radio":
            if "coverurl" in metaDict:
                rc = "/var/local/www/" + metaDict["coverurl"]
                if os.path.exists(rc):
                    if rc != "/var/local/www/images/default-cover-v6.svg":
                        result = Image.open(rc)
        elif metaDict["source"] == "bluetooth":
            result = bt_back
        elif metaDict["source"] == "airplay":
            result = ap_back
        elif metaDict["source"] == "spotify":
            result = sp_back
        elif metaDict["source"] == "squeeze":
            result = sq_back
        elif metaDict["source"] == "input":
            result = jp_back
        else:  # source: library
            if "file" in metaDict:
                if len(metaDict["file"]) > 0:
                    fp = "/var/lib/mpd/music/" + metaDict["file"]
                    coverok = False
                    # depending on cfg., try the embedded / folder's cover 1st
                    if EMBCOVERPRIO == 1:
                        mf = MediaFile(fp)
                        if mf.art:
                            result = Image.open(BytesIO(mf.art))
                            coverok = True
                    if not coverok:
                        for it in covers:
                            cp = os.path.dirname(fp) + "/" + it
                            if os.path.exists(cp):
                                result = Image.open(cp)
                                coverok = True
                                break
                    if not coverok and EMBCOVERPRIO == 0:
                        mf = MediaFile(fp)
                        if mf.art:
                            result = Image.open(BytesIO(mf.art))

    # return filename and image for cover (tuple)
    return result


def main():

    # Initialize display
    disp.begin()

    disp.set_backlight(True)

    filename = "/var/local/www/currentsong.txt"

    c = 0
    ss = 0
    x1 = 20
    x2 = 20
    x3 = 20
    mn = 50
    artist_top = 7
    album_top = 35
    title_top = 105
    volume_top = 184
    time_top = 222
    act_mpd = is_service_active("mpd")
    cover = None
    oldcover = None
    oldcovername = ""

    if act_mpd == True:
        while True:
            client = musicpd.MPDClient()  # create client object
            try:
                client.connect()  # use MPD_HOST/MPD_PORT
            except KeyboardInterrupt:
                raise
            except:
                time.sleep(2)
                pass
            else:
                try:
                    # moode_meta = get_moode_metadata(filename)
                    moode_meta = client.currentsong()
                    # print(moode_meta)

                    moode_meta["source"] = "library"
                    if "file" in moode_meta:
                        if (moode_meta["file"].find("http://", 0) > -1) or (moode_meta["file"].find("https://", 0) > -1):
                            # set radio stream to true
                            moode_meta["source"] = "radio"
                            # if radio station has arist and title in one line separated by a hyphen, split into correct keys
                            if moode_meta["title"].find(" - ", 0) > -1:
                                (art, tit) = moode_meta["title"].split(" - ", 1)
                                moode_meta["artist"] = art
                                moode_meta["title"] = tit
                        elif moode_meta["file"].find("Bluetooth Active", 0) > -1:
                            moode_meta["source"] = "bluetooth"
                        elif moode_meta["file"].find("Airplay Active", 0) > -1:
                            moode_meta["source"] = "airplay"
                        elif moode_meta["file"].find("Spotify Active", 0) > -1:
                            moode_meta["source"] = "spotify"
                        elif moode_meta["file"].find("Squeezelite Active", 0) > -1:
                            moode_meta["source"] = "squeeze"
                        elif moode_meta["file"].find("Input Active", 0) > -1:
                            moode_meta["source"] = "input"

                    mpd_status = client.status()
                    # print(mpd_status)
                    # print()

                    # avoid re-reading the previous image again
                    covername = get_cover_filepath(moode_meta)
                    if (covername != oldcovername):
                        oldcovername = covername
                        print("reading cover for: ", covername)
                        cover = get_cover(moode_meta)
                        oldcover = cover
                        im_stat = ImageStat.Stat(cover)
                        im_mean = im_stat.mean
                        mn = mean(im_mean)
                    else:
                        cover = oldcover

                    if TEXT == 0 or ("state" in mpd_status and mpd_status["state"] != "play"):
                        img.paste(cover.resize((WIDTH,HEIGHT), Image.LANCZOS).convert("RGB"))
                    else:
                        img.paste(cover.resize((WIDTH,HEIGHT), Image.LANCZOS).filter(ImageFilter.GaussianBlur).convert("RGB"))

                    if "state" in mpd_status:
                        if (mpd_status["state"] == "stop") and (BLANK != 0):
                            if ss < BLANK:
                                ss = ss + 1
                            else:
                                disp.set_backlight(False)
                        else:
                            ss = 0
                            disp.set_backlight(True)

                    # txt_col = (255-int(im_mean[0]), 255-int(im_mean[1]), 255-int(im_mean[2]))
                    txt_col = (255,255,255)
                    shd_col = (15,15,15)
                    bar_col = (255, 255, 255, 255)
                    dark = False
                    if mn > 175:
                        txt_col = (55,55,55)
                        shd_col = (200,200,200)
                        dark=True
                        bar_col = (100,100,100,225)
                    if mn < 80:
                        txt_col = (200,200,200)
                        shd_col = (55,55,55)

                    if (moode_meta["source"] == "library") or (moode_meta["source"] == "radio"):

                        if (OVERLAY > 0):
                            if "state" in mpd_status:
                                if OVERLAY == 3 or OVERLAY == 2:
                                    if mpd_status["state"] != "play":
                                        if dark is False:
                                            img.paste(play_icons, (0,0), play_icons)
                                        else:
                                            img.paste(play_icons_dark, (0,0), play_icons_dark)
                                    else:
                                        if dark is False:
                                            img.paste(pause_icons, (0,0), pause_icons)
                                        else:
                                            img.paste(pause_icons_dark, (0,0), pause_icons_dark)
                                # FIXME: this prevents MPD from detecting buttons state, so we cannot use it
                                # volume_pressed = GPIO.input(6) or GPIO.input(24)
                                if (((OVERLAY == 3 or OVERLAY == 1) and "state" in mpd_status and mpd_status["state"] == "play")
                                        or False): # volume_pressed):
                                    # FIXME: this would draw the volume icon twice, since it is in the play_icons image too!
                                    # if dark is False:
                                    #     img.paste(vol_icons, (0,0), vol_icons)
                                    # else:
                                    #     img.paste(vol_icons_dark, (0,0), vol_icons_dark)
                                    if "volume" in mpd_status:
                                        vol = int(mpd_status["volume"])
                                        vol_x = 5 + int((vol/100)*(WIDTH - 40))
                                        draw.rectangle((5, volume_top, WIDTH-35, volume_top+8), (255,255,255,145))
                                        draw.rectangle((5, volume_top, vol_x, volume_top+8), bar_col)
                            else:
                                img.paste(play_icons, (0,0), play_icons)

                        if TIMEBAR == 1 and ("state" in mpd_status and mpd_status["state"] == "play"):
                            if "elapsed" in mpd_status:
                                el_time = int(float(mpd_status["elapsed"]))
                                if "duration" in mpd_status:
                                    du_time = int(float(mpd_status["duration"]))
                                    dur_x = 5 + int((el_time/du_time)*(WIDTH-10))
                                    print (el_time, du_time, dur_x)
                                    draw.rectangle((5, time_top, WIDTH-5, time_top + 12), (255,255,255,145))
                                    draw.rectangle((5, time_top, dur_x, time_top + 12), bar_col)

                        if TEXT == 1 and ("state" in mpd_status and mpd_status["state"] == "play"):
                            if "artist" in moode_meta:
                                w1, y1 = draw.textsize(moode_meta["artist"], font_m)
                                x1 = x1-20
                                if x1 < (WIDTH - w1 - 220):
                                    x1 = 220
                                if w1 <= WIDTH:
                                    x1 = (WIDTH - w1)//2
                                if SHADOW != 0:
                                    draw.text((x1+SHADOW, artist_top+SHADOW), moode_meta["artist"], font=font_m, fill=shd_col)
                                draw.text((x1, artist_top), moode_meta["artist"], font=font_m, fill=txt_col)

                            if "album" in moode_meta:
                                w2, y2 = draw.textsize(moode_meta["album"], font_s)
                                x2 = x2-20
                                if x2 < (WIDTH - w2 - 220):
                                    x2 = 220
                                if w2 <= WIDTH:
                                    x2 = (WIDTH - w2)//2
                                if SHADOW != 0:
                                    draw.text((x2+SHADOW, album_top+SHADOW), moode_meta["album"], font=font_s, fill=shd_col)
                                draw.text((x2, album_top), moode_meta["album"], font=font_s, fill=txt_col)

                            if "title" in moode_meta:
                                w3, y3 = draw.textsize(moode_meta["title"], font_l)
                                x3 = x3-20
                                if x3 < (WIDTH - w3 - 220):
                                    x3 = 220
                                if w3 <= WIDTH:
                                    x3 = (WIDTH - w3)//2
                                if SHADOW != 0:
                                    draw.text((x3+SHADOW, title_top+SHADOW), moode_meta["title"], font=font_l, fill=shd_col)
                                draw.text((x3, title_top), moode_meta["title"], font=font_l, fill=txt_col)

                    else:  # corresponds to: if (moode_meta["source"] == "library") or (moode_meta["source"] == "radio"):
                        if "file" in moode_meta:
                            txt = moode_meta["file"].replace(" ", "\n")
                            w3, h3 = draw.multiline_textsize(txt, font_l, spacing=6)
                            x3 = (WIDTH - w3)//2
                            y3 = (HEIGHT - h3)//2
                            if SHADOW != 0:
                                draw.text((x3+SHADOW, y3+SHADOW), txt, font=font_l, fill=shd_col)
                            draw.text((x3, y3), txt, font=font_l, fill=txt_col, spacing=6, align="center")

                    disp.display(img)

                    if c == 0:
                        # im7 = img.save(script_path + "/dump.jpg")
                        c += 1

                    if ("state" in mpd_status and mpd_status["state"] == "play"):
                        time.sleep(0.25)
                    else:
                        time.sleep(0.5)

                except KeyboardInterrupt:
                    raise
                except BaseException as e:
                    print(e)
                    time.sleep(2)

    else:  # act_mpd != True:

        draw.rectangle((0,0,240,240), fill=(0,0,0))
        txt = "MPD not Active!\nEnsure MPD is running\nThen restart script"
        mlw, mlh = draw.multiline_textsize(txt, font=font_m, spacing=4)
        draw.multiline_text(((WIDTH-mlw)//2, 20), txt, fill=(255,255,255), font=font_m, spacing=4, align="center")
        disp.display(img)


if __name__ == "__main__":

    try:
        main()
    except KeyboardInterrupt:
        disp.reset()
        disp.set_backlight(False)
        pass

