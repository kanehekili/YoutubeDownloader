# YoutubeDownloader
GTK3 UI for youtube-dl,vimeo and others

Verison 1.0.0

This simple GUI for the youtube-dl runs on linux. 

![Screenshot](./Yt.png)

Prerequisites are:
  * python3
  * python3-gi (debian) or python-gobject (Arch)
  * youtube-dl
  * ffmpeg

### Install on Debian, Linux Mint (19.X) or Ubuntu 18.04 (bionic) 
```
sudo apt install python3-gi ffmpeg youtube-dl
```
### Install on Arch or Manjaro
```
sudo pacman -Syu python-gobject ffmpeg youtube-dl
```

###Features
Downloads either video(with audio) or audio only from youtube, vimeo and other platforms by simply dragging the url from the browser to the gui.

You may set the target directories for video and audio individually. 

The URLs in the list can be saved and restored

### How to install
* Download the YtDownloader*.tar contained in the "build" folder ![here](build/YtDownloader1.0.0.tar)
* Unpack it and run the command "sudo ./install.sh" in the unpacked folder.
* Install just copies a desktop file and some python scripts to /usr/local/sbin/YtDownloader


