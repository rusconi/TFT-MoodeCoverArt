
import ST7735
from PIL import Image, ImageDraw
#from PIL import ImageFont



disp = ST7735.ST7735(
    port=0,
    cs=0,   #ST7735.BG_SPI_CS_FRONT,  # BG_SPI_CSB_BACK or BG_SPI_CS_FRONT
    dc=17,
    backlight=22,               # 18 for back BG slot, 19 for front BG slot.
    rst=27,
    width=128,
    height=160,
    rotation=90,
    invert=False,
    spi_speed_hz=20000000
)

disp2 = ST7789.ST7789(
    port=0,
    cs=ST7789.BG_SPI_CS_FRONT,  # BG_SPI_CSB_BACK or BG_SPI_CS_FRONT
    dc=9,
    backlight=13,               # 18 for back BG slot, 19 for front BG slot.
    spi_speed_hz=80 * 1000 * 1000
)

WIDTH = disp.width
HEIGHT = disp.height

'''
#disp.command(0x28)
img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(img)
draw.rectangle((0, 0, 160, 128), (0, 0, 0))
disp.display(img)
'''
disp.reset()
disp.set_backlight(False)

disp2.reset()
disp2.set_backlight(False)
