from PIL import Image, ImageDraw, ImageColor, ImageFont, ImageStat
import subprocess
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


draw = ImageDraw.Draw(img, 'RGBA')


def isServiceActive(service):

    waiting = True
    count = 0
    active = False

    while (waiting == True):

        process = subprocess.run(['systemctl','is-active',service], check=False, stdout=subprocess.PIPE, universal_newlines=True)
        output = process.stdout
        stat = output[:6]
        
        if stat == 'active':
            waiting = False
            active = True
            

        if count > 29:
            waiting = False
            

        count += 1
        time.sleep(1)

    return active


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
        
        metaDict['source'] = 'library'
        if 'file' in metaDict:
            if metaDict['file'].find('http://', 0) > -1:
                # set radio stream to9 true
                metaDict['source'] = 'radio'
                # if radio station has arist and title in one line separated by a hyphen, split into correct keys
                if metaDict['title'].find(' - ', 0) > -1:
                    (art,tit) = metaDict['title'].split(' - ', 1)
                    metaDict['artist'] = art
                    metaDict['title'] = tit
            elif metaDict['file'].find('Bluetooth Active', 0) > -1:
                metaDict['source'] = 'bluetooth'
            elif metaDict['file'].find('Airplay Active', 0) > -1:
                metaDict['source'] = 'airplay'
            elif metaDict['file'].find('Spotify Active', 0) > -1:
                metaDict['source'] = 'spotify'
            elif metaDict['file'].find('Squeezelite Active', 0) > -1:
                metaDict['source'] = 'squeeze'
            elif metaDict['file'].find('Input Active', 0) > -1:
                metaDict['source'] = 'input' 
            

    # return metadata
    return metaDict

def get_cover(metaDict):

    cover = None
    cover = Image.open(script_path + '/images/default-cover-v6.jpg')
    covers = ['Cover.jpg', 'cover.jpg', 'Cover.jpeg', 'cover.jpeg', 'Cover.png', 'cover.png', 'Cover.tif', 'cover.tif', 'Cover.tiff', 'cover.tiff',
		'Folder.jpg', 'folder.jpg', 'Folder.jpeg', 'folder.jpeg', 'Folder.png', 'folder.png', 'Folder.tif', 'folder.tif', 'Folder.tiff', 'folder.tiff']
    if metaDict['source'] == 'radio':
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
    title_top = 150
    volume_top = 184
    time_top = 222
    '''
    if FULL == True and DRIVER == 'ST7735':
        title_top = 80
        volume_top = 136
        time_top = 174
    '''
    act_mpd = isServiceActive('mpd')
    
    if act_mpd == True:
        while True:
            client = musicpd.MPDClient()       # create client object
            client.connect()                   # use MPD_HOST/MPD_PORT
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
            
        
            top = 20
            if 'artist' in moode_meta:
                w1, y1 = draw.textsize(moode_meta['artist'], font_m)
                x1 = x1-20
                if x1 < (WIDTH - w1 - 20):
                    x1 = 0
                if w1 <= WIDTH:
                    x1 = (WIDTH - w1)//2
                draw.text((x1, top), moode_meta['artist'], font=font_m, fill=txt_col)
            
            top = 75
            
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
            
            #print(moode_meta['source'])
            time.sleep(1)

        client.disconnect()
    else:
        draw.rectangle((0,0,240,240), fill=(0,0,0))
        txt = 'MPD not Active!\nEnsure MPD is running\nThen restart script'
        mlw, mlh = draw.multiline_textsize(txt, font=font_m, spacing=4)
        draw.multiline_text(((WIDTH-mlw)//2, 20), txt, fill=(255,255,255), font=font_m, spacing=4, align="center")
        disp.display(img)
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
        #else:
        #    img.paste(bt_back, (0,0))




if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        disp.reset()
        disp.set_backlight(False)
        pass
