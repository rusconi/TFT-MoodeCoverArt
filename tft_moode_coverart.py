from PIL import Image, ImageDraw, ImageColor, ImageFont, ImageStat
import subprocess
import time
import musicpd
import os
import os.path
from os import path
import RPi.GPIO as GPIO
from mediafile import MediaFile
from io import BytesIO
from numpy import mean 
import ST7789
from PIL import ImageFilter
import yaml

# set default config for pirate audio

__version__ = "0.0.4"

# get the path of the script
script_path = os.path.dirname(os.path.abspath( __file__ ))
# set script path as current directory - 
os.chdir(script_path)

MODE=0
OVERLAY=2
TIMEBAR=1
BLANK=0

confile = 'config.yml'

# Read config.yml for user config
if path.exists(confile):
 
    with open(confile) as config_file:
        data = yaml.load(config_file, Loader=yaml.FullLoader)
        displayConf = data['display']
        OVERLAY = displayConf['overlay']
        MODE = displayConf['mode']
        TIMEBAR = displayConf['timebar']
        BLANK = displayConf['blank']



     
# Standard SPI connections for ST7789
# Create ST7789 LCD display class.
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



# Initialize display.
disp.begin()


WIDTH = 240
HEIGHT = 240
font_s = ImageFont.truetype(script_path + '/fonts/Roboto-Medium.ttf',20)
font_m = ImageFont.truetype(script_path + '/fonts/Roboto-Medium.ttf',24)
font_l = ImageFont.truetype(script_path + '/fonts/Roboto-Medium.ttf',30)


img = Image.new('RGB', (240, 240), color=(0, 0, 0, 25))

play_icons = Image.open(script_path + '/images/controls-play.png').resize((240,240), resample=Image.LANCZOS).convert("RGBA")
play_icons_dark = Image.open(script_path + '/images/controls-play-dark.png').resize((240,240), resample=Image.LANCZOS).convert("RGBA")

pause_icons = Image.open(script_path + '/images/controls-pause.png').resize((240,240), resample=Image.LANCZOS).convert("RGBA")
pause_icons_dark = Image.open(script_path + '/images/controls-pause-dark.png').resize((240,240), resample=Image.LANCZOS).convert("RGBA")

vol_icons = Image.open(script_path + '/images/controls-vol.png').resize((240,240), resample=Image.LANCZOS).convert("RGBA")
vol_icons_dark = Image.open(script_path + '/images/controls-vol-dark.png').resize((240,240), resample=Image.LANCZOS).convert("RGBA")

bt_back = Image.open(script_path + '/images/bta.png').resize((240,240), resample=Image.LANCZOS).convert("RGBA")
ap_back = Image.open(script_path + '/images/airplay.png').resize((240,240), resample=Image.LANCZOS).convert("RGBA")
jp_back = Image.open(script_path + '/images/jack.png').resize((240,240), resample=Image.LANCZOS).convert("RGBA")
sp_back = Image.open(script_path + '/images/spotify.png').resize((240,240), resample=Image.LANCZOS).convert("RGBA")
sq_back = Image.open(script_path + '/images/squeeze.png').resize((240,240), resample=Image.LANCZOS).convert("RGBA")

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
            if (metaDict['file'].find('http://', 0) > -1) or (metaDict['file'].find('https://', 0) > -1):
                # set radio stream to true
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
            rc = '/var/www/' + metaDict['coverurl']
            if path.exists(rc):
                if rc != '/var/www/images/default-cover-v6.svg':
                    cover = Image.open(rc)

    elif metaDict['source'] == 'airplay':
        cover = ap_back
    elif metaDict['source'] == 'bluetooth':
        cover = bt_back
    elif metaDict['source'] == 'input':
        cover = jp_back
    elif metaDict['source'] == 'spotify':
        cover = sp_back
    elif metaDict['source'] == 'squeeze':
        cover = sq_back
    else:
        if 'file' in metaDict:
            if len(metaDict['file']) > 0:

                fp = '/var/lib/mpd/music/' + metaDict['file']   
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

    disp.set_backlight(True)
    
    filename = '/var/local/www/currentsong.txt'

    c = 0
    p = 0
    k=0
    ol=0
    ss = 0
    x1 = 20
    x2 = 20
    x3 = 20
    title_top = 105
    volume_top = 184
    time_top = 222
    act_mpd = isServiceActive('mpd')

    if act_mpd == True:
        while True:
            client = musicpd.MPDClient()   # create client object
            try:     
                client.connect()           # use MPD_HOST/MPD_PORT
            except:
                pass
            else:                  
                moode_meta = getMoodeMetadata(filename)

                mpd_current = client.currentsong()
                mpd_status = client.status()
                cover = get_cover(moode_meta)


                
                mn = 50
                if OVERLAY == 3:
                    img.paste(cover.resize((WIDTH,HEIGHT), Image.LANCZOS).convert('RGB'))
                else:
                    img.paste(cover.resize((WIDTH,HEIGHT), Image.LANCZOS).filter(ImageFilter.GaussianBlur).convert('RGB'))
                
                if 'state' in mpd_status:
                    if (mpd_status['state'] == 'stop') and (BLANK != 0):
                        if ss < BLANK:
                            ss = ss + 1
                        else:
                            disp.set_backlight(False)
                    else:
                        ss = 0
                        disp.set_backlight(True)
                
                
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
                    bar_col = (100,100,100,225)
                if mn < 80:
                    txt_col = (200,200,200)
                
                if (moode_meta['source'] == 'library') or (moode_meta['source'] == 'radio'):

                    if (OVERLAY > 0) and (OVERLAY < 3):
                        if 'state' in mpd_status:
                            if OVERLAY == 2:
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
                            elif OVERLAY == 1:
                                if dark is False:
                                    img.paste(vol_icons, (0,0), vol_icons)
                                else:
                                    img.paste(vol_icons_dark, (0,0), vol_icons_dark)
                            
                        else:
                            img.paste(play_icons, (0,0), play_icons)
    
                        if 'volume' in mpd_status:
                            vol = int(mpd_status['volume'])
                            vol_x = int((vol/100)*(WIDTH - 33))
                            draw.rectangle((5, volume_top, WIDTH-34, volume_top+8), (255,255,255,145))
                            draw.rectangle((5, volume_top, vol_x, volume_top+8), bar_col)
                    
                    if OVERLAY < 3:    
                        if TIMEBAR == 1:
                            if 'elapsed' in  mpd_status:
                                el_time = int(float(mpd_status['elapsed']))
                                if 'duration' in mpd_status:
                                    du_time = int(float(mpd_status['duration']))
                                    dur_x = int((el_time/du_time)*(WIDTH-10))
                                    draw.rectangle((5, time_top, WIDTH-5, time_top + 12), (255,255,255,145))
                                    draw.rectangle((5, time_top, dur_x, time_top + 12), bar_col)
        
                        
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


                else:
                    if 'file' in moode_meta:
                        txt = moode_meta['file'].replace(' ', '\n')
                        w3, h3 = draw.multiline_textsize(txt, font_l, spacing=6)
                        x3 = (WIDTH - w3)//2
                        y3 = (HEIGHT - h3)//2
                        draw.text((x3, y3), txt, font=font_l, fill=txt_col, spacing=6, align="center")
            
            
            disp.display(img)

            if c == 0:
                im7 = img.save(script_path+'/dump.jpg')
                c += 1


            time.sleep(1)
            ol += 1

        client.disconnect()
    else:
        draw.rectangle((0,0,240,240), fill=(0,0,0))
        txt = 'MPD not Active!\nEnsure MPD is running\nThen restart script'
        mlw, mlh = draw.multiline_textsize(txt, font=font_m, spacing=4)
        draw.multiline_text(((WIDTH-mlw)//2, 20), txt, fill=(255,255,255), font=font_m, spacing=4, align="center")
        disp.display(img)
        



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        disp.reset()
        disp.set_backlight(False)
        pass
