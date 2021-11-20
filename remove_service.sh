#!/bin/bash

echo -e "Remove TFT-MoodeCoverArt Service\n"


while true
do
    read -p "Do you wish to Remove TFT-MoodeCoverArt as a service?" yn
    case $yn in
        [Yy]* ) echo -e "Removing Service \n"
                sudo systemctl stop tft-moodecoverart.service
                sudo systemctl disable tft-moodecoverart.service
                sudo rm /etc/systemd/system/tft-moodecoverart.service
                sudo systemctl daemon-reload
                sudo systemctl reset-failed
                echo -e "\nTFT-MoodeCoverArt removed as a service.\n"
                echo -e "Please reboot the Raspberry Pi.\n"
                break;;
        [Nn]* ) echo -e "Service not removed \n"; break;;
        * ) echo "Please answer yes or no.";;
    esac
done

while true
do
    read -p "Do you wish to reboot now?" yn
    case $yn in
        [Yy]* ) echo -e "Rebooting \n"
                sudo reboot
                break;;
        [Nn]* ) echo -e "Not rebooting \n"
                break;;
        * ) echo "Please answer yes or no.";;
    esac
done

echo "TFT-MoodeCoverArt service removal complete"

