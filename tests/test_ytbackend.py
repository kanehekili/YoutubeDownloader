"""The yt-dlp command line this app hands to the backend.

Two things are nailed down here.

1. No player_client pinning. Commit 887d145 hardcoded
   `--extractor-args youtube:player_client=web_embedded,web,tv` for every
   youtube URL. web_embedded fetches through /embed/<id>, so every video whose
   owner disabled embedding failed with "Playback on other websites has been
   disabled by the video owner" - and because yt-dlp reports the *first*
   client's playability reason, that message also masked unrelated failures
   like bot checks and rate limits. yt-dlp chooses its own clients depending on
   whether the cookies authenticate the session, and keeps that choice current.

2. The backend path is read when the download starts, not when the Downloader
   is constructed. The GUI reassigns YtModel.YOUTUBE_DL when the user flips the
   GIT/distro switch, so command lists cached in __init__ would keep whichever
   binary they were born with.

Plain unittest, no network - executeAsync and Popen are mocked:

    cd /home/matze/git/YoutubeDownloader && python3 -m unittest discover -s tests
"""
import logging
import unittest
from unittest import mock

import support

support.setupPath()

import YtModel  # noqa: E402


def setUpModule():
    """no logger is configured here, so Log.error would reach logging's
    lastResort handler and litter the test output - test_logging covers it"""
    logging.disable(logging.CRITICAL)


def tearDownModule():
    logging.disable(logging.NOTSET)


YOUTUBE_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
SHORT_URL = "https://youtu.be/dQw4w9WgXcQ"
OTHER_URL = "https://www.ardmediathek.de/video/xyz"


class CommandBuilderTest(unittest.TestCase):
    """Downloader._buildCommand - the format arguments per download mode"""

    def setUp(self):
        self.dl = YtModel.Downloader(mock.Mock())

    def video(self, quality):
        return self.dl._buildCommand(YtModel.MODE_VIDEO, quality, None)

    def audio(self, audioFormat):
        return self.dl._buildCommand(YtModel.MODE_AUDIO, YtModel.Model.FORMATS[0], audioFormat)

    def formatOf(self, cmd):
        return cmd[cmd.index("-f") + 1]

    def test_mp4AsksForMp4Streams(self):
        cmd = self.video("mp4")
        self.assertEqual(self.formatOf(cmd), "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]")
        self.assertEqual(cmd[cmd.index("--merge-output-format") + 1], "mp4")

    def test_mkvMergesIntoMkv(self):
        cmd = self.video("mkv")
        self.assertEqual(self.formatOf(cmd), "bestvideo+bestaudio/best")
        self.assertEqual(cmd[cmd.index("--merge-output-format") + 1], "mkv")

    def test_anyLeavesTheContainerToYtdlp(self):
        cmd = self.video("any")
        self.assertEqual(self.formatOf(cmd), "bestvideo+bestaudio/best")
        self.assertNotIn("--merge-output-format", cmd)

    def test_mp3ReencodesToMp3(self):
        cmd = self.audio("mp3")
        self.assertIn("--extract-audio", cmd)
        self.assertEqual(cmd[cmd.index("--audio-format") + 1], "mp3")

    def test_opusTakesTheNativeWebmStream(self):
        """acodec=opus makes ffmpeg repack rather than re-encode aac->opus"""
        cmd = self.audio("opus")
        self.assertEqual(self.formatOf(cmd), "bestaudio[acodec=opus]/bestaudio/best")
        self.assertEqual(cmd[cmd.index("--audio-format") + 1], "opus")

    def test_originalDoesNotConvertAtAll(self):
        cmd = self.audio("original")
        self.assertNotIn("--extract-audio", cmd)
        self.assertNotIn("--audio-format", cmd)

    def test_unknownAudioFormatFallsBackToMp3(self):
        """configs written before the audio setting existed have no value"""
        for bogus in (None, "", "flac"):
            with self.subTest(audioFormat=bogus):
                self.assertEqual(self.audio(bogus)[-1], "mp3")

    def test_audioModesNeverFetchVideo(self):
        for fmt in YtModel.Model.AUDIO_FORMATS:
            with self.subTest(audioFormat=fmt):
                self.assertTrue(self.formatOf(self.audio(fmt)).startswith("bestaudio"))

    def test_outputTemplateIsAlwaysPresent(self):
        self.assertEqual(self.video("mp4")[self.video("mp4").index("-o") + 1], '%(title)s.%(ext)s')


class BackendPathTest(unittest.TestCase):
    """the GIT/distro switch must reach a Downloader that already exists"""

    def test_commandUsesTheCurrentBackend(self):
        with mock.patch.object(YtModel, 'YOUTUBE_DL', '/usr/bin/yt-dlp'):
            dl = YtModel.Downloader(mock.Mock())
            self.assertEqual(dl._buildCommand(YtModel.MODE_VIDEO, "mp4", None)[1], '/usr/bin/yt-dlp')

    def test_switchAfterConstructionIsPickedUp(self):
        """this is what broke while the lists were cached in __init__"""
        with mock.patch.object(YtModel, 'YOUTUBE_DL', '/usr/bin/yt-dlp'):
            dl = YtModel.Downloader(mock.Mock())
        with mock.patch.object(YtModel, 'YOUTUBE_DL', '/opt/ytdownloader/yt-dlp'):
            cmd = dl._buildCommand(YtModel.MODE_VIDEO, "mp4", None)
        self.assertEqual(cmd[1], '/opt/ytdownloader/yt-dlp')


class DownloadCommandTest(unittest.TestCase):
    """the whole command as it reaches executeAsync"""

    def capture(self, url, browser=None, videomode=None, quality="mp4"):
        dl = YtModel.Downloader(mock.Mock())
        with mock.patch.object(YtModel, 'executeAsync', return_value=iter(())) as ea:
            dl.download(url, videomode or YtModel.MODE_VIDEO, quality, browser, "/tmp")
        return ea.call_args[0][0]

    def test_noExtractorArgsForYoutube(self):
        for url in (YOUTUBE_URL, SHORT_URL):
            with self.subTest(url=url):
                cmd = self.capture(url)
                self.assertNotIn('--extractor-args', cmd)
                self.assertFalse([a for a in cmd if 'player_client' in a])

    def test_noExtractorArgsForOtherSites(self):
        self.assertNotIn('--extractor-args', self.capture(OTHER_URL))

    def test_webEmbeddedIsNeverRequested(self):
        """the client that produced the "disabled by the video owner" error"""
        self.assertFalse([a for a in self.capture(YOUTUBE_URL) if 'web_embedded' in a])

    def test_urlIsTheLastArgument(self):
        self.assertEqual(self.capture(YOUTUBE_URL)[-1], YOUTUBE_URL)

    def test_browserCookiesArePassed(self):
        cmd = self.capture(YOUTUBE_URL, browser="firefox")
        self.assertEqual(cmd[cmd.index('--cookies-from-browser') + 1], "firefox")
        self.assertEqual(cmd[-1], YOUTUBE_URL)

    def test_noCookieOptionWithoutBrowser(self):
        self.assertNotIn('--cookies-from-browser', self.capture(YOUTUBE_URL))

    def test_missingBackendIsReportedNotCrashed(self):
        with mock.patch.object(YtModel, 'YOUTUBE_DL', None):
            res = YtModel.Downloader(mock.Mock()).download(YOUTUBE_URL, YtModel.MODE_VIDEO, "mp4", None, "/tmp")
        self.assertTrue(res.hasError())


class ListInfoCommandTest(unittest.TestCase):
    """getListInfo builds its own command - it carried the same pinning"""

    def capture(self, url, loadGroup=False, stdout=b'{"id":"x","title":"t"}', stderr=b''):
        proc = mock.Mock(**{'communicate.return_value': (stdout, stderr)})
        with mock.patch.object(YtModel, 'Popen', return_value=proc) as popen:
            res = YtModel.getListInfo(url, loadGroup)
        return popen.call_args[0][0], res

    def test_noExtractorArgsForSingleVideo(self):
        cmd, _ = self.capture(YOUTUBE_URL)
        self.assertNotIn('--extractor-args', cmd)
        self.assertFalse([a for a in cmd if 'player_client' in a])

    def test_noExtractorArgsForPlaylist(self):
        cmd, _ = self.capture(YOUTUBE_URL, loadGroup=True)
        self.assertNotIn('--extractor-args', cmd)

    def test_singleVideoSuppressesThePlaylist(self):
        cmd, _ = self.capture(YOUTUBE_URL)
        self.assertIn('--no-playlist', cmd)
        self.assertEqual(cmd[-1], YOUTUBE_URL)

    def test_playlistModeAsksForAFlatList(self):
        cmd, _ = self.capture(YOUTUBE_URL, loadGroup=True)
        self.assertIn('--flat-playlist', cmd)

    def test_startRadioIsStrippedFromPlaylistUrls(self):
        cmd, _ = self.capture(YOUTUBE_URL + "&start_radio=1", loadGroup=True)
        self.assertEqual(cmd[-1], YOUTUBE_URL)

    def test_listIsStrippedForSingleVideo(self):
        cmd, _ = self.capture(YOUTUBE_URL + "&list=PL123")
        self.assertEqual(cmd[-1], YOUTUBE_URL)

    def test_parsedEntriesAreReturned(self):
        _, res = self.capture(YOUTUBE_URL)
        self.assertFalse(res.hasError())
        self.assertEqual(res.result[0]["title"], "t")

    def test_stderrBecomesAnErrorWhenNothingWasParsed(self):
        _, res = self.capture(YOUTUBE_URL, stdout=b'', stderr=b'ERROR: nope')
        self.assertTrue(res.hasError())


if __name__ == '__main__':
    unittest.main()
