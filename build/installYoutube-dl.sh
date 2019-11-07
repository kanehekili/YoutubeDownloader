#!/bin/bash
#check if sudo
if [ "$EUID" -ne 0 ] ; then
  echo "Sorry, but you are not root. Use sudo to run"
  exit 1
fi

wget https://yt-dl.org/downloads/latest/youtube-dl -O /usr/local/bin/youtube-dl
chmod a+rx /usr/local/bin/youtube-dl
