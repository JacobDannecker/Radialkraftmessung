#!/bin/bash
username=$1
# Tinkerforge APR-Repository hinzufuegen
wget https://download.tinkerforge.com/apt/$(. /etc/os-release; echo $ID)/tinkerforge.gpg -q -O - | sudo tee /etc/apt/trusted.gpg.d/tinkerforge.gpg > /dev/null
echo "deb https://download.tinkerforge.com/apt/$(. /etc/os-release; echo $ID $VERSION_CODENAME) main" | sudo tee /etc/apt/sources.list.d/tinkerforge.list
sudo apt update
# Benoetigte Software installieren
sudo apt install -y python3-matplotib
sudo apt install -y python3-pandas
sudo apt install -y python3-pyqt6
sudo apt install -y python3-subprocess
sudo apt install -y python3-os
sudo apt install -y python3-pathlib
sudo apt install -y python3-datetime
sudo apt install -y python3-time
sudo apt install -y python3-timeit
sudo apt install -y python3-csv
sudo apt install -y python3-sys
sudo apt install -y python3-tinkerforge
sudo apt install -y brickd
sudo apt install -y xorg
sudo apt install -y openbox
sudo apt install -y nemo
sudo apt install -y python3-pyxdg
# Openbox konfigurieren
mkdir /home/$username/.config
mkdir /home/$username/.config/openbox
mv /home/$username/Software_RasPi/.bash_profile /home/$username/
touch .xinitrc
echo "exec openbox-session" >> .xinitrc
mv .xinitrc /home/$username/
touch autostart
echo "python3 /home/$username/Software_RasPi/Main_App.py &" >> autostart
mv /home/$username/Software_RasPi/autostart /home/$username/.config/openbox/
