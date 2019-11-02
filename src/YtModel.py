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
from fileinput import filename

#import threading
MODE_VIDEO=0;
MODE_AUDIO=1;
lang = locale.getdefaultlocale()

TEXT_MAP = {}
if "en" in lang[0]:
    TEXT_MAP["TITLE"]="You Tube Downloader"
    TEXT_MAP["LABEL_DROP_AREA"]="Drop URLs onto list below"
    TEXT_MAP["BUTTON_OK"]="Download"
    TEXT_MAP["BUTTON_CANX"]="   Done   "
    TEXT_MAP["BUTTON_DEL"]="Delete"
    TEXT_MAP["FOLDER_MUSIC"]="Music"
    TEXT_MAP["FOLDER_VIDEO"]="Videos"
    TEXT_MAP["DIALOG_TITLE_ERROR"]="An error occurred )-:"
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
    TEXT_MAP["FOLDER_VIDEO_SAVE"]="Video Folder"
    TEXT_MAP["FOLDER_AUDIO_SAVE"]="Audio Folder"
elif "de" in lang[0]:
    TEXT_MAP["TITLE"]="You Tube Downloader"
    TEXT_MAP["LABEL_DROP_AREA"]="URLs auf die Liste ziehen"
    TEXT_MAP["BUTTON_OK"]="Download"
    TEXT_MAP["BUTTON_CANX"]="   Fertig   "
    TEXT_MAP["BUTTON_DEL"]=" Löschen "
    TEXT_MAP["FOLDER_MUSIC"]="Musik"
    TEXT_MAP["FOLDER_VIDEO"]="Videos"
    TEXT_MAP["DIALOG_TITLE_ERROR"]="Da ist ein Fehler passiert )-:"
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
    TEXT_MAP["URL_DLG"]="Video Adresse"
    TEXT_MAP["ENTER_URL"]="Manuelle Eingabe der Video URL"
    TEXT_MAP["SETTINGS_LABEL"]="Einstellungen"
    TEXT_MAP["FOLDER_VIDEO_SAVE"]="Video Ordner"
    TEXT_MAP["FOLDER_AUDIO_SAVE"]="Audio Ordner"
def _t(s):
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

def executeAsync(cmd,commander,targetDir):
    popen = subprocess.Popen(cmd, cwd=targetDir,stdout=subprocess.PIPE,stderr=subprocess.STDOUT, universal_newlines=True)
    commander.setProcess(popen)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)
    

'''
The downloader.
expects an object that can receive the progress data:
onProgress(percent(float), size with units (str), speed with units (str) 
'''
class Downloader():
    ISPRESENT = re.compile('.+has already been downloaded')
    REGEXP = re.compile("([0-9.]+)% of ([~]*[0-9.]+.iB) at *([A-z]+|[0-9.]+.iB/s)")
    DONE = re.compile('([0-9.]+)% [A-z]+ ([0-9.]+.iB) in ([0-9:]+)' )
    
    def __init__(self,receiver):
        self.client = receiver
        self.proc = None
        

    def download(self,url,videomode,targetDir):
        #TODO --recode-video mp4
        cmd=["/usr/bin/youtube-dl","-f","best"]
        if videomode==MODE_AUDIO:
            cmd.extend(["--extract-audio","--audio-format","mp3","--audio-quality","0"])
        cmd.append(url)
        error = None
        start = time.monotonic()-1000
        for line in executeAsync(cmd,self,targetDir):
            now= time.monotonic()
            elapsed = int(now-start)
            showProgress=elapsed>=1
            err = self.parseAndDispatch(line,showProgress)
            if showProgress:
                start=now
            if err is not None:
                error=err
        return error   
            
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
                    self.client.onProgress(100.,"0","0")
                else:
                    m = self.DONE.search(line)
                    if m is not None:
                        self.client.onProgressDone(m.group(0))
                    
                print ("<"+line.rstrip())  
                if "ERROR" in line:
                    print("error:%s"%(line));#TODO
                    return line
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
    cmd=["/usr/bin/youtube-dl","-j",url]
    result = Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
    if len(result[0])>0:
        text= result[0].decode("utf-8")
        result = json.loads(text) #is a map
        #json.dumps(map) is the reverse....
        #for item in result.items():
        #    print(item)
        return result 
'''
too slow - use get info instead. Slow too.
    cmd=["/usr/bin/youtube-dl","-e",url]
'''
def jsontest1():
    test=["A","B","C"]
    jarray = json.dumps(test)
    print(jarray)
    test2 = json.loads(jarray)    
    print(test2)

def test():
    regexp = re.compile("([0-9.]+)% of ([~]*[0-9.]+.iB) at *([A-z]+|[0-9.]+.iB/s)")
    #uk = re.compile("([0-9.]+)% [A-z]+ ([~]*[0-9.]+.iB) at *([A-z]+)")
    #text="[download]   0.0% of 8.72MiB at 615.99KiB/s ETA 00:14"
    text="[download] 100.0% of 8.72MiB at  6.85MiB/s ETA 00:00"
    test2='[download] 100.0% of ~345.91MiB at  6.49MiB/s ETA 00:00'
    test3='[download]  13.9% of ~346.95MiB at Unknown speed ETA 00:04'
    m = regexp.search(text)
    found = m.groups()
    print(m.group(0))
    for item in found:
        print("1:%s"%(item))
    m = regexp.search(test2)
    found = m.groups()
    print(m.group(0))
    for item in found:
        print("2:%s"%(item))
    m = regexp.search(test3)
    found = m.groups()
    print(m.group(0))
    for item in found:
        print("3:%s"%(item))
                    
def test2():
    text='[download] Philips PM5644 test pattern 1920 x 1080px HD-yaqe1qesQ8c.mp4 has already been downloaded'
    ISPRESENT = re.compile('.+has already been downloaded')
    if ISPRESENT.match(text):
        print("ok")

def test3():
    text='[download] 100% of 345.91MiB in 01:00'
    DONE = re.compile('([0-9.]+)% [A-z]+ ([0-9.]+.iB) in ([0-9:]+)' )
    ok=DONE.match(text)
    print(ok)
    m = DONE.search(text)
    found = m.groups()
    print(m.group(0))
    for item in found:
        print("1:%s"%(item))

          
if __name__ == '__main__':
    #getInfo("https://www.youtube.com/watch?v=nYh-n7EOtMA")
    #download("https://www.youtube.com/watch?v=yaqe1qesQ8c", MODE_VIDEO, "/home/matze/Videos/test")
    test3()
    pass