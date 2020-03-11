# TFT-MoodeCoverArt

Based on the look of the pirate audio plugin for mopidy.

Best with Pimoroni pirate audio boards with 240*240 TFT (ST7789).

Can also be used with a 160*128 ST7735 TFT.

### Assumptions.

**Your moode installation works and produces audio**

If your pirate audio board doesn't output anything

Choose "Pimoroni pHAT DAC" or "HiFiBerry DAC" in moode audio config

There is a DAC enable pin—BCM 25— that must be driven high to enable the DAC. You can do this by 

```
sudo nano /boot/config.txt
```
and add the following to the file
```
gpio=25=op,dh
```

### Preparation.

**Enable SPI pn your RPI**

see here:

[Configuring SPI](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-spi)

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

### Install the TFT-MoodeCoverArt script

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

**Make the shell control script executable:**

```
chmod u+x /home/pi/TFT-MoodeCoverArt/tft_moode_coverart.sh
Test the script:

```
python3 /home/pi/TFT-MoodeCoverArt/tft_moode_coverart.py

Ctrl-c to quit
```

**If you want to start the display at boot:**

Edit the rc.local file

```
sudo nano /etc/rc.local
```

add the following as the last line before *exit 0*
```
/home/pi/TFT-MoodeCoverArt/tft_moode_coverart.sh -s > /dev/null 2>&1
```

The last few lines of rc.local should look something like this:

```
# moOde startup and job processor daemon
/var/www/command/worker.php > /dev/null 2>&1

# start TFT-Moode-CoverArt
/home/pi/TFT-MoodeCoverArt/tft_moode_coverart.sh -s > /dev/null 2>&1

exit 0
```
**Note:** The tft_moode_coverart.sh bash script allows you to easily start, 
restart or stop the python script, even if it is running in the background.

tft_moode_coverart.sh -s (re)starts the script, and

tft_moode_coverart.sh -q stops the script.

The rationale is so that any already running script is stopped and the screen blanked before any restart

To run the script, either:
```
cd /home/pi/pi/TFT-MoodeCoverArt
./tft_moode_coverart.sh

or

/home/pi/TFT-MoodeCoverArt/tft_moode_coverart.sh
```

### Potential Issues:

Incorrect colours on ST7735.

You need to edit the ST7735 driver

```
sudo nano /usr/local/lib/python3.7/dist-packages/ST7735/__init__.py
```
change the following line
```
ST7735_MADCTL = 0x36
```
to
```
ST7735_MADCTL = 0x00
```
