#!/bin/bash
#check if sudo
if [ "$EUID" -ne 0 ] ; then
  echo "Sorry, but you are not root. Use sudo to run"
  exit 1
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
sudo cp $DIR/YtGui.desktop /usr/share/applications;
sudo mkdir -p /opt/ytdownloader;
sudo cp -r $DIR/* /opt/ytdownloader;
sudo chmod +x /opt/ytdownloader/YtGui.py
sudo ln -s /opt/ytdownloader/YtGui.py /usr/bin/YtGui

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