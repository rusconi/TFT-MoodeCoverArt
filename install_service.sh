#!/bin/bash

echo -e "Install TFT-MoodeCoverArt Service. \n"
cd /home/pi/TFT-MoodeCoverArt

while true
do
    read -p "Do you wish to install TFT-MoodeCoverArt as a service?" yn
    case $yn in
        [Yy]* ) echo -e "Installing Service \n"
                sudo cp tft-moodecoverart.service /lib/systemd/system
                sudo chmod 644 /lib/systemd/system/tft-moodecoverart.service
                sudo systemctl daemon-reload
                sudo systemctl enable tft-moodecoverart.service
				echo -e "\nTFT-MoodeCoverArt installed as a service.\n"
                echo -e "Please reboot the Raspberry Pi.\n"
                break;;
        [Nn]* ) echo -e "Service not installed \n"; break;;
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

echo "TFT-MoodeCoverArt install complete"