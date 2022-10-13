'''
Created on Oct 25, 2019

@author: matze
'''
from configparser import ConfigParser
import locale
from os.path import expanduser
from subprocess import Popen
import subprocess
import os,urllib
from urllib.parse import urlparse
import json 
import re
import time
from datetime import timedelta

#import threading
MODE_VIDEO="V";
MODE_AUDIO="A";
lang = locale.getdefaultlocale()

YOUTUBE_DL="/usr/bin/yt-dlp"
if not os.path.exists(YOUTUBE_DL):
    YOUTUBE_DL=None

TEXT_MAP = {}
if "en" in lang[0]:
    TEXT_MAP["TITLE"]="Video Downloader"
    TEXT_MAP["LABEL_DROP_AREA"]="Drop URLs onto list below"
    TEXT_MAP["BUTTON_OK"]="Download"
    TEXT_MAP["BTN_INTERRUPT"]=" Interrupt "
    TEXT_MAP["BUTTON_CANX"]="   Exit   "
    TEXT_MAP["MENU_DEL"]="Remove"
    TEXT_MAP["MENU_DEL_ALL"]="Remove all"
    TEXT_MAP["MENU_RELOAD"]="Force Reload"
    TEXT_MAP["MENU_OPEN"]="Open Folder"
    TEXT_MAP["FOLDER_MUSIC"]="Music"
    TEXT_MAP["FOLDER_VIDEO"]="Videos"
    TEXT_MAP["DIALOG_ERROR_TITLE"]="Error Message"
    TEXT_MAP["DIALOG_ERROR_HEADER"]="An error occurred )-:"
    TEXT_MAP["DIALOG_INFO_TITLE"]="Information"
    TEXT_MAP["NOT_AN_URL_ERROR"]="Invalid URL"
    TEXT_MAP["FILE_SAVE"]="Name of TODO"
    TEXT_MAP["COL1"]="URL"
    TEXT_MAP["COL2"]="Title"
    TEXT_MAP["COL3"]="Status"
    TEXT_MAP["COL4"]="A/V"
    TEXT_MAP["INSTALL_YT"]="Please install yt-dlp and ffmpeg"
    TEXT_MAP["TIP_TOOL_ADD"]="Add URL manually"
    TEXT_MAP["TIP_TOOL_OPEN"]="Load saved URL List"
    TEXT_MAP["TIP_TOOL_SAVE"]="Save the URL List"
    TEXT_MAP["TIP_TOOL_UPDATE"]="Update to the lastest yt-dlp"
    TEXT_MAP["COMBO_VIDEO"]="Video+Audio"
    TEXT_MAP["COMBO_AUDIO"]="Audio only"
    TEXT_MAP["TIP_TOOL_COMBO"]="Dowload settings"
    TEXT_MAP["TIP_TOOL_SETTINGS"]="File settings"
    TEXT_MAP["TIP_LIST"]="Drop URL from browser here"
    TEXT_MAP["TIP_BTN_OK"]="Start Download"
    TEXT_MAP["TIP_BTN_CANX"]="Exit"
    TEXT_MAP["TIP_BTN_DEL"]="Remove entry"
    TEXT_MAP["LIST_LOADED"]="List loaded"
    TEXT_MAP["LIST_SAVED"]="List saved"
    TEXT_MAP["SETTINGS_DLG"]="Settings dialog"
    TEXT_MAP["URL_DLG"]="Add video URL"
    TEXT_MAP["ENTER_URL"]="Enter video URL"
    #TEXT_MAP["SETTINGS_LABEL"]="Settings"
    TEXT_MAP["SET_AUDIO_LBL"]="Store audio at:"
    TEXT_MAP["SET_VIDEO_LBL"]="Store videos at:"
    TEXT_MAP["FOLDER_VIDEO_SAVE"]="Video Folder"
    TEXT_MAP["FOLDER_AUDIO_SAVE"]="Audio Folder"
    TEXT_MAP["DL_SETTINGS_TITLE"]="Quality settings"
    TEXT_MAP["SEL_MP4"]="Good quality with mp4"
    TEXT_MAP["SEL_MKV"]="Highest quality with mkv"
    TEXT_MAP["SEL_ANY"]="Highest quality auto container"
    TEXT_MAP["NO_DL"]="Could not find yt-dlp. It should be in \n /usr/bin"
    TEXT_MAP["STATUS_INTERRUPT"]="Process interrupted"
    TEXT_MAP["ALREADY_THERE"]="File already downloaded"
    
elif "de" in lang[0]:
    TEXT_MAP["TITLE"]="Video Downloader"
    TEXT_MAP["LABEL_DROP_AREA"]="URLs auf die Liste ziehen"
    TEXT_MAP["BUTTON_OK"]="Download"
    TEXT_MAP["BTN_INTERRUPT"]="Stoppen "
    TEXT_MAP["BUTTON_CANX"]="   Schließen   "
    TEXT_MAP["MENU_DEL"]="Löschen"
    TEXT_MAP["MENU_DEL_ALL"]="Alle löschen"
    TEXT_MAP["MENU_RELOAD"]="Erneut Laden"
    TEXT_MAP["MENU_OPEN"]="Ordner öffnen"
    TEXT_MAP["FOLDER_MUSIC"]="Musik"
    TEXT_MAP["FOLDER_VIDEO"]="Videos"
    TEXT_MAP["DIALOG_ERROR_TITLE"]="Fehler Hinweis"
    TEXT_MAP["DIALOG_ERROR_HEADER"]="Da ist ein Fehler passiert )-:"
    TEXT_MAP["DIALOG_INFO_TITLE"]="Information"
    TEXT_MAP["NOT_AN_URL_ERROR"]="Ungültige URL"
    TEXT_MAP["FILE_SAVE"]="Wie soll die Datei heißen?"
    TEXT_MAP["COL1"]="Adresse"
    TEXT_MAP["COL2"]="Titel"
    TEXT_MAP["COL3"]="Status"
    TEXT_MAP["COL4"]="A/V"
    TEXT_MAP["INSTALL_YT"]="Bitte yt-dlp und ffmpeg installieren"
    TEXT_MAP["TIP_TOOL_ADD"]="Youtube URL eingeben"
    TEXT_MAP["TIP_TOOL_OPEN"]="URL Liste laden"
    TEXT_MAP["TIP_TOOL_SAVE"]="URL Liste speichern"
    TEXT_MAP["TIP_TOOL_UPDATE"]="Update auf die neuste yt-dlp"
    TEXT_MAP["COMBO_VIDEO"]="Video+Audio"
    TEXT_MAP["COMBO_AUDIO"]="nur Audio"
    TEXT_MAP["TIP_TOOL_COMBO"]="Einstellung für Download"
    TEXT_MAP["TIP_TOOL_SETTINGS"]="Einstellungen für Dateien"
    TEXT_MAP["TIP_LIST"]="URL vom Browser hierher ziehen"
    TEXT_MAP["TIP_BTN_OK"]="Download starten"
    TEXT_MAP["TIP_BTN_CANX"]="Beenden"
    TEXT_MAP["TIP_BTN_DEL"]="Eintrag löschen"
    TEXT_MAP["LIST_LOADED"]="Liste geladen"
    TEXT_MAP["LIST_SAVED"]="Liste gespeichert"
    TEXT_MAP["SETTINGS_DLG"]="Einstellungen"
    TEXT_MAP["SET_AUDIO_LBL"]="Ordner für Musik:"
    TEXT_MAP["SET_VIDEO_LBL"]="Ordner für Videos"    
    TEXT_MAP["URL_DLG"]="Video Adresse"
    TEXT_MAP["ENTER_URL"]="Manuelle Eingabe der Video URL"
    #TEXT_MAP["SETTINGS_LABEL"]="Einstellungen"
    TEXT_MAP["FOLDER_VIDEO_SAVE"]="Video Ordner"
    TEXT_MAP["FOLDER_AUDIO_SAVE"]="Audio Ordner"
    TEXT_MAP["DL_SETTINGS_TITLE"]="Qualitätseinstellungen"
    TEXT_MAP["SEL_MP4"]="Gute Qualität im mp4 Format"
    TEXT_MAP["SEL_MKV"]="Sehr gute Qualität im mkv Format"
    TEXT_MAP["SEL_ANY"]="Sehr gute Qualität im beliebigen Format"
    TEXT_MAP["NO_DL"]="yt-dlp nicht gefunden. Sollte in\n /usr/bin sein"
    TEXT_MAP["STATUS_INTERRUPT"]="Download abgebrochen"
    TEXT_MAP["ALREADY_THERE"]="Datei schon geladen"
    
    
def _t(s):
    if not s in TEXT_MAP:
        print('TEXT_MAP["%s"]="missing"'%(s))
        return s
    return TEXT_MAP[s]

class ConfigAccessor():
    __SECTION="DATA"
    

    def __init__(self,fileName):
        self._findConfigPath(fileName)
        self.parser = ConfigParser()
        self.parser.add_section(self.__SECTION)

    def _findConfigPath(self,fileName):
        home = expanduser("~")
        cfg = os.path.join(home,".config")
        if os.path.exists(cfg):
            self._path= os.path.join(cfg,fileName)
        else:
            self._path = os.path.join(home,fileName)
        

    def read(self):
        self.parser.read(self._path)

    def add(self,key,value):
        self.parser.set(self.__SECTION,key,value)

    def get(self,key):
        if self.parser.has_option(self.__SECTION, key):
            return self.parser.get(self.__SECTION,key)
        return None

    def getInt(self,key):
        if self.parser.has_option(self.__SECTION, key):
            return self.parser.getint(self.__SECTION,key)
        return None

    def store(self):
        try:
            with open(self._path, 'w') as aFile:
                self.parser.write(aFile)
        except IOError:
            return False
        return True

class Model():
    FORMATS=["mp4","mkv","any"]
    def __init__(self):
        self.text = TEXT_MAP
        self.config = ConfigAccessor("YtDownloader.ini")
        self._assureConfig()
    
    def isManualYT(self):
        #return os.path.isfile("/usr/local/bin/youtube-dl")
        #currently always
        return True
        
    
    def _assureConfig(self):

        self.config.read()
        x = self.config.getInt("SCREENX")
        if not x:
            home = expanduser("~")
            self.config.add("SCREENX","760")
            self.config.add("SCREENY","450")
            pathM = os.path.join(home,_t("FOLDER_MUSIC"))
            pathV = os.path.join(home,_t("FOLDER_VIDEO"))
            if os.path.exists(pathM):
                self.config.add("DEST_MUSIC",pathM)
            else:
                self._setEmergencyFolder(home,"DEST_MUSIC")
            if os.path.exists(pathV):
                self.config.add("DEST_VIDEO",pathV)
            else:
                self._setEmergencyFolder(home,"DEST_VIDEO")
            self.config.add("DOWNLOAD_TYPE",MODE_VIDEO)#video or audio
            self.config.add("URLList",json.dumps([]))
            self.config.add("FORMAT",self.FORMATS[0])
    
    def getScreenX(self):
        return self.config.getInt("SCREENX")
    
    def getScreenY(self):
        return self.config.getInt("SCREENY")

    def setScreenX(self,anInt):
        self.config.add("SCREENX",str(anInt))
        
    def setScreenY(self,anInt):    
        self.config.add("SCREENY",str(anInt))

    def getMusicPath(self):
        return self.config.get("DEST_MUSIC")
    
    def setMusicPath(self,path):
        self.config.add("DEST_MUSIC",path)

    def getVideoPath(self):
        return self.config.get("DEST_VIDEO")

    def setVideoPath(self,path):
        self.config.add("DEST_VIDEO",path)   
         
    def getDownloadTypeIndex(self):
        mode = self.config.get("DOWNLOAD_TYPE")
        if mode is MODE_VIDEO:
            return 0;
        return 1;

    def getDownloadType(self):
        return self.config.get("DOWNLOAD_TYPE")
    
    def setDownloadTypeIndex(self,anInt):
        #0==Video, 1== Audio
        if anInt == 0:
            self.config.add("DOWNLOAD_TYPE", MODE_VIDEO)
        else:
            self.config.add("DOWNLOAD_TYPE", MODE_AUDIO)
    
    def getURLList(self):
        txt = self.config.get("URLList")
        return json.loads(txt)
    
    def setURLList(self,anArray):
        txt= json.dumps(anArray)
        self.config.add("URLList",txt)
        self.config.store()
    
    def setFormat(self,aString):
        self.config.add("FORMAT",aString)

    def getFormat(self):
        return self.config.get("FORMAT")        
    
    def hasValidLibrary(self):
        return YOUTUBE_DL is not None
    
    def _setEmergencyFolder(self,home,key):
        pathD = os.path.join(home,"Downloads")
        if not os.path.exists(pathD):
            os.mkdir(pathD)
        self.config.add(key,pathD)
                    
        
def convertURL(rawData):
    if len(rawData)< 1:
        return None
    
    text = urllib.parse.unquote(rawData)
    aParseResult = urlparse(text)

    if "http" in aParseResult.scheme:
        return aParseResult
    return None

#throws exception..
import sys
def executeAsync(cmd,commander,targetDir):
    print(cmd)
    stdout_line=None
    popen = subprocess.Popen(cmd, cwd=targetDir,stdout=subprocess.PIPE,stderr=subprocess.STDOUT, universal_newlines=True)
    commander.setProcess(popen)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    
    popen.stdout.flush()    
    popen.stdout.close()
    sys.stdout.flush()
    return_code = popen.poll()
    while return_code is None:
        return_code = popen.poll()    
    
    if return_code:
        if return_code == -9:
            raise StopAsyncIteration(_t("BTN_INTERRUPT"))
        form=cropError(stdout_line)
        raise Exception(form)

def cropError(errorText):
    if errorText is None:
        return 
    #text= error.replace('"','*')
    text = errorText.split('. ') 
    text = text[0].split(";")
    return text[0]

def errorToText(error):
    if len(error.args)>1:
        errTxt = error.args[1]
    else:
        errTxt= error.args[0]
    return errTxt
    
    
#Helper class for returning either result objects or errors
class ProcResult():
    def __init__(self,res=None,err=None):
        self.result=res
        self.error = err
        
    def hasError(self):
        return self.error is not None


'''
The downloader.
expects an object that can receive the progress data:
onProgress(percent(float), size with units (str), speed with units (str) 

best video & audio for mp4
yt-dlp -f bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio --merge-output-format mp4 https://www.youtube.com/watch?v=Xj3gU3jACe8

bestaudio:
yt-dlp -f bestaudio --extract-audio --audio-quality 0 --audio-format mp3

very best only (trick=mkv)
yt-dlp -f bestvideo+bestaudio --merge-output-format mkv https://www.youtube.com/watch?v=Xj3gU3jACe8
or:
yt-dlp -f bestvideo+bestaudio https://www.youtube.com/watch?v=Xj3gU3jACe8
>>leads to a webm file. needs complete transcoding for mp4....(VP9+Opus)
'''
class Downloader():
    ISPRESENT = re.compile('.+has already been downloaded')
    REGEXP = re.compile("([0-9.]+)% of ([ ~]*[0-9.]+.iB) at *([A-z]+|[0-9.]+.iB/s)")
    DONE = re.compile('([0-9.]+)% [A-z ]+ ([0-9.]+)(.iB) in ([0-9:]+)' )
    TITLE = re.compile("\[download\] Destination: ([^.]+)+")
    MP4 = ["python3",YOUTUBE_DL,"-f","bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]","-o",'%(title)s.%(ext)s',"--merge-output-format","mp4"]
    MKV = ["python3",YOUTUBE_DL,"-f","bestvideo+bestaudio/best","-o",'%(title)s.%(ext)s',"--merge-output-format","mkv"]
    ANY = ["python3",YOUTUBE_DL,"-f","bestvideo+bestaudio/best","-o",'%(title)s.%(ext)s']
    AUDIO = ["python3",YOUTUBE_DL,"-f","bestaudio/best","-o",'%(title)s.%(ext)s',"--extract-audio","--audio-quality","0","--audio-format","mp3"]
    SEARCH=['"ytsearch %s"']
    
    def __init__(self,receiver):
        self.client = receiver
        self.proc = None
        self.res = ProcResult(res="Done")
        self.downloadtime=timedelta(minutes=0)
        self.downloadSize=0.0
        self.filename=None
        

    def download(self,url,videomode,quality,targetDir):
        #TODO --transcode-video to mp4?
        if YOUTUBE_DL is None:
            return ProcResult(None,_t("NO_DL"))

        if videomode==MODE_AUDIO:
            cmd = self.AUDIO
        else:
            if quality == Model.FORMATS[0]:
                cmd=self.MP4
            elif quality == Model.FORMATS[1]:
                cmd=self.MKV
            else:
                cmd=self.ANY
        command = cmd+[url]
        start = time.monotonic()-1000
        try:
            for line in executeAsync(command,self,targetDir):
                now= time.monotonic()
                elapsed = int(now-start)
                showProgress=elapsed>=1
                err = self.parseAndDispatch(line,showProgress)
                if showProgress:
                    start=now
                if err is not None:
                    self.res.error = err
        except StopAsyncIteration as error:
            self.client.onProgress(None,_t("STATUS_INTERRUPT"))
            
        except Exception as error:
            self.res.error=errorToText(error)
        self.proc=None
        return self.res   
    
    def parseAndDispatch(self,line,showProgress):
        try:        
            m = self.REGEXP.search(line) 
            progress = float(m.group(1))
            #size = m.group(2)
            speed = m.group(3)
            if showProgress:
                self.client.onProgress(progress,speed)

        except Exception as error:
            if len(line)>5:
                if self.ISPRESENT.match(line):
                    self.client.onProgressDone(_t("ALREADY_THERE"),self.filename)
                else:
                    m = self.DONE.search(line)
                    if m is not None:
                        proz=m.group(1)
                        size1=m.group(2)
                        unit= m.group(3)
                        dur= m.group(4)
                        self.downloadSize+=float(size1)
                        dm=dur.split(':')
                        td=timedelta(minutes=int(int(dm[0])),seconds=int(dm[1]))
                        self.downloadtime+=td
                        self.client.onProgressDone(proz+'% of '+format(self.downloadSize,'.2f')+unit+" in "+str(self.downloadtime),self.filename)
                    else:
                        fn = self.TITLE.search(line)
                        if fn is not None:
                            self.filename = fn.group(1)
                print ("<"+line.rstrip())  
                if "ERROR" in line:
                    print("error:%s"%(line));#TODO
                    return cropError(line)
        return None 
    
                
    def stop(self):
        if self.proc is None:
            print("Can't kill proc!")
        else:
            print("downloader - stop process")
            self.proc.kill()

    def setProcess(self,popen):
        self.proc=popen

def getListInfo(url):
    #read url and display list items
    #Not usable while downloading
    if YOUTUBE_DL is None:
        return ProcResult(None,_t("NO_DL"))
    
    cmd=["python3",YOUTUBE_DL,"-i","-j","--flat-playlist",url]
    try:
        result = Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
        form=None
        resArray=None
        if len(result[1])>0:
            #This is mostly an api problem
            form=cropError(result[1].decode("utf-8"))
            #return ProcResult(None,form)
        if len(result[0])>0:
            entries= result[0].decode("utf-8").splitlines()
            resArray=[]
            for line in entries:
                resArray.append(json.loads(line)) #is a map
        return ProcResult(resArray,form)
    except Exception as error:
        form=errorToText(error)
        return ProcResult(None,form)

    
def openFile(path):
    subprocess.call(('xdg-open',path))
#TODO make it async in thread

def play(root,name):
    target = os.path.join(root,name)
    cmd = ['xdg-open',target]
    process = Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    #poll?

def removeFile(root,name):
    target = os.path.join(root,name)
    print("Removing:",target)
    os.remove(target)

def openFolder(root):
    cmd = ['xdg-open',root]
    process = subprocess.call(cmd)

def updateYt():
    #cmd=['pkexec',YOUTUBE_DL,'--update']
    cmd=['pkexec',YOUTUBE_DL,"-U"] 
    result = Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
    form=None
    resArray=None
    if len(result[1])>0:
            #This is mostly an api problem
            form=cropError(result[1].decode("utf-8"))
    if len(result[0])>0:
        entries= result[0].decode("utf-8").splitlines()
        resArray=[]
        for line in entries:
            resArray.append(line) #simple text 
    return ProcResult(resArray,form)

def convert():
    TITLE = re.compile("\[download\][ Destination:]+ ([A-z 0-9-\w']+)+")
    TITLE = re.compile("\[download\] Destination: ([A-z 0-9-\w']+[^.]+)+")
    TITLE = re.compile("\[download\] Destination: ([^.]+)+")
   
    txt=[0 for x in range(24)]
    txt[0]="[download] De 23$%&/&=)?hfggfdgsdf sdfsdwe3454767565645.mp4"
    txt[1]="[download] Destination: Pip _ A Short Animated Film-07d2dXHYb94.f137.mp4"
    txt[2]= "[download] Pip _ A Short Animated Film-07d2dXHYb94.mp4 has already been downloaded and merged"
    txt[3]= "[download] Destination: Poko 110 - Bowling For Minus-QwMfiVl4Wm0.f244.webm"
    txt[4]="[download] Destination: CGI 3D Animated Short - 'Take Me Home' - by Nair Archawattana _ TheCGBros.f137.mp4"
    
    txt[5]="[ARDBetaMediathek] magnus-trolljaeger/folge-1-ein-fall-fuer-idioten-s01-e01/ndr-fernsehen: Downloading JSON metadata"
    txt[6]="[ARDBetaMediathek] 86159550: Downloading m3u8 information"
    txt[7]="[hlsnative] Downloading m3u8 manifest"
    txt[8]="[hlsnative] Total fragments: 192"
    txt[9]="[download] Destination: Folge 1 - Ein Fall für Idioten (S01_E01).mp4"
    txt[10]="[download]  49.5% of ~310.68MiB at  207.71B/s ETA 01:10"
    txt[11]="[download]  49.5% of ~310.68MiB at  267.05B/s ETA 01:10"
    txt[12]="[download]  49.5% of ~310.68MiB at  385.74B/s ETA 01:10"
    txt[13]="[download]  49.5% of ~310.68MiB at  623.11B/s ETA 01:10"
    txt[14]="[download] Got server HTTP error: HTTP Error 404: Not Found. Retrying fragment 192 (attempt 2 of 10)..."
    txt[15]="[download] Got server HTTP error: HTTP Error 404: Not Found. Retrying fragment 192 (attempt 3 of 10)..."
    txt[16]="[download] Got server HTTP error: HTTP Error 404: Not Found. Retrying fragment 192 (attempt 4 of 10)..."
    txt[17]="[download] Got server HTTP error: HTTP Error 404: Not Found. Retrying fragment 192 (attempt 5 of 10)..."
    txt[18]="[download] Got server HTTP error: HTTP Error 404: Not Found. Retrying fragment 192 (attempt 6 of 10)..."
    txt[19]="[download] Got server HTTP error: HTTP Error 404: Not Found. Retrying fragment 192 (attempt 7 of 10)..."
    txt[20]="[download] Got server HTTP error: HTTP Error 404: Not Found. Retrying fragment 192 (attempt 8 of 10)..."
    txt[21]="[download] Got server HTTP error: HTTP Error 404: Not Found. Retrying fragment 192 (attempt 9 of 10)..."
    txt[22]="[download] Got server HTTP error: HTTP Error 404: Not Found. Retrying fragment 192 (attempt 10 of 10)..."
    txt[23]="[download] Skipping fragment 192..."
    
    
    for index in range(len(txt)):
        line= txt[index]
        if TITLE.search(line):
            s=TITLE.search(line)
            found = s.groups()
            #ok=TITLE.match(line)
            #print("OK:",ok.group(0)," #1:",ok.group(1)," #2:",ok.group(1))
            print("Raw=",s.group(0)," TITLE:",s.group(1))
            for item in found:
                print("1:%s"%(item))
        else:
            print("not:",line)
if __name__ == '__main__':
    convert()
    pass