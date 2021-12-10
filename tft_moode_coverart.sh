#!/bin/bash
 
while getopts ":sq" opt; do
  case ${opt} in
    s ) sudo pkill -f tft_moode_coverart.py; exec sudo /usr/bin/python3 /home/pi/TFT-MoodeCoverArt/tft_moode_coverart.py
      ;;
    q ) sudo pkill -f tft_moode_coverart.py; sleep 1; sudo python3 /home/pi/TFT-MoodeCoverArt/clear_display.py
      ;;
    \? ) echo "Usage: $0 [-s] [-q]"
      ;;
  esac
done

