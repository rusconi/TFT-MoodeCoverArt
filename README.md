# TFT-MoodeCoverArt

Based on the look of the pirate audio plugin for mopidy.

Best with Pimoroni pirate audio boards with 240*240 TFT (ST7789).

Can also be used with a 160*128 ST7735 TFT.

Assumptions.

Your moode installation works and produces audio

If your pirate audio board doesn't output anything, see the pimoroni website

Preparation

Enable SPI pn your RPI

Install these pre-requisites:
```
sudo apt-get update
sudo apt-get install python3-rpi.gpio python3-spidev python3-pip python3-pil python3-numpy
sudo pip3 install mediafile
```
Install the TFT driver

If using a pirate audio board:
```
sudo pip3 install st7789
```
If using an ST7735 TFT
```
sudo pip3 install st7735
```
It's ok to install both if you want.

Install the TFT-MoodeCoverArt script

```
cd /home/pi
git clone https://github.com/rusconi/TFT-MoodeCoverArt.git
'''

If using a generic ST7735 tft edit the python script

```
nano /home/pi/TFT-MoodeCoverArt/tft_moode_coverart.py
```

change the lines
```
DRIVER = 'ST7789'
#DRIVER = 'ST7735'
to
#DRIVER = 'ST7789'
DRIVER = 'ST7735'
```

Test the script:
```
python3 /home/pi/TFT-MoodeCoverArt/tft_moode_coverart.py
```





/usr/local/lib/python3.7/dist-packages/ST7735/__init__.py

ST7735_MADCTL = 0x36
to
ST7735_MADCTL = 0x00