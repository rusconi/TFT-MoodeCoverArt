

import ST7789
from PIL import Image, ImageDraw
from os import path
import yaml

# set default config for pirate audio

MODE=0

OVERLAY=2

confile = 'config.yml'

# Read conf.json for user config
if path.exists(confile):
 
    with open(confile) as config_file:
        data = yaml.load(config_file, Loader=yaml.FullLoader)
        displayConf = data['display']
        OVERLAY = displayConf['overlay']
        MODE = displayConf['mode']


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


disp.begin()
img = Image.new('RGB', (240, 240), color=(0, 0, 0))
draw = ImageDraw.Draw(img)
draw.rectangle((0, 0, 240, 240), (0, 0, 0))
disp.display(img)

disp.set_backlight(False)
