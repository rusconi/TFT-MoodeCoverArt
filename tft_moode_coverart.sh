#!/bin/bash
 
while getopts ":sq" opt; do
  case ${opt} in
    s ) sudo pkill -f tft_moode_coverart.py; sudo /usr/bin/python3 /home/pi/TFT-MoodeCoverArt/clear_display.py; sudo /usr/bin/python3 /home/pi/TFT-MoodeCoverArt/tft_moode_coverart.py &
      ;;
    q ) sudo pkill -f tft_moode_coverart.py; sudo python3 /home/pi/TFT-MoodeCoverArt/clear_display.py
      ;;
    \? ) echo "Usage: cmd [-s] [-q]"
      ;;
  esac
done