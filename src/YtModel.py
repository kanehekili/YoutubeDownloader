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
MODE_VIDEO=0;
MODE_AUDIO=1;
lang = locale.getdefaultlocale()

YOUTUBE_DL="/usr/bin/youtube-dl"
if not os.path.exists(YOUTUBE_DL):
    YOUTUBE_DL="/usr/local/bin/youtube-dl"    
if not os.path.exists(YOUTUBE_DL):
    YOUTUBE_DL=None

TEXT_MAP = {}
if "en" in lang[0]:
    TEXT_MAP["TITLE"]="Video Downloader"
    TEXT_MAP["LABEL_DROP_AREA"]="Drop URLs onto list below"
    TEXT_MAP["BUTTON_OK"]="Download"
    TEXT_MAP["BUTTON_CANX"]="   Exit   "
    TEXT_MAP["BUTTON_DEL"]="Delete"
    TEXT_MAP["FOLDER_MUSIC"]="Music"
    TEXT_MAP["FOLDER_VIDEO"]="Videos"
    TEXT_MAP["DIALOG_ERROR_TITLE"]="Error Message"
    TEXT_MAP["DIALOG_ERROR_HEADER"]="An error occurred )-:"
    TEXT_MAP["NOT_AN_URL_ERROR"]="Invalid URL"
    TEXT_MAP["FILE_SAVE"]="Name of TODO"
    TEXT_MAP["COL1"]="URL"
    TEXT_MAP["COL2"]="Title"
    TEXT_MAP["COL3"]="Status"
    TEXT_MAP["INSTALL_YT"]="Please install youtube-dl and ffmpeg"
    TEXT_MAP["TIP_TOOL_ADD"]="Add URL manually"
    TEXT_MAP["TIP_TOOL_OPEN"]="Load saved URL List"
    TEXT_MAP["TIP_TOOL_SAVE"]="Save the URL List"
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
    TEXT_MAP["SETTINGS_LABEL"]="Settings"
    TEXT_MAP["SET_AUDIO_LBL"]="Store audio at:"
    TEXT_MAP["SET_VIDEO_LBL"]="Store videos at:"
    TEXT_MAP["FOLDER_VIDEO_SAVE"]="Video Folder"
    TEXT_MAP["FOLDER_AUDIO_SAVE"]="Audio Folder"
    TEXT_MAP["DL_SETTINGS_TITLE"]="Quality settings"
    TEXT_MAP["SEL_MP4"]="Good quality with mp4"
    TEXT_MAP["SEL_MKV"]="Highest quality with mkv"
    TEXT_MAP["SEL_ANY"]="Highest quality auto container"
    TEXT_MAP["NO_DL"]="Could not find youtube-dl. It should be either in \n /usr/bin or /usr/local/bin"
    
elif "de" in lang[0]:
    TEXT_MAP["TITLE"]="You Tube Downloader"
    TEXT_MAP["LABEL_DROP_AREA"]="URLs auf die Liste ziehen"
    TEXT_MAP["BUTTON_OK"]="Download"
    TEXT_MAP["BUTTON_CANX"]="   Schließen   "
    TEXT_MAP["BUTTON_DEL"]=" Löschen "
    TEXT_MAP["FOLDER_MUSIC"]="Musik"
    TEXT_MAP["FOLDER_VIDEO"]="Videos"
    TEXT_MAP["DIALOG_ERROR_TITLE"]="Fehler Hinweis"
    TEXT_MAP["DIALOG_ERROR_HEADER"]="Da ist ein Fehler passiert )-:"
    TEXT_MAP["NOT_AN_URL_ERROR"]="Ungültige URL"
    TEXT_MAP["FILE_SAVE"]="Wie soll die Datei heißen?"
    TEXT_MAP["COL1"]="Adresse"
    TEXT_MAP["COL2"]="Titel"
    TEXT_MAP["COL3"]="Status"
    TEXT_MAP["INSTALL_YT"]="Bitte youtube-dl und ffmpeg installieren"
    TEXT_MAP["TIP_TOOL_ADD"]="Youtube URL eingeben"
    TEXT_MAP["TIP_TOOL_OPEN"]="URL Liste laden"
    TEXT_MAP["TIP_TOOL_SAVE"]="URL Liste speichern"
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
    TEXT_MAP["SETTINGS_LABEL"]="Einstellungen"
    TEXT_MAP["FOLDER_VIDEO_SAVE"]="Video Ordner"
    TEXT_MAP["FOLDER_AUDIO_SAVE"]="Audio Ordner"
    TEXT_MAP["DL_SETTINGS_TITLE"]="Qualitätseinstellungen"
    TEXT_MAP["SEL_MP4"]="Gute Qualität im mp4 Format"
    TEXT_MAP["SEL_MKV"]="Sehr gute Qualität im mkv Format"
    TEXT_MAP["SEL_ANY"]="Sehr gute Qualität im beliebigen Format"
    TEXT_MAP["NO_DL"]="youtube-dl nicht gefunden. Sollte entweder in\n /usr/bin oder /usr/local/bin sein"
    
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
            self.config.add("DOWNLOAD_TYPE",str(MODE_VIDEO))#video or audio
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
         
    def getDownloadType(self):
        return self.config.getInt("DOWNLOAD_TYPE")
    
    def setDownloadType(self,anInt):
        self.config.add("DOWNLOAD_TYPE", str(anInt))
    
    def getURLList(self):
        txt = self.config.get("URLList")
        return json.loads(txt)
    
    def setURLList(self,anArray):
        txt= json.dumps(anArray)
        self.config.add("URLList",txt)
    
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
    data = rawData.split('&')
    if len(data)< 1:
        return None
    
    text = urllib.parse.unquote(data[0])
    aParseResult = urlparse(text)
    if "http" in aParseResult.scheme:
        print(aParseResult.geturl())
        return aParseResult
    return None

#throws exception..
import signal
def executeAsync(cmd,commander,targetDir):
    popen = subprocess.Popen(cmd, cwd=targetDir,stdout=subprocess.PIPE,stderr=subprocess.STDOUT, universal_newlines=True)
    commander.setProcess(popen)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        form=cropError(stdout_line)
        raise Exception(form)

def cropError(errorText):
    form=''
    #text= error.replace('"','*')
    text = errorText.split('. ') 
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
youtube-dl -f bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio --merge-output-format mp4 https://www.youtube.com/watch?v=Xj3gU3jACe8

bestaudio:
youtube-dl -f bestaudio --extract-audio --audio-quality 0 --audio-format mp3

very best only (trick=mkv)
youtube-dl -f bestvideo+bestaudio --merge-output-format mkv https://www.youtube.com/watch?v=Xj3gU3jACe8
or:
youtube-dl -f bestvideo+bestaudio https://www.youtube.com/watch?v=Xj3gU3jACe8
>>leads to a webm file. needs complete transcoding for mp4....(VP9+Opus)
'''
class Downloader():
    ISPRESENT = re.compile('.+has already been downloaded')
    REGEXP = re.compile("([0-9.]+)% of ([~]*[0-9.]+.iB) at *([A-z]+|[0-9.]+.iB/s)")
    DWN_SIZE =re.compile('([0-9.]+)([A-z]+)')
    DONE = re.compile('([0-9.]+)% [A-z]+ ([0-9.]+.iB) in ([0-9:]+)' )
    MP4 = [YOUTUBE_DL,"-f","bestvideo[ext=mp4]+bestaudio[ext=m4a]","--merge-output-format","mp4"]
    MKV = [YOUTUBE_DL,"-f","bestvideo+bestaudio","--merge-output-format","mkv"]
    ANY = [YOUTUBE_DL,"-f","bestvideo+bestaudio"]
    AUDIO = [YOUTUBE_DL,"-f","bestaudio","--extract-audio","--audio-quality","0","--audio-format","mp3"]
    
    def __init__(self,receiver):
        self.client = receiver
        self.proc = None
        self.res = ProcResult(res="Done")
        self.downloadtime=timedelta(minutes=0)
        self.downloadSize=0.0
        

    def download(self,url,videomode,quality,targetDir):
        #TODO --transcode-video to mp4?
        if YOUTUBE_DL is None:
            return ProcResult(None,_t("NO_DL"))

        cmd=[]
        if videomode==MODE_AUDIO:
            cmd = self.AUDIO
        else:
            if quality == Model.FORMATS[0]:
                cmd=self.MP4
            elif quality == Model.FORMATS[1]:
                cmd=self.MKV
            else:
                cmd=self.ANY
        cmd.append(url)
        start = time.monotonic()-1000
        try:
            for line in executeAsync(cmd,self,targetDir):
                now= time.monotonic()
                elapsed = int(now-start)
                showProgress=elapsed>=1
                err = self.parseAndDispatch(line,showProgress)
                if showProgress:
                    start=now
                if err is not None:
                    self.res.error = err
        except Exception as error:
            self.res.error=errorToText(error)
        return self.res   
            
    def parseAndDispatch(self,line,showProgress):
        
        try:        
            m = self.REGEXP.search(line) 
            progress = float(m.group(1))
            size = m.group(2)
            speed = m.group(3)
            if showProgress:
                #print("%.1f size:%s speed:%s "%(progress,size,speed))
                self.client.onProgress(progress,size,speed)

        except Exception as error:
            if len(line)>5:
                if self.ISPRESENT.match(line):
                    self.client.onProgressDone(None)
                else:
                    m = self.DONE.search(line)
                    if m is not None:
                        t1=m.group(1)
                        t2=m.group(2)
                        tf = self.DWN_SIZE.match(t2)
                        self.downloadSize+=float(tf.group(1))
                        rate = tf.group(2)                       
                        dm=m.group(3).split(':')
                        td=timedelta(minutes=int(int(dm[0])),seconds=int(dm[1]))
                        self.downloadtime+=td
                        self.client.onProgressDone(t1+'% of '+str(self.downloadSize)+rate+" in "+str(self.downloadtime))
                    
                print ("<"+line.rstrip())  
                if "ERROR" in line:
                    print("error:%s"%(line));#TODO
                    return cropError(line)
        return None 
    
                
    def stop(self):
        if self.proc is None:
            print("Can't kill proc!")
        else:
            print("VCCutter - stop process")
            self.proc.kill()

    def setProcess(self,popen):
        self.proc=popen
        
def getInfo(url):
    #read url and display info -DOES NOT RETURN if & is contained
    #Not usable while downloading
    if YOUTUBE_DL is None:
        return ProcResult(None,_t("NO_DL"))
    cmd=[YOUTUBE_DL,"-j",url]
    try:
        result = Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
        if len(result[1])>0:
            #This is mostly an api problem
            form=cropError(result[1].decode("utf-8"))
            return ProcResult(None,form)
        if len(result[0])>0:
            text= result[0].decode("utf-8")
            result = json.loads(text) #is a map
            return ProcResult(result,None)
    except Exception as error:
        form=errorToText(error)
        print(form)
        return ProcResult(None,form)

def convert():
    txt="38.12Mib"
    rex =re.compile('[0-9.]+')
    #sx = re.compile('[A-Z][a-z]+')
    sx = re.compile('([0-9.]+)([A-z]+)')
    m1= rex.match(txt)
    m2= sx.match(txt)
    print(m2.group(1))
    print(m2.group(2))
if __name__ == '__main__':
    convert()
    pass