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

if test -f "/usr/bin/yt-dlp"; then
	echo "yt-dlp installed in /usr/bin"
elif test -f "/opt/ytdownloader/yt-dlp"; then
	echo "yt-dlp installed in /opt"
else 
	echo "downloading yt-dlp ..."

#if test -f "/usr/bin/yt-dlp" || test -f "/opt/ytdownloader/yt-dlp"; then
#	echo "yt-dlp installed"
#else
#	echo "downloading yt-dlp ..."
#    if ! command -v curl &> /dev/null; then
#      wget https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -O /opt/ytdownloader/yt-dlp
#    else  
#      curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /opt/ytdownloader/yt-dlp
#    fi  
#   chmod a+rx /opt/ytdownloader/yt-dlp
fi

USER_HOME=$(eval echo ~${SUDO_USER})
if test -f "$USER_HOME/.config/YtDownloader.ini"; then
    rm $USER_HOME/.config/YtDownloader.ini;
fi

if ! command -v ffmpeg &> /dev/null; then
  echo "ffmpeg not installed, trying to install it through your package manager."

  ## checking package managers if they are installed
  YUM_CMD=$(which yum)
  PACMAN_CMD=$(which pacman)
  APT_GET_CMD=$(which apt-get)
  ZYPPER_CMD=$(which zypper)
  ## OTHER_CMD=$(which OTHER)


  #echo $YUM_CMD
  #echo $PACMAN_CMD
  #echo $APT_GET_CMD
  #echo $ZYPPER_CMD


  if [[ ! -z $YUM_CMD ]]; then
      sudo dnf -y install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
      sudo dnf -y install https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
      sudo dnf -y install ffmpeg
  elif [[ ! -z $PACMAN_CMD ]]; then
      pacman -Syu ffmpeg
  elif [[ ! -z $APT_GET_CMD ]]; then
      apt update
      apt install ffmpeg
  elif [[ ! -z $ZYPPER_CMD ]]; then
      zypper addrepo https://download.opensuse.org/repositories/openSUSE:Factory/standard/openSUSE:Factory.repo
      zypper refresh
      zypper install ffmpegthumbs
  ## elif [[ ! -z $OTHER_CMD ]]; then
  ##    OTHER_COMMAND
  else
     echo "error: Can't install package ffmpeg, check https://ffmpeg.org/ on how to download it for your system."
     echo "####################################################"
     echo "#   Ensure you have installed:                     #"                     
     echo "#       *ffmpeg                                    #"
     echo "####################################################"
     exit 1;
  fi
fi

printf '\n'
printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' -
printf '\n'

echo "App successfully installed."
