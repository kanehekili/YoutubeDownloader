"""The ini moved into ~/.config/YtDownloader/ and must bring its contents.

Up to 1.6.3 the settings were a flat ~/.config/YtDownloader.ini. They now live
at ~/.config/YtDownloader/yt.ini, beside YtDownloader.log, the way VideoCut
keeps vc.ini and EasyPlayer ep.ini. Without the one-time migration an upgrade
would silently reset the URL list, the download folders and the GIT/distro
backend choice back to defaults.

    cd /home/matze/git/YoutubeDownloader && python3 -m unittest discover -s tests
"""
import json
import logging
import os
import tempfile
import unittest
from unittest import mock

import support

support.setupPath()

import YtModel  # noqa: E402
from FFMPEGTools import ConfigAccessor, OSTools  # noqa: E402

LEGACY = """[DATA]
screenx = 1043
screeny = 473
dest_music = /home/somebody/Music/VD
dest_video = /home/somebody/Videos/VD
download_type = A
urllist = [["abc123", "A Title", "0.0", "A", "https://www.youtube.com/watch?v=abc123"]]
format = any
backend = 1
brauser = firefox
audio_format = opus
"""


def setUpModule():
    logging.disable(logging.CRITICAL)


def tearDownModule():
    logging.disable(logging.NOTSET)


class MigrationTestCase(unittest.TestCase):
    """every test gets a private home, so the real ini is never touched"""

    def setUp(self):
        self.home = tempfile.mkdtemp()
        OSTools().ensureDirectory(os.path.join(self.home, ".config"))
        for target in (mock.patch.object(OSTools, 'getHomeDirectory', return_value=self.home),
                       mock.patch.object(ConfigAccessor, 'homeDir', self.home)):
            target.start()
            self.addCleanup(target.stop)

    @property
    def legacyPath(self):
        return os.path.join(self.home, ".config", "YtDownloader.ini")

    @property
    def currentPath(self):
        return os.path.join(self.home, ".config", "YtDownloader", "yt.ini")

    def writeLegacy(self, content=LEGACY):
        with open(self.legacyPath, "w", encoding="utf-8") as f:
            f.write(content)

    def writeCurrent(self, content=LEGACY):
        OSTools().ensureDirectory(os.path.dirname(self.currentPath))
        with open(self.currentPath, "w", encoding="utf-8") as f:
            f.write(content)


class ConfigLocationTest(MigrationTestCase):

    def test_iniLivesBesideTheLog(self):
        YtModel.Model()
        folder = os.path.join(self.home, ".config", "YtDownloader")
        self.assertTrue(os.path.isdir(folder))
        self.assertEqual(YtModel.Model.CONFIG_FILE, "yt.ini")

    def test_freshInstallCanStoreItsSettings(self):
        model = YtModel.Model()
        model.setVideoPath("/home/somebody/Videos")
        self.assertTrue(model.config.store())
        self.assertTrue(os.path.isfile(self.currentPath))


class LegacyMigrationTest(MigrationTestCase):

    def test_legacyIniIsMovedNotCopied(self):
        self.writeLegacy()
        YtModel.Model()
        self.assertTrue(os.path.isfile(self.currentPath), "new ini must exist")
        self.assertFalse(os.path.exists(self.legacyPath), "old ini must be gone")

    def test_settingsSurviveTheMove(self):
        self.writeLegacy()
        model = YtModel.Model()
        self.assertEqual(model.getVideoPath(), "/home/somebody/Videos/VD")
        self.assertEqual(model.getMusicPath(), "/home/somebody/Music/VD")
        self.assertEqual(model.getFormat(), "any")
        self.assertEqual(model.getAudioFormat(), "opus")
        self.assertEqual(model.getBrowser(), "firefox")
        self.assertEqual(model.getYtBackend(), YtModel.BACKEND_LOCAL)
        self.assertEqual(model.getDownloadType(), YtModel.MODE_AUDIO)

    def test_urlListSurvivesTheMove(self):
        self.writeLegacy()
        urls = YtModel.Model().getURLList()
        self.assertEqual(len(urls), 1)
        self.assertEqual(urls[0][1], "A Title")

    def test_screenGeometrySurvivesTheMove(self):
        """_assureConfig keys off SCREENX - a lost value would reset everything"""
        self.writeLegacy()
        model = YtModel.Model()
        self.assertEqual(model.getScreenX(), 1043)
        self.assertEqual(model.getScreenY(), 473)

    def test_existingNewIniIsNeverOverwritten(self):
        current = LEGACY.replace("/home/somebody/Videos/VD", "/the/current/one")
        self.writeCurrent(current)
        self.writeLegacy()
        model = YtModel.Model()
        self.assertEqual(model.getVideoPath(), "/the/current/one")
        self.assertTrue(os.path.exists(self.legacyPath), "legacy is left alone once migrated")

    def test_noLegacyFileIsNotAnError(self):
        model = YtModel.Model()
        self.assertEqual(model.getScreenX(), 760, "falls back to the defaults")

    def readCurrent(self):
        with open(self.currentPath, encoding="utf-8") as f:
            return f.read()

    def test_migrationRunsOnlyOnce(self):
        self.writeLegacy()
        YtModel.Model()
        first = self.readCurrent()
        YtModel.Model()
        self.assertEqual(self.readCurrent(), first)

    def test_unreadableLegacyDoesNotStopTheApp(self):
        """a lost ini is a nuisance, not a reason to refuse to start"""
        self.writeLegacy()
        with mock.patch.object(OSTools, 'moveFile', side_effect=OSError(13, "Permission denied")):
            model = YtModel.Model()
        self.assertEqual(model.getScreenX(), 760)

    def test_defaultsAreWrittenForAFreshConfig(self):
        model = YtModel.Model()
        self.assertEqual(model.getFormat(), YtModel.Model.FORMATS[0])
        self.assertEqual(model.getAudioFormat(), YtModel.Model.AUDIO_DEFAULT)
        self.assertEqual(json.loads(json.dumps(model.getURLList())), [])


if __name__ == '__main__':
    unittest.main()
