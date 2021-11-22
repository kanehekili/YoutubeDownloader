#!/bin/bash
#check if sudo
if [ "$EUID" -ne 0 ] ; then
  echo "Sorry, but you are not root. Use sudo to run"
  exit 1
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cp $DIR/YtGui.desktop /usr/share/applications;
mkdir -p /opt/ytdownloader;
cp -r $DIR/* /opt/ytdownloader;
chmod +x /opt/ytdownloader/YtGui.py
ln -s /opt/ytdownloader/YtGui.py /usr/bin/YtGui

if test -f "/usr/local/bin/yt-dlp"; then
	echo "yt-dlp installed"
else
    if ! command -v curl &> /dev/null; then
      wget https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -O /usr/local/bin/yt-dlp
    else  
      curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
    fi  
   chmod a+rx /usr/local/bin/yt-dlp
fi

USER_HOME=$(eval echo ~${SUDO_USER})
if test -f "$USER_HOME/.config/YtDownloader.ini"; then
    rm $USER_HOME/.config/YtDownloader.ini;
fi

echo "####################################################"
echo "#   Ensure you have installed:                     #"                     
echo "#       *ffmpeg                                    #"
echo "####################################################"
echo "App installed."