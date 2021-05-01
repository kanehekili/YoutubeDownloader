#!/bin/bash
#check if sudo
if [ "$EUID" -ne 0 ] ; then
  echo "Sorry, but you are not root. Use sudo to run"
  exit 1
fi

#copy desktop to /usr/share applications
sudo cp YtGui.desktop /usr/share/applications;
sudo mkdir -p /usr/local/bin/YtDownloader;
sudo cp * /usr/local/bin/YtDownloader/;
sudo chmod +x /usr/local/bin/YtDownloader/YtGui.py;
USER_HOME=$(eval echo ~${SUDO_USER})
if test -f "$USER_HOME/.config/YtDownloader.ini"; then
    rm $USER_HOME/.config/YtDownloader.ini;
fi

echo "####################################################"
echo "#   Ensure you have installed:                     #"                     
echo "#       *youtube-dl                                #"
echo "#       *ffmpeg                                    #"
echo "####################################################"
echo "App installed."