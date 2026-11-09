'''
Created on Oct 25, 2019

@author: matze
'''
import locale
from subprocess import Popen
import subprocess
import urllib
from urllib.parse import urlparse
import json
import re
import time
from datetime import timedelta,datetime
import sys
from FFMPEGTools import Log, ConfigAccessor, OSTools

# import threading
MODE_VIDEO = "V";
MODE_AUDIO = "A";
BACKEND_LOCAL = 1
BACKEND_DISTRO = 0
lang = locale.getlocale()

# If yt-dlp is present we use the distros one. Our binary will be delivered and can be activated by user 
INTRINSIC_YT_PATH = "/opt/ytdownloader/yt-dlp"
DISTRO_DL = "/usr/bin/yt-dlp"
if OSTools().fileExists(DISTRO_DL):
    YOUTUBE_DL = DISTRO_DL
elif OSTools().fileExists(INTRINSIC_YT_PATH):
    YOUTUBE_DL = INTRINSIC_YT_PATH
else:
    YOUTUBE_DL = None

TEXT_MAP = {}
if "en" in lang[0]:
    TEXT_MAP["TITLE"] = "Video Downloader"
    TEXT_MAP["LABEL_DROP_AREA"] = "Drop URLs onto list below"
    TEXT_MAP["BUTTON_OK"] = "Download"
    TEXT_MAP["BTN_INTERRUPT"] = " Interrupt "
    TEXT_MAP["BUTTON_CANX"] = "   Exit   "
    TEXT_MAP["MENU_DEL"] = "Remove"
    TEXT_MAP["MENU_DEL_ALL"] = "Remove all"
    TEXT_MAP["MENU_RELOAD"] = "Force Reload"
    TEXT_MAP["MENU_OPEN"] = "Open Folder"
    TEXT_MAP["FOLDER_MUSIC"] = "Music"
    TEXT_MAP["FOLDER_VIDEO"] = "Videos"
    TEXT_MAP["DIALOG_ERROR_TITLE"] = "Error Message"
    TEXT_MAP["DIALOG_ERROR_HEADER"] = "An error occurred )-:"
    TEXT_MAP["DIALOG_INFO_TITLE"] = "Information"
    TEXT_MAP["NOT_AN_URL_ERROR"] = "Invalid URL"
    TEXT_MAP["FILE_SAVE"] = "Name of TODO"
    TEXT_MAP["COL1"] = "URL"
    TEXT_MAP["COL2"] = "Title"
    TEXT_MAP["COL3"] = "Status"
    TEXT_MAP["COL4"] = "A/V"
    TEXT_MAP["INSTALL_YT"] = "Please install yt-dlp and ffmpeg"
    TEXT_MAP["TIP_TOOL_ADD"] = "Add URL manually"
    TEXT_MAP["TIP_TOOL_OPEN"] = "Load saved URL List"
    TEXT_MAP["TIP_TOOL_SAVE"] = "Save the URL List"
    TEXT_MAP["TIP_TOOL_UPDATE"] = "Update to the lastest yt-dlp"
    TEXT_MAP["COMBO_VIDEO"] = "Video+Audio"
    TEXT_MAP["COMBO_AUDIO"] = "Audio only"
    TEXT_MAP["TIP_TOOL_COMBO"] = "Dowload settings"
    TEXT_MAP["TIP_TOOL_SETTINGS"] = "File settings"
    TEXT_MAP["TIP_LIST"] = "Drop URL from browser here"
    TEXT_MAP["TIP_BTN_OK"] = "Start Download"
    TEXT_MAP["TIP_BTN_CANX"] = "Exit"
    TEXT_MAP["TIP_BTN_DEL"] = "Remove entry"
    TEXT_MAP["TIP_GROUP_LOAD"] = "Green = Single video,Orange = Playlist (slow!)"
    TEXT_MAP["LIST_LOADED"] = "List loaded"
    TEXT_MAP["LIST_SAVED"] = "List saved"
    TEXT_MAP["SETTINGS_DLG"] = "Settings dialog"
    TEXT_MAP["URL_DLG"] = "Add video URL"
    TEXT_MAP["ENTER_URL"] = "Enter video URL"
    # TEXT_MAP["SETTINGS_LABEL"]="Settings"
    TEXT_MAP["SET_AUDIO_LBL"] = "Store audio at:"
    TEXT_MAP["SET_VIDEO_LBL"] = "Store videos at:"
    TEXT_MAP["FOLDER_VIDEO_SAVE"] = "Video Folder"
    TEXT_MAP["FOLDER_AUDIO_SAVE"] = "Audio Folder"
    TEXT_MAP["DL_SETTINGS_TITLE"] = "Quality settings"
    TEXT_MAP["SEL_MP4"] = "Good quality with mp4"
    TEXT_MAP["SEL_MKV"] = "Highest quality with mkv"
    TEXT_MAP["SEL_ANY"] = "Highest quality auto container"
    TEXT_MAP["DL_AUDIO_TITLE"] = "Audio format (Audio only)"
    TEXT_MAP["SEL_MP3"] = "mp3 - plays on every device"
    TEXT_MAP["SEL_OPUS"] = "opus - best quality, small files"
    TEXT_MAP["SEL_ORIGINAL"] = "original - no conversion (m4a or webm)"
    TEXT_MAP["NO_DL"] = "Could not find yt-dlp. It should be in \n /usr/bin"
    TEXT_MAP["STATUS_INTERRUPT"] = "Process interrupted"
    TEXT_MAP["ALREADY_THERE"] = "File already downloaded"
    TEXT_MAP["STATUS_CONVERTING"] = "Converting audio..."
    TEXT_MAP["STATUS_MERGING"] = "Merging video and audio..."
    TEXT_MAP["STATUS_FILE_DONE"] = "Done"
    TEXT_MAP["STATUS_ALL_DONE"] = "All downloads completed"
    TEXT_MAP["DISTRO_YT"] = "Switch between the latest GIT(pressed) or distro yt-dlp"
    TEXT_MAP["DL_BROWSER_TITLE"] = "Select browser for cookies"
    TEXT_MAP["DL_BROWER_TIP"] = "You need to sign into Youtube. Select which browser has the cookie"
    TEXT_MAP["STATUS_UPDATING"] = "Updating yt-dlp..."
    TEXT_MAP["STATUS_BUSY_DROP"] = "Download running - no new URLs accepted"
    
elif "de" in lang[0]:
    TEXT_MAP["TITLE"] = "Video Downloader"
    TEXT_MAP["LABEL_DROP_AREA"] = "URLs auf die Liste ziehen"
    TEXT_MAP["BUTTON_OK"] = "Download"
    TEXT_MAP["BTN_INTERRUPT"] = "Stoppen "
    TEXT_MAP["BUTTON_CANX"] = "   Schließen   "
    TEXT_MAP["MENU_DEL"] = "Löschen"
    TEXT_MAP["MENU_DEL_ALL"] = "Alle löschen"
    TEXT_MAP["MENU_RELOAD"] = "Erneut Laden"
    TEXT_MAP["MENU_OPEN"] = "Ordner öffnen"
    TEXT_MAP["FOLDER_MUSIC"] = "Musik"
    TEXT_MAP["FOLDER_VIDEO"] = "Videos"
    TEXT_MAP["DIALOG_ERROR_TITLE"] = "Fehler Hinweis"
    TEXT_MAP["DIALOG_ERROR_HEADER"] = "Da ist ein Fehler passiert )-:"
    TEXT_MAP["DIALOG_INFO_TITLE"] = "Information"
    TEXT_MAP["NOT_AN_URL_ERROR"] = "Ungültige URL"
    TEXT_MAP["FILE_SAVE"] = "Wie soll die Datei heißen?"
    TEXT_MAP["COL1"] = "Adresse"
    TEXT_MAP["COL2"] = "Titel"
    TEXT_MAP["COL3"] = "Status"
    TEXT_MAP["COL4"] = "A/V"
    TEXT_MAP["INSTALL_YT"] = "Bitte yt-dlp und ffmpeg installieren"
    TEXT_MAP["TIP_TOOL_ADD"] = "Youtube URL eingeben"
    TEXT_MAP["TIP_TOOL_OPEN"] = "URL Liste laden"
    TEXT_MAP["TIP_TOOL_SAVE"] = "URL Liste speichern"
    TEXT_MAP["TIP_TOOL_UPDATE"] = "Update auf die neuste yt-dlp"
    TEXT_MAP["COMBO_VIDEO"] = "Video+Audio"
    TEXT_MAP["COMBO_AUDIO"] = "nur Audio"
    TEXT_MAP["TIP_TOOL_COMBO"] = "Einstellung für Download"
    TEXT_MAP["TIP_TOOL_SETTINGS"] = "Einstellungen für Dateien"
    TEXT_MAP["TIP_LIST"] = "URL vom Browser hierher ziehen"
    TEXT_MAP["TIP_BTN_OK"] = "Download starten"
    TEXT_MAP["TIP_BTN_CANX"] = "Beenden"
    TEXT_MAP["TIP_BTN_DEL"] = "Eintrag löschen"
    TEXT_MAP["TIP_GROUP_LOAD"] = "Grün = Einzel Video,Orange = Playlist (dauert!)"    
    TEXT_MAP["LIST_LOADED"] = "Liste geladen"
    TEXT_MAP["LIST_SAVED"] = "Liste gespeichert"
    TEXT_MAP["SETTINGS_DLG"] = "Einstellungen"
    TEXT_MAP["SET_AUDIO_LBL"] = "Ordner für Musik:"
    TEXT_MAP["SET_VIDEO_LBL"] = "Ordner für Videos"    
    TEXT_MAP["URL_DLG"] = "Video Adresse"
    TEXT_MAP["ENTER_URL"] = "Manuelle Eingabe der Video URL"
    # TEXT_MAP["SETTINGS_LABEL"]="Einstellungen"
    TEXT_MAP["FOLDER_VIDEO_SAVE"] = "Video Ordner"
    TEXT_MAP["FOLDER_AUDIO_SAVE"] = "Audio Ordner"
    TEXT_MAP["DL_SETTINGS_TITLE"] = "Qualitätseinstellungen"
    TEXT_MAP["SEL_MP4"] = "Gute Qualität im mp4 Format"
    TEXT_MAP["SEL_MKV"] = "Sehr gute Qualität im mkv Format"
    TEXT_MAP["SEL_ANY"] = "Sehr gute Qualität im beliebigen Format"
    TEXT_MAP["DL_AUDIO_TITLE"] = "Audio Format (nur Audio)"
    TEXT_MAP["SEL_MP3"] = "mp3 - läuft auf jedem Gerät"
    TEXT_MAP["SEL_OPUS"] = "opus - beste Qualität, kleine Dateien"
    TEXT_MAP["SEL_ORIGINAL"] = "Original - keine Umwandlung (m4a oder webm)"
    TEXT_MAP["NO_DL"] = "yt-dlp nicht gefunden. Sollte in\n /usr/bin sein"
    TEXT_MAP["STATUS_INTERRUPT"] = "Download abgebrochen"
    TEXT_MAP["ALREADY_THERE"] = "Datei schon geladen"
    TEXT_MAP["STATUS_CONVERTING"] = "Konvertiere Audio..."
    TEXT_MAP["STATUS_MERGING"] = "Führe Video und Audio zusammen..."
    TEXT_MAP["STATUS_FILE_DONE"] = "Fertig"
    TEXT_MAP["STATUS_ALL_DONE"] = "Alle Downloads abgeschlossen"
    TEXT_MAP["DISTRO_YT"] = "Yt-dlp als GIT Version(gedrückt) oder Distro Version nutzen"  
    TEXT_MAP["DL_BROWSER_TITLE"] = "Brauser Auswahl für cookies"
    TEXT_MAP["DL_BROWER_TIP"] = "Youtube erwartet, das man eingeloggt ist. Wähle Deinen Brauser aus"
    TEXT_MAP["STATUS_UPDATING"] = "Aktualisiere yt-dlp..."
    TEXT_MAP["STATUS_BUSY_DROP"] = "Download läuft - keine neuen URLs"
    
    
def _t(s):
    if not s in TEXT_MAP:
        Log.warning('TEXT_MAP["%s"]="missing"', s)
        return s
    return TEXT_MAP[s]


class Model():
    FORMATS = ["mp4", "mkv", "any"]
    AUDIO_FORMATS = ["mp3", "opus", "original"]
    AUDIO_DEFAULT = "mp3"
    BRAUSER_DEFAULT="firefox";

    CONFIG_FOLDER = "YtDownloader"
    CONFIG_FILE = "yt.ini"
    #up to 1.6.3 the ini was a flat file directly in ~/.config
    LEGACY_CONFIG = "YtDownloader.ini"

    def __init__(self):
        self.text = TEXT_MAP
        self._migrateLegacyConfig()
        self.config = ConfigAccessor(self.CONFIG_FOLDER, self.CONFIG_FILE, "DATA")
        self._assureConfig()
        self.groupLoad = False #Yt hack of playlists

    '''
    The ini now lives beside the log in ~/.config/YtDownloader, the way
    VideoCut and EasyPlayer keep theirs. Carry the old flat file over once,
    otherwise the URL list and the chosen backend would be lost on upgrade.
    '''

    def _migrateLegacyConfig(self):
        cfgDir = OSTools().joinPathes(OSTools().getHomeDirectory(), ".config")
        legacy = OSTools().joinPathes(cfgDir, self.LEGACY_CONFIG)
        current = OSTools().joinPathes(cfgDir, self.CONFIG_FOLDER, self.CONFIG_FILE)
        if not OSTools().fileExists(legacy) or OSTools().fileExists(current):
            return
        try:
            OSTools().ensureDirectory(OSTools().getDirectory(current))
            OSTools().moveFile(legacy, current)
            Log.info("Migrated config %s -> %s", legacy, current)
        except OSError as osError:
            #a lost ini is a nuisance, not a reason to refuse to start
            Log.error("Could not migrate %s: %s", legacy, osError.strerror)


    def hasDistroYT(self):
        return OSTools().fileExists(DISTRO_DL)  # todo config setting
    
    def _assureConfig(self):

        self.config.read()
        x = self.config.getInt("SCREENX")
        if not x:
            home = OSTools().getHomeDirectory()
            self.config.set("SCREENX", "760")
            self.config.set("SCREENY", "450")
            pathM = OSTools().joinPathes(home, _t("FOLDER_MUSIC"))
            pathV = OSTools().joinPathes(home, _t("FOLDER_VIDEO"))
            if OSTools().isDirectory(pathM):
                self.config.set("DEST_MUSIC", pathM)
            else:
                self._setEmergencyFolder(home, "DEST_MUSIC")
            if OSTools().isDirectory(pathV):
                self.config.set("DEST_VIDEO", pathV)
            else:
                self._setEmergencyFolder(home, "DEST_VIDEO")
            self.config.set("DOWNLOAD_TYPE", MODE_VIDEO)  # video or audio
            self.config.set("URLList", json.dumps([]))
            self.config.set("FORMAT", self.FORMATS[0])
            self.config.set("AUDIO_FORMAT", self.AUDIO_DEFAULT)
    
    def getScreenX(self):
        return self.config.getInt("SCREENX")
    
    def getScreenY(self):
        return self.config.getInt("SCREENY")

    def setScreenX(self, anInt):
        self.config.set("SCREENX", str(anInt))
        
    def setScreenY(self, anInt): 
        self.config.set("SCREENY", str(anInt))

    def getMusicPath(self):
        return self.config.get("DEST_MUSIC")
    
    def setMusicPath(self, path):
        self.config.set("DEST_MUSIC", path)

    def setBrowser(self,browserName):
        self.config.set("BRAUSER", browserName)
        
    def getBrowser(self):
        br = self.config.get("BRAUSER")
        if br is None:
            br= self.BRAUSER_DEFAULT
        Log.debug("Using browser cookies: %s", br)
        return br

    def getVideoPath(self):
        return self.config.get("DEST_VIDEO")

    def setVideoPath(self, path):
        self.config.set("DEST_VIDEO", path)   
         
    def getDownloadTypeIndex(self):
        mode = self.config.get("DOWNLOAD_TYPE")
        if mode is MODE_VIDEO:
            return 0;
        return 1;

    def getDownloadType(self):
        return self.config.get("DOWNLOAD_TYPE")
    
    def setDownloadTypeIndex(self, anInt):
        # 0==Video, 1== Audio
        if anInt == 0:
            self.config.set("DOWNLOAD_TYPE", MODE_VIDEO)
        else:
            self.config.set("DOWNLOAD_TYPE", MODE_AUDIO)

    def setYtBackend(self, backendMode):
        self.config.set("BACKEND", str(backendMode))
    
    def getYtBackend(self):
        return self.config.getInt("BACKEND")
    
    def getURLList(self):
        txt = self.config.get("URLList")
        return json.loads(txt)
    
    def setURLList(self, anArray):
        txt = json.dumps(anArray)
        self.config.set("URLList", txt)
        self.config.store()
    
    def setFormat(self, aString):
        self.config.set("FORMAT", aString)

    def getFormat(self):
        return self.config.get("FORMAT")

    def setAudioFormat(self, aString):
        self.config.set("AUDIO_FORMAT", aString)

    def getAudioFormat(self):
        # missing in ini files written before this setting existed -> stay on mp3
        af = self.config.get("AUDIO_FORMAT")
        if af not in self.AUDIO_FORMATS:
            af = self.AUDIO_DEFAULT
        return af

    def hasValidLibrary(self):
        return YOUTUBE_DL is not None
    
    def _setEmergencyFolder(self, home, key):
        pathD = OSTools().joinPathes(home, "Downloads")
        OSTools().ensureDirectory(pathD)
        self.config.set(key, pathD)
                        
        
def convertURL(rawData):
    if len(rawData) < 1:
        return None
    
    text = urllib.parse.unquote(rawData)
    aParseResult = urlparse(text)

    if "http" in aParseResult.scheme:
        return aParseResult
    return None


# throws exception..


def executeAsync(cmd, commander, targetDir):
    stdout_line = None
    popen = subprocess.Popen(cmd, cwd=targetDir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
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
        #cropError throws most of the last line away - keep it all in the log
        Log.warning("yt-dlp exit code %d, last line: %s", return_code, (stdout_line or "").rstrip())
        form = cropError(stdout_line)
        raise Exception(form)


def cropError(errorText):
    if errorText is None:
        return 
    text = errorText.split('. ') 
    text = text[-1].split(";")
    return text[0]


def errorToText(error):
    if len(error.args) > 1:
        errTxt = error.args[1]
    else:
        errTxt = error.args[0]
    return errTxt
    
    
# Helper class for returning either result objects or errors
class ProcResult():

    def __init__(self, res=None, err=None):
        self.result = res
        self.error = err
        
    def hasError(self):
        return self.error is not None

'''
The downloader.
expects an object that can receive the progress data:
onProgress(percent(float), size with units (str), speed with units (str) 

best video & audio for mp4
yt-dlp -f bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio --merge-output-format mp4 https://www.youtube.com/watch?v=Xj3gU3jACe8

audio only. Youtube serves audio as a separate stream, so "bestaudio" alone already
downloads audio only (.m4a or .webm/Opus) - no video is fetched in any of these:

mp3 (default, plays everywhere - ffmpeg re-encodes Opus/AAC to mp3):
yt-dlp -f bestaudio/best --extract-audio --audio-quality 0 --audio-format mp3

opus (native webm stream, ffmpeg only repacks it - no re-encoding, no quality loss):
yt-dlp -f bestaudio[acodec=opus]/bestaudio/best --extract-audio --audio-format opus

original (no conversion at all, ffmpeg not needed. Gives .m4a or .webm):
yt-dlp -f bestaudio/best

very best only (trick=mkv)
yt-dlp -f bestvideo+bestaudio --merge-output-format mkv https://www.youtube.com/watch?v=Xj3gU3jACe8
or:
yt-dlp -f bestvideo+bestaudio https://www.youtube.com/watch?v=Xj3gU3jACe8
>>leads to a webm file. needs complete transcoding for mp4....(VP9+Opus)
'''


class Downloader():
    ISPRESENT = re.compile(r'.+has already been downloaded')
    REGEXP = re.compile(r"([0-9.]+)% of ([ ~]*[0-9.]+.iB) at *([A-z]+|[0-9.]+.iB/s)")
    DONE_TEST = re.compile(r'([0-9.]+)% [A-z ]+ ([0-9.]+)(.iB) in ([0-9:]+)')
    DONEWITHSPEED = re.compile(r'\[download\]\s+([0-9.]+%)\s+of\s+' 
                       r'([0-9.]+)(KiB|MiB|GiB|TiB)\s+' 
                       r'in\s+([0-9:]+)\s+at\s+' 
                       r'([0-9.]+)((?:KiB|MiB|GiB|TiB)/s)' )
    DONE = re.compile(r'\[download\]\s+([0-9.]+%)\s+of\s+'
                      r'([0-9.]+)(KiB|MiB|GiB|TiB)\s+'
                      r'in\s+([0-9:]+)'
)
    
    TITLE = re.compile(r"\[download\] Destination: (.+?)(?:\s*\.[^.\/\s]+)$")
    
    def __init__(self, receiver):
        self.client = receiver
        self.proc = None
        self.res = ProcResult(res=_t("STATUS_FILE_DONE"))
        self.downloadtime = timedelta(minutes=0)
        self.downloadSize = 0.0
        self.filename = None

    '''
    The yt-dlp arguments for the wanted target format. Built on each download,
    not cached in __init__: the GUI flips YOUTUBE_DL between the distro and the
    local binary at runtime, so a list built in the constructor would keep
    whichever path it was born with.
    '''

    def _buildCommand(self, videomode, quality, audioFormat):
        if videomode == MODE_AUDIO:
            # audioFormat may be None when called from an older config - mp3 stays the default
            if audioFormat == Model.AUDIO_FORMATS[1]:
                # acodec=opus picks the native webm stream, so ffmpeg only repacks it into .opus.
                # plain "bestaudio" would select the higher rated m4a and re-encode aac->opus
                args = ["-f", "bestaudio[acodec=opus]/bestaudio/best", "--extract-audio", "--audio-format", "opus"]
            elif audioFormat == Model.AUDIO_FORMATS[2]:
                args = ["-f", "bestaudio/best"]
            else:
                args = ["-f", "bestaudio/best", "--extract-audio", "--audio-quality", "0", "--audio-format", "mp3"]
        else:
            if quality == Model.FORMATS[0]:
                args = ["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]", "--merge-output-format", "mp4"]
            elif quality == Model.FORMATS[1]:
                args = ["-f", "bestvideo+bestaudio/best", "--merge-output-format", "mkv"]
            else:
                args = ["-f", "bestvideo+bestaudio/best"]
        return ["python3", YOUTUBE_DL, "-o", '%(title)s.%(ext)s'] + args

    def download(self, url, videomode, quality,browser,targetDir,audioFormat=None):
        # TODO --transcode-video to mp4?
        if YOUTUBE_DL is None:
            return ProcResult(None, _t("NO_DL"))

        # No player_client pinning: yt-dlp picks its own clients depending on
        # whether the cookies authenticate us, and keeps that list current.
        # Forcing web_embedded first made every non embeddable video fail with
        # "Playback on other websites has been disabled by the video owner",
        # and masked unrelated errors with the same message.
        cmd = self._buildCommand(videomode, quality, audioFormat)
        #cookie hack: https://www.reddit.com/r/youtubedl/comments/1kezfg1/problems_with_ytdlp_on_yt/
        if browser:
            cookie = ["--cookies-from-browser",browser,url]
        else:
            cookie = [url]
        command = cmd + cookie
        Log.info("yt-dlp: %s", " ".join(command))
        start = time.monotonic() - 1000
        try:
            for line in executeAsync(command, self, targetDir):
                now = time.monotonic()
                elapsed = int(now - start)
                showProgress = elapsed >= 1
                err = self.parseAndDispatch(line, showProgress)
                if showProgress:
                    start = now
                if err is not None:
                    self.res.error = err
        except StopAsyncIteration as error:
            Log.info("Download interrupted by user")
            self.client.onProgress(None, _t("STATUS_INTERRUPT"))

        except Exception as error:
            Log.exception("Download failed:")
            self.res.error = errorToText(error)
        self.proc = None
        if not self.res.hasError():
            self.client.onProgressDone(_t("STATUS_FILE_DONE"), self.filename)
        return self.res
    
    def parseAndDispatch(self, line, showProgress):
        try: 
            m = self.REGEXP.search(line) 
            progress = float(m.group(1))
            # size = m.group(2)
            speed = m.group(3)
            if showProgress:
                self.client.onProgress(progress, speed)

        except Exception as error:
            if len(line) > 5:
                if self.ISPRESENT.match(line):
                    self.client.onProgressDone(_t("ALREADY_THERE"), self.filename)
                else:
                    m = self.DONE.search(line)
                    if m is not None:
                        ''' DONE:
                        proz = m.group(1)
                        size1 = m.group(2)
                        unit = m.group(3)
                        dur = m.group(4)
                        '''
                        proz = m.group(1)
                        size1 = m.group(2)
                        unit = m.group(3)
                        dur = m.group(4)
                        #speed = m.group(5)
                        #sUnit= m.group(6)
                        self.downloadSize += float(size1)
                        #need to add up audio and video time... 
                        '''
                        downloadtime: 0:00:00  delta: 0:00:00  line: [download] 100% of   30.56MiB in 00:00:05 at 6.00MiB/s   
                        <[download] 100% of   30.56MiB in 00:00:05 at 6.00MiB/s
                        <[download] Destination: 4K Video Sample H.264 (AVC).f258.m4a
                        downloadtime: 0:00:00  delta: 0:00:00  line: [download] 100% of    1.37MiB in 00:00:00 at 3.23MiB/s   
                        '''
                        t = datetime.strptime(dur,"%H:%M:%S")
                        td = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
                        self.downloadtime += td
                        #self.client.onProgressDone(proz + 'of ' + format(self.downloadSize, '.2f') + unit +" @ "+speed+sUnit, self.filename)
                        self.client.onProgressDone(f"{proz} of {format(self.downloadSize, '.2f')} {unit} in {self.downloadtime}",self.filename)
                    else:
                        # yt-dlp names the postprocessor ExtractAudio, but there is no
                        # video to extract from - it converts the audio codec
                        if '[ExtractAudio]' in line:
                            self.client.onProgress(100, _t("STATUS_CONVERTING"))
                        elif '[Merger]' in line:
                            self.client.onProgress(100, _t("STATUS_MERGING"))
                        else:
                            fn = self.TITLE.search(line)
                            if fn is not None:
                                self.filename = fn.group(1)
                if "ERROR" in line:
                    Log.error("ytdl| %s", line.rstrip())
                    return cropError(line)
                Log.debug("ytdl| %s", line.rstrip())
        return None
                
    def stop(self):
        if self.proc is None:
            Log.warning("Can't kill proc - no process running")
        else:
            Log.info("downloader - stop process")
            self.proc.kill()

    def setProcess(self, popen):
        self.proc = popen


def getListInfo(url,loadGroup):
    # read url and display list items
    # Not usable while downloading
    if YOUTUBE_DL is None:
        return ProcResult(None, _t("NO_DL"))
    #we have that startRadio syndrome:
    refinedURL = url.split('&start_radio')[0]
    if loadGroup:
        cmd = ["python3", YOUTUBE_DL, "-i", "-j", "--flat-playlist", refinedURL]
    else:
        refinedURL = url.split('&list')[0]
        #no player_client pinning here either - see Downloader.download
        cmd = ["python3", YOUTUBE_DL, "-i", "-j", "--no-playlist", refinedURL]

    Log.info("yt-dlp list: %s", " ".join(cmd))
    try:
        result = Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        form = None
        resArray = None
        if len(result[1]) > 0:
            # This is mostly an api problem
            stderr = result[1].decode("utf-8")
            Log.error("ytdl stderr: %s", stderr.rstrip())
            form = cropError(stderr)
            # return ProcResult(None,form)
        if len(result[0]) > 0:
            entries = result[0].decode("utf-8").splitlines()
            resArray = []
            for line in entries:
                resArray.append(json.loads(line))  # is a map
        return ProcResult(resArray, form if resArray is None else None)
    except Exception as error:
        Log.exception("Reading the URL info failed:")
        form = errorToText(error)
        return ProcResult(None, form)

    
def openFile(path):
    subprocess.call(('xdg-open', path))
# TODO make it async in thread


def play(path):
    cmd = ['xdg-open', path]
    process = Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # poll?


def removeFile(path):
    OSTools().removeFile(path)


def openFolder(root):
    cmd = ['xdg-open', root]
    subprocess.call(cmd)


def updateYt():
    # cmd=['pkexec',YOUTUBE_DL,'--update']
    cmd = ['pkexec', INTRINSIC_YT_PATH, "-U"]
    Log.info("yt-dlp update: %s", " ".join(cmd))
    result = Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    form = None
    resArray = None
    if len(result[1]) > 0:
            # This is mostly an api problem
            stderr = result[1].decode("utf-8")
            Log.error("update stderr: %s", stderr.rstrip())
            form = cropError(stderr)
    if len(result[0]) > 0:
        entries = result[0].decode("utf-8").splitlines()
        resArray = []
        for line in entries:
            Log.info("update| %s", line.rstrip())
            resArray.append(line)  # simple text
    return ProcResult(resArray, form)


def convert():
    TITLE = re.compile(r"\[download\][ Destination:]+ ([A-z 0-9-\w']+)+")
    TITLE = re.compile(r"\[download\] Destination: ([A-z 0-9-\w']+[^.]+)+")
    TITLE = re.compile(r"\[download\] Destination: ([^.]+)+")
    TITLE = re.compile(r"\[download\] Destination: (.+?)(?:\s*\.[^.\/\s]+)$")
    YTVID = re.compile(r"Extracting URL: .*?watch\?v=([^&\s]+)")
   
    txt = [0 for x in range(25)]
    txt[0] = "[download] De 23$%&/&=)?hfggfdgsdf sdfsdwe3454767565645.mp4"
    txt[1] = "[download] Destination: Pip _ A Short Animated Film-07d2dXHYb94.f137.mp4"
    txt[2] = "[download] Pip _ A Short Animated Film-07d2dXHYb94.mp4 has already been downloaded and merged"
    txt[3] = "[download] Destination: Poko 110 - Bowling For Minus-QwMfiVl4Wm0.f244.webm"
    txt[4] = "[download] Destination: CGI 3D Animated Short - 'Take Me Home' - by Nair Archawattana _ TheCGBros.f137.mp4"
    txt[24] = "[download] Destination: Mr. Crawly .mp4" 
    
    txt[5] = "[ARDBetaMediathek] magnus-trolljaeger/folge-1-ein-fall-fuer-idioten-s01-e01/ndr-fernsehen: Downloading JSON metadata"
    txt[6] = "[ARDBetaMediathek] 86159550: Downloading m3u8 information"
    txt[7] = "[hlsnative] Downloading m3u8 manifest"
    txt[8] = "[hlsnative] Total fragments: 192"
    txt[9] = "[download] Destination: Folge 1 - Ein Fall für Idioten (S01_E01).mp4"
    txt[10] = "[download]  49.5% of ~310.68MiB at  207.71B/s ETA 01:10"
    txt[11] = "[download]  49.5% of ~310.68MiB at  267.05B/s ETA 01:10"
    txt[12] = "[download]  49.5% of ~310.68MiB at  385.74B/s ETA 01:10"
    txt[13] = "[download]  49.5% of ~310.68MiB at  623.11B/s ETA 01:10"
    txt[14] = "[download] Got server HTTP error: HTTP Error 404: Not Found. Retrying fragment 192 (attempt 2 of 10)..."
    txt[15] = "[download] Got server HTTP error: HTTP Error 404: Not Found. Retrying fragment 192 (attempt 3 of 10)..."
    txt[16] = "[download] Got server HTTP error: HTTP Error 404: Not Found. Retrying fragment 192 (attempt 4 of 10)..."
    txt[17] = "[download] Got server HTTP error: HTTP Error 404: Not Found. Retrying fragment 192 (attempt 5 of 10)..."
    txt[18] = "[download] Got server HTTP error: HTTP Error 404: Not Found. Retrying fragment 192 (attempt 6 of 10)..."
    txt[19] = "[download] Got server HTTP error: HTTP Error 404: Not Found. Retrying fragment 192 (attempt 7 of 10)..."
    txt[20] = "[download] Got server HTTP error: HTTP Error 404: Not Found. Retrying fragment 192 (attempt 8 of 10)..."
    txt[21] = "[download] Got server HTTP error: HTTP Error 404: Not Found. Retrying fragment 192 (attempt 9 of 10)..."
    txt[22] = "[download] Got server HTTP error: HTTP Error 404: Not Found. Retrying fragment 192 (attempt 10 of 10)..."
    txt[23] = "[download] Skipping fragment 192..."
    txt[24] = "Extracting URL: https://www.youtube.com/watch?v=hnXqk_Hm-Bg"
    
    for index in range(len(txt)):
        line = txt[index]
        if TITLE.search(line):
            s = TITLE.search(line)
            found = s.groups()
            # ok=TITLE.match(line)
            # print("OK:",ok.group(0)," #1:",ok.group(1)," #2:",ok.group(1))
            print("Raw=", s.group(0), " TITLE:", s.group(1))
            for item in found:
                print("1:%s" % (item))
        elif YTVID.search(line):
            data = YTVID.search(line)
            print(data.group(1))
        else:
            print("not:", line)


if __name__ == '__main__':
    convert()
    pass
