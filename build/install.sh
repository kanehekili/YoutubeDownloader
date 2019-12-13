#!/bin/bash
#check if sudo
if [ "$EUID" -ne 0 ] ; then
  echo "Sorry, but you are not root. Use sudo to run"
  exit 1
fi
#copy desktop to /usr/share applications
sudo cp Yt.desktop /usr/share/applications;
sudo mkdir -p /usr/local/bin/YtDownloader;
sudo cp * /usr/local/bin/YtDownloader/;
rm $HOME/.config/YtDownloader.ini

echo "####################################################"
echo "#   Ensure you have installed:                     #"                     
echo "#       *youtube-dl                                #"
echo "#       *ffmpeg                                    #"
echo "####################################################"
echo "App installed."