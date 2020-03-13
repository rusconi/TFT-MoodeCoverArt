from PIL import Image, ImageDraw, ImageColor, ImageFont, ImageStat
import time
import ST7789
#import ST7735
import musicpd
import os
import os.path
from os import path
import RPi.GPIO as GPIO
from mediafile import MediaFile
from io import BytesIO
from numpy import mean 

from PIL import ImageFilter, ImageEnhance


# choose between ST7789 and ST7735 driver
# Uncomment the driver you want, comment out the other
DRIVER = 'ST7789'
#DRIVER = 'ST7735'
FULL = False

if DRIVER == 'ST7789':
        # Standard SPI connections for ST7789
        # Create ST7789 LCD display class.
        disp = ST7789.ST7789(
            port=0,
            cs=ST7789.BG_SPI_CS_FRONT,  # BG_SPI_CSB_BACK or BG_SPI_CS_FRONT
            dc=9,
            backlight=13,               # 18 for back BG slot, 19 for front BG slot.
            spi_speed_hz=80 * 1000 * 1000
        )


if DRIVER == 'ST7735':
    # Create ST7735 LCD display class. If using ST7789, delete the st7735 coding. then uncomment the ST7789
    disp = ST7735.ST7735(
        port=0,
        cs=0,   #ST7735.BG_SPI_CS_FRONT,  # BG_SPI_CSB_BACK or BG_SPI_CS_FRONT
        dc=17,
        backlight=22,               
        rst=27,
        width=128,
        height=160,
        rotation=90,
        invert=False,
        spi_speed_hz=4000000
    )
    
# Initialize display.
disp.begin()
# get the path of the script
script_path = os.path.dirname(os.path.abspath( __file__ ))

#WIDTH = disp.width
#HEIGHT = disp.height
WIDTH = 240
HEIGHT = 240
font_s = ImageFont.truetype(script_path + '/fonts/Roboto-Medium.ttf',20)
font_m = ImageFont.truetype(script_path + '/fonts/Roboto-Medium.ttf',24)
font_l = ImageFont.truetype(script_path + '/fonts/Roboto-Medium.ttf',30)

# setup gpio 22 here as output to allow it to be set as backlight later
# this stops tft displaying anything until image created and ready to display
GPIO.setup(22, GPIO.OUT)

img = Image.new('RGB', (240, 240), color=(0, 0, 0, 25))
im3 = Image.new('RGB', (160, 128), color=(0, 0, 0, 25))
om4 = Image.new('RGB', (128, 128), color=(0, 0, 0, 25))

play_icons = Image.open(script_path + '/images/controls-play.png').resize((240,240), resample=Image.LANCZOS).convert("RGBA")
play_icons_dark = Image.open(script_path + '/images/controls-play-dark.png').resize((240,240), resample=Image.LANCZOS).convert("RGBA")

pause_icons = Image.open(script_path + '/images/controls-pause.png').resize((240,240), resample=Image.LANCZOS).convert("RGBA")
pause_icons_dark = Image.open(script_path + '/images/controls-pause-dark.png').resize((240,240), resample=Image.LANCZOS).convert("RGBA")

vol_icons = Image.open(script_path + '/images/controls-vol.png').resize((240,240), resample=Image.LANCZOS).convert("RGBA")
vol_icons_dark = Image.open(script_path + '/images/controls-vol-dark.png').resize((240,240), resample=Image.LANCZOS).convert("RGBA")

draw = ImageDraw.Draw(img, 'RGBA')





def getMoodeMetadata(filename):
    # Initalise dictionary
    metaDict = {}
    
    if path.exists(filename):
        # add each line fo a list removing newline
        nowplayingmeta = [line.rstrip('\n') for line in open(filename)]
        i = 0
        while i < len(nowplayingmeta):
            # traverse list converting to a dictionary
            (key, value) = nowplayingmeta[i].split('=')
            metaDict[key] = value
            i += 1
        
        metaDict['radio'] = False
        if 'file' in metaDict:
            if metaDict['file'].find('http://', 0) > -1:
                # set radio stream to9 true
                metaDict['radio'] = True
                # if radio station has arist and title in one line separated by a hyphen, split into correct keys
                if metaDict['title'].find(' - ', 0) > -1:
                    (art,tit) = metaDict['title'].split(' - ', 1)
                    metaDict['artist'] = art
                    metaDict['title'] = tit

    # return metadata
    return metaDict

def get_cover(metaDict):

    cover = None
    cover = Image.open(script_path + '/images/default-cover-v6.jpg')
    covers = ['Cover.jpg', 'cover.jpg', 'Cover.jpeg', 'cover.jpeg', 'Cover.png', 'cover.png', 'Cover.tif', 'cover.tif', 'Cover.tiff', 'cover.tiff',
		'Folder.jpg', 'folder.jpg', 'Folder.jpeg', 'folder.jpeg', 'Folder.png', 'folder.png', 'Folder.tif', 'folder.tif', 'Folder.tiff', 'folder.tiff']
    if metaDict['radio'] is True:
        if 'coverurl' in metaDict:
            cover = Image.open('/var/www/' + metaDict['coverurl'])
    else:
        if 'file' in metaDict:
            if len(metaDict['file']) > 0:
                fp = '/mnt/' + metaDict['file']   
                mf = MediaFile(fp)     
                if mf.art:
                    cover = Image.open(BytesIO(mf.art))
                    return cover
                else:
                    for it in covers:
                        cp = os.path.dirname(fp) + '/' + it
                        
                        if path.exists(cp):
                            cover = Image.open(cp)
                            return cover
    return cover


def main():
    client = musicpd.MPDClient()       # create client object
    client.connect()                   # use MPD_HOST/MPD_PORT 

    if DRIVER == 'ST7735':
        # set gpio 22 as backlight control and turn on
        disp._backlight = 22
    
    disp.set_backlight(True)
    
    filename = '/var/local/www/currentsong.txt'

    c = 0
    p = 0
    k=0
    x1 = 20
    x2 = 20
    x3 = 20
    title_top = 105
    volume_top = 184
    time_top = 222
    if FULL == True and DRIVER == 'ST7735':
        title_top = 80
        volume_top = 136
        time_top = 174

    while True:

        moode_meta = getMoodeMetadata(filename)

        mpd_current = client.currentsong()
        mpd_status = client.status()
        cover = get_cover(moode_meta)


        
        mn = 50
        #if cover != None:
            #enhancer = ImageEnhance.Color(cover)
            #cover = enhancer.enhance(0.25)
        img.paste(cover.resize((WIDTH,HEIGHT), Image.LANCZOS).filter(ImageFilter.GaussianBlur).convert('RGB'))
            
           
        im_stat = ImageStat.Stat(cover) 
        im_mean = im_stat.mean
        mn = mean(im_mean)
        
        #txt_col = (255-int(im_mean[0]), 255-int(im_mean[1]), 255-int(im_mean[2]))
        txt_col = (255,255,255)
        bar_col = (255, 255, 255, 255)
        dark = False
        if mn > 175:
            txt_col = (55,55,55)
            dark=True
        if mn < 80:
            txt_col = (200,200,200)

        if (FULL == False and DRIVER == 'ST7735') or DRIVER == 'ST7789':
            if 'state' in mpd_status:
                if mpd_status['state'] != 'play':
                    if dark is False:
                        img.paste(pause_icons, (0,0), pause_icons)
                    else:
                        img.paste(pause_icons_dark, (0,0), pause_icons_dark)
                else:
                    if dark is False:
                        img.paste(play_icons, (0,0), play_icons)
                    else:
                        img.paste(play_icons_dark, (0,0), play_icons_dark)
            else:
                img.paste(play_icons, (0,0), play_icons)
        else:
            if dark is False:
                img.paste(vol_icons, (0,0), vol_icons)
            else:
                img.paste(vol_icons_dark, (0,0), vol_icons_dark)


        if dark is True:
            bar_col = (100,100,100,225)
        
        top = 7
        if 'artist' in moode_meta:
            w1, y1 = draw.textsize(moode_meta['artist'], font_m)
            x1 = x1-20
            if x1 < (WIDTH - w1 - 20):
                x1 = 0
            if w1 <= WIDTH:
                x1 = (WIDTH - w1)//2
            draw.text((x1, top), moode_meta['artist'], font=font_m, fill=txt_col)
        
        top = 35
        
        if 'album' in moode_meta:
            w2, y2 = draw.textsize(moode_meta['album'], font_s)
            x2 = x2-20
            if x2 < (WIDTH - w2 - 20):
                x2 = 0
            if w2 <= WIDTH:
                x2 = (WIDTH - w2)//2
            draw.text((x2, top), moode_meta['album'], font=font_s, fill=txt_col)

        
        if 'title' in moode_meta:
            w3, y3 = draw.textsize(moode_meta['title'], font_l)
            x3 = x3-20
            if x3 < (WIDTH - w3 - 20):
                x3 = 0
            if w3 <= WIDTH:
                x3 = (WIDTH - w3)//2
            draw.text((x3, title_top), moode_meta['title'], font=font_l, fill=txt_col)


        

        if 'volume' in mpd_status:
            vol = int(mpd_status['volume'])
            vol_x = int((vol/100)*(WIDTH - 33))
            draw.rectangle((5, volume_top, WIDTH-34, volume_top+8), (255,255,255,145))
            draw.rectangle((5, volume_top, vol_x, volume_top+8), bar_col)
        if 'elapsed' in  mpd_status:
            el_time = int(float(mpd_status['elapsed']))
            if 'duration' in mpd_status:
                du_time = int(float(mpd_status['duration']))
                dur_x = int((el_time/du_time)*(WIDTH-10))
                draw.rectangle((5, time_top, WIDTH-5, time_top + 12), (255,255,255,145))
                draw.rectangle((5, time_top, dur_x, time_top + 12), bar_col)
        
          
    
        if DRIVER == 'ST7735':
            if FULL == True:
                im4 = img.resize((160,160), Image.LANCZOS)
                im3.paste(im4, (0,0))
            else:
                im4 = img.resize((128,128), Image.LANCZOS)
                im3.paste(im4, (16,0))
            disp.display(im3)
        elif DRIVER == 'ST7789':
            disp.display(img)
 
        time.sleep(1)

    client.disconnect()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        disp.reset()
        disp.set_backlight(False)
        pass
