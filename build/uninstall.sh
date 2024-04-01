#!/bin/bash
#check if sudo
if [ "$EUID" -ne 0 ] ; then
  echo "Sorry, but you are not root. Use sudo to run"
  exit 1
fi

sudo rm /usr/share/applications/YtGui.desktop
sudo rm /usr/bin/YtGui
sudo rm -rf /opt/ytdownloader
if test -f "$USER_HOME/.config/YtDownloader.ini"; then
	rm $HOME/.config/YtDownloader.ini
fi
echo "App removed."
