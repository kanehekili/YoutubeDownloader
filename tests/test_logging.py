"""The rotating logger from the shared FFMPEGTools block.

The app used to debug through print(), which is lost the moment the GUI is
started from a desktop launcher - exactly the case where a yt-dlp failure needs
explaining afterwards. setupRotatingLogger keeps the structure VideoCut uses: a
5MB RotatingFileHandler with 5 backups, each rotated file gzipped by
OSTools().compressor, and the log placed next to the script when that directory
is writable, else under ~/.config/<AppName>.

That last rule is what makes the installed app work at all: the package lives
in root-owned /opt/ytdownloader, so the log has to land in the user's home,
beside the ini.

logging.basicConfig is global and a no-op once the root logger has handlers,
so every test here installs its own handlers into a tmpdir and tears them down
again.

    cd /home/matze/git/YoutubeDownloader && python3 -m unittest discover -s tests
"""
import glob
import gzip
import logging
import os
import sys
import tempfile
import unittest
from unittest import mock

import support

support.setupPath()

import FFMPEGTools  # noqa: E402
from FFMPEGTools import Log, OSTools  # noqa: E402


class LoggerTestCase(unittest.TestCase):
    """gives each test a tmpdir as "script dir" and a clean root logger"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(self._restoreLogging)
        self.handlers = logging.root.handlers
        self.level = logging.root.level
        self.logLevel = Log.level
        logging.root.handlers = []
        logging.disable(logging.NOTSET)

    def _restoreLogging(self):
        for h in logging.root.handlers:
            h.close()
        logging.root.handlers = self.handlers
        logging.root.level = self.level
        Log.setLevel(self.logLevel)

    def setupIn(self, folder, name="YtDownloader", console=False, logFolder=None):
        """run setupRotatingLogger as if FFMPEGTools.py lived in `folder`"""
        with mock.patch.object(OSTools, 'getLocalPath', return_value=folder):
            FFMPEGTools.setupRotatingLogger(name, console, logFolder)
        return os.path.join(folder, name + ".log")

    def read(self, path):
        with open(path, encoding="utf-8") as f:
            return f.read()

    def denyWriteTo(self, folder):
        """make exactly one directory look read-only to setupRotatingLogger"""
        realAccess = os.access

        def noWrite(path, mode):
            if path == folder and mode == os.W_OK:
                return False
            return realAccess(path, mode)

        return mock.patch.object(FFMPEGTools.os, 'access', side_effect=noWrite)


class LogFileTest(LoggerTestCase):

    def test_logLandsNextToTheScriptWhenWritable(self):
        """the development case - the log stays in src/"""
        path = self.setupIn(self.tmp)
        Log.info("hello")
        self.assertTrue(os.path.isfile(path))
        self.assertIn("hello", self.read(path))

    def test_readOnlyScriptDirFallsBackToConfig(self):
        """the installed case: /opt/ytdownloader belongs to root"""
        home = tempfile.mkdtemp()
        with mock.patch.object(OSTools, 'getHomeDirectory', return_value=home), \
             self.denyWriteTo(self.tmp):
            self.setupIn(self.tmp)
        Log.info("fallback")
        expected = os.path.join(home, ".config", "YtDownloader", "YtDownloader.log")
        self.assertTrue(os.path.isfile(expected), "log must land under ~/.config")
        self.assertIn("fallback", self.read(expected))

    def test_logFolderOverridesTheConfigSubdir(self):
        home = tempfile.mkdtemp()
        with mock.patch.object(OSTools, 'getHomeDirectory', return_value=home), \
             self.denyWriteTo(self.tmp):
            self.setupIn(self.tmp, logFolder="ytgui")
        Log.info("x")
        self.assertTrue(os.path.isfile(os.path.join(home, ".config", "ytgui", "YtDownloader.log")))

    def test_formatMatchesVideoCut(self):
        path = self.setupIn(self.tmp)
        Log.warning("careful")
        # 2026-11-08 00:12:13,456 WARNING : careful
        self.assertRegex(self.read(path).strip(),
                         r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} WARNING : careful$')

    def test_consoleHandlerOnlyOnRequest(self):
        self.setupIn(self.tmp, console=False)
        self.assertEqual([h for h in logging.root.handlers if type(h) is logging.StreamHandler], [])
        for h in logging.root.handlers:
            h.close()
        logging.root.handlers = []
        self.setupIn(self.tmp, console=True)
        streams = [h for h in logging.root.handlers if type(h) is logging.StreamHandler]
        self.assertEqual(len(streams), 1)
        self.assertIs(streams[0].stream, sys.stdout)

    def test_debugIsOnByDefault(self):
        """the whole point is the ytdl output, which is logged at debug"""
        path = self.setupIn(self.tmp)
        Log.debug("ytdl| [download] 42%")
        self.assertIn("ytdl| [download] 42%", self.read(path))

    def test_exceptionWritesATraceback(self):
        path = self.setupIn(self.tmp)
        try:
            raise ValueError("boom")
        except ValueError:
            Log.exception("Download failed:")
        written = self.read(path)
        self.assertIn("Download failed:", written)
        self.assertIn("ValueError: boom", written)
        self.assertIn("Traceback", written)


class LogLevelTest(LoggerTestCase):

    def test_setLogLevelFiltersLowerLevels(self):
        path = self.setupIn(self.tmp)
        FFMPEGTools.setLogLevel("Warning")
        Log.info("invisible")
        Log.warning("visible")
        written = self.read(path)
        self.assertNotIn("invisible", written)
        self.assertIn("visible", written)

    def test_everyLevelNameIsUnderstood(self):
        self.setupIn(self.tmp)
        for name, expected in (("Debug", logging.DEBUG), ("Info", logging.INFO),
                               ("Warning", logging.WARNING), ("Error", logging.ERROR)):
            with self.subTest(level=name):
                FFMPEGTools.setLogLevel(name)
                self.assertEqual(Log.level, expected)

    def test_unknownLevelNameIsIgnored(self):
        self.setupIn(self.tmp)
        FFMPEGTools.setLogLevel("Error")
        FFMPEGTools.setLogLevel("Verbose")
        self.assertEqual(Log.level, logging.ERROR)


class RotationTest(LoggerTestCase):

    def flood(self, lines=200):
        for i in range(lines):
            Log.info("filler line %d, long enough to roll the handler over", i)

    def test_handlerIsWiredToTheGzipRotator(self):
        self.setupIn(self.tmp)
        fh = logging.root.handlers[0]
        self.assertEqual(fh.maxBytes, 5 * 1024 * 1024)
        self.assertEqual(fh.backupCount, 5)
        self.assertEqual(fh.namer("YtDownloader.log.1"), "YtDownloader.log.1.gz")

    def test_rotatedLogsAreGzippedAndReadable(self):
        path = self.setupIn(self.tmp)
        logging.root.handlers[0].maxBytes = 1024
        self.flood()
        archives = glob.glob(path + ".*.gz")
        self.assertTrue(archives, "rotation must leave .gz files behind")
        with gzip.open(archives[0], "rt", encoding="utf-8") as gz:
            self.assertIn("filler line", gz.read())

    def test_uncompressedBackupsAreRemoved(self):
        """compressor() deletes the source - plain .log.N must not pile up"""
        path = self.setupIn(self.tmp)
        logging.root.handlers[0].maxBytes = 1024
        self.flood()
        for n in range(1, 6):
            self.assertFalse(os.path.exists(f"{path}.{n}"), f"{path}.{n} left uncompressed")

    def test_backupCountIsHonoured(self):
        path = self.setupIn(self.tmp)
        logging.root.handlers[0].maxBytes = 512
        self.flood(2000)
        self.assertLessEqual(len(glob.glob(path + ".*.gz")), 5)


if __name__ == '__main__':
    unittest.main()
