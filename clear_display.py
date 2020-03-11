
import ST7735
import ST7789
from PIL import Image, ImageDraw

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

img = Image.new('RGB', (240, 240), color=(0, 0, 0))
draw = ImageDraw.Draw(img)
draw.rectangle((0, 0, 160, 128), (0, 0, 0))
disp.display(img)

disp.set_backlight(False)
disp2 = ST7789.ST7789(
    port=0,
    cs=ST7789.BG_SPI_CS_FRONT,  # BG_SPI_CSB_BACK or BG_SPI_CS_FRONT
    dc=9,
    backlight=13,               # 18 for back BG slot, 19 for front BG slot.
    spi_speed_hz=80 * 1000 * 1000
)

draw2 = ImageDraw.Draw(img)

draw.rectangle((0, 0, 240, 240), (0, 0, 0))
disp.display(img)
disp.set_backlight(False)

draw2.rectangle((0, 0, 240, 240), (0, 0, 0))
disp2.display(img)
disp2.set_backlight(False)
