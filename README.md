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



