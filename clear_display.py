
import ST7735
import ST7789
from PIL import Image, ImageDraw

# choose between ST7789 and ST7735 driver
# Uncomment the driver you want, comment out the other
DRIVER = 'ST7789'
#DRIVER = 'ST7735'

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
        #backlight=22,               
        rst=27,
        width=128,
        height=160,
        rotation=90,
        invert=False,
        spi_speed_hz=40000000
    )

disp.begin()
img = Image.new('RGB', (240, 240), color=(0, 0, 0))
draw = ImageDraw.Draw(img)
draw.rectangle((0, 0, 240, 240), (0, 0, 0))
disp.display(img)

disp.set_backlight(False)
