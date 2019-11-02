#!/bin/bash
#check if sudo
if [ "$EUID" -ne 0 ] ; then
  echo "Sorry, but you are not root. Use sudo to run"
  exit 1
fi

sudo rm /usr/share/applications/Yt.desktop
sudo rm -rf /usr/local/sbin/YtDownloader

echo "App removed."