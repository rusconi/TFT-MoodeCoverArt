# TFT-MoodeCoverArt 
*version = "0.0.8" : changes*

* changed the service file installation path, for consistency and to fix the uninstall script which was non-functional
* new power-off action (to activate press play/pause, and press it again and hold for 5 seconds); requires config `shutdown_or_toggle_play.sh` for the play/pause GPIO button in moode, see below
* faster start and with less screen blinking
* some other optimizations to reduce CPU usage and response/update time
* new overlay mode for greater flexibility (and some others renumbered for clarity)
* text and timebar overlays are now configurable independently (and for any overlay mode) for greater flexibility
* new config option, embcoverprio, to match moode's cover search priority (if that one is changed, change this option here to have consistent covers)
* invert play/pause icons for clarity
* changed the text overflow management: text now "travels" fully, appearing from the right until disappearing to the left
* new choice for displaying text overlays only when state is playing (the default behaviour is to show it always, as before); when it is used, the "crisp" (not blurred) cover image will be shown on pause/stop state
* small fixes in volume / time bar display for very low values
* small improvement in text shadow option: for this font and screen sizes, a default value of 2 looks better

*version = "0.0.7" : changes*

* update for moode 7.6.0 - BUG FIX: URL encoding for radio station logos

*version = "0.0.6" : changes*

* added option for text shadow

*version = "0.0.5" : changes*

* radio icons location changed

*version = "0.0.4" : changes*

* added option to display cover art only without overlays (see config file for instructions)

*version = "0.0.3" : changes*

* added option to turn off backlight when mpd state = stop (see config file for instructions)

-------------------------------------------------------


Based on the look of the pirate audio plugin for mopidy.

Works with Pimoroni pirate audio boards with 240*240 TFT (ST7789), as well as standalone ST7789 boards.

![Sample Image](/pics/display.jpg)

### Features.

The script will display cover art (where available) for the moode library or radio stations.

* For the moode library, embedded art will be displayed first, then folder or cover images if there is no embedded art.
* For radio stations, the moode images are used.
* If no artwork is found a default image is displayed.

Metadata displayed:
* Artist
* Album/Radio Station
* Title

Overlays with a Time bar, Volume bar and Play/Pause, Next and Volume icons to match the Pirate Audio buttons are optional.

There is also an option in config.yml to not display metadata.

The script has a built in test to see if the mpd service is running. This should allow enough delay when 
used as a service. If a running mpd service is not found after around 30 seconds the script displays the following and stops.

```
   MPD not Active!
Ensure MPD is running
 Then restart script
```

**Limitations**

Metadata will only be displayed for Radio Stations and the Library.

For the `Airplay`, `Spotify`, `Bluetooth`, `Squeezelite` and `Dac Input` renderers, different backgrounds will display.

The overlay colours adjust for light and dark artwork, but can be hard to read with some artwork.

The script does not search online for artwork.

### Assumptions.

**You can SSH into your RPI, enter commands at the shell prompt, and use the nano editor.**

**Your moode installation works and produces audio**

If your pirate audio board doesn't output anything

Choose "Pimoroni pHAT DAC" or "HiFiBerry DAC" in moode audio config

See the Installation section [**here**](https://github.com/pimoroni/pirate-audio) about gpio pin 25. 

### Preparation.

**Enable SPI pn your RPI**

see [**Configuring SPI**](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-spi)

Install these pre-requisites:
```
sudo apt-get update
sudo apt-get install python3-rpi.gpio python3-spidev python3-pip python3-pil python3-numpy
sudo pip3 install mediafile
sudo pip3 install pyyaml
```
Install the TFT driver.

I have forked the Pimoroni driver and modified it to work with other ST7789 boards. Install it with the following command:

```
sudo pip3 install RPI-ST7789
```

***Ensure 'Metadata file' is turned on in Moode System Configuration***

Recommended: set "GPIO config" (in Moode System Configuration) with these values:
* Button 1 (on), PIN 5, CMD: `/home/pi/TFT-MoodeCoverArt/shutdown_or_toggle_play.sh`
** If the power-off action is not wanted, use CMD: `mpc,toggle` (play/pause)
* Button 2 (on), PIN 6, CMD: `/var/www/vol.sh,-dn,1`
* Button 3 (on), PIN 16, CMD: `mpc,next`
* Button 4 (on), PIN 24, CMD: `/var/www/vol.sh,-up,1`

### Install the TFT-MoodeCoverArt script

```
cd /home/pi
git clone https://github.com/rusconi/TFT-MoodeCoverArt.git
```

### Config File

The default config should work with Pirate Audio boards.

The config.yml file can be edited to:

* suit different ST7789 boards
* set overlay display options
* display the text with a shadow

The comments in 'config.yml' should be self explanatory.


**Make the shell scripts executable, if needed:**

```
chmod 777 *.sh
```

Test the script:

```
python3 /home/pi/TFT-MoodeCoverArt/tft_moode_coverart.py


Ctrl-c to quit
```

**If the script works, you may want to start the display at boot:**

### Install as a service.

```
cd /home/pi/TFT-MoodeCoverArt
./install_service.sh
```

Follow the prompts.

If you wish to remove the script as a service:

```
cd /home/pi/TFT-MoodeCoverArt
./remove_service.sh
```

