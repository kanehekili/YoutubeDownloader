"""The OSTools helpers this project added to the shared FFMPEGTools block.

src/FFMPEGTools.py is a verbatim copy of VideoCut's, which is the canonical
version. Two helpers were added there for this app and carried over to
EasyPlayer, so they are covered here as well as in VideoCut:

  moveFile  - the config migration needs a move; os.replace alone would fail
              across filesystems
  findFiles - the GUI looks a download up again by part of its title, which
              collectFiles (extension based) cannot do

ConfigAccessor's folder creation is tested too: without it store() raises
IOError and loses the settings whenever ~/.config/<AppName> is not there yet,
which is every fresh install run from the sources.

    cd /home/matze/git/YoutubeDownloader && python3 -m unittest discover -s tests
"""
import os
import tempfile
import unittest
from unittest import mock

import support

support.setupPath()

from FFMPEGTools import ConfigAccessor, OSTools  # noqa: E402


class SingletonTest(unittest.TestCase):
    """OSTools is a singleton in VideoCut and must stay one here"""

    def test_oneInstanceOnly(self):
        self.assertIs(OSTools(), OSTools())

    def test_joinPathes(self):
        self.assertEqual(OSTools().joinPathes("/a", "b", "c.log"), "/a/b/c.log")

    def test_ensureDirectoryCreatesNestedPath(self):
        target = os.path.join(tempfile.mkdtemp(), "deep", "deeper")
        OSTools().ensureDirectory(target)
        self.assertTrue(os.path.isdir(target))

    def test_ensureDirectoryAcceptsAnExistingPath(self):
        target = tempfile.mkdtemp()
        OSTools().ensureDirectory(target)
        self.assertTrue(os.path.isdir(target))


class MoveFileTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def write(self, name, content="x=1"):
        path = os.path.join(self.tmp, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def read(self, path):
        with open(path, encoding="utf-8") as f:
            return f.read()

    def test_moveKeepsTheContentAndDropsTheSource(self):
        src = self.write("old.ini")
        dest = os.path.join(self.tmp, "new.ini")
        OSTools().moveFile(src, dest)
        self.assertFalse(os.path.exists(src))
        self.assertEqual(self.read(dest), "x=1")

    def test_moveOverwritesTheTarget(self):
        src = self.write("old.ini", "new content")
        dest = self.write("new.ini", "stale content")
        OSTools().moveFile(src, dest)
        self.assertEqual(self.read(dest), "new content")

    def test_crossDeviceFallsBackToCopyAndDelete(self):
        """os.replace raises EXDEV across mounts - shutil.move must take over"""
        src = self.write("old.ini")
        dest = os.path.join(self.tmp, "new.ini")
        with mock.patch("FFMPEGTools.os.replace", side_effect=OSError(18, "Invalid cross-device link")):
            OSTools().moveFile(src, dest)
        self.assertFalse(os.path.exists(src))
        self.assertEqual(self.read(dest), "x=1")

    def test_missingSourceStillRaises(self):
        with self.assertRaises(OSError):
            OSTools().moveFile(os.path.join(self.tmp, "nope.ini"),
                               os.path.join(self.tmp, "new.ini"))


class FindFilesTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def touch(self, *parts):
        path = os.path.join(self.tmp, *parts)
        OSTools().ensureDirectory(os.path.dirname(path))
        with open(path, "w", encoding="utf-8") as f:
            f.write("")
        return path

    def names(self, fragment):
        return [os.path.basename(p) for p in OSTools().findFiles(self.tmp, fragment)]

    def test_findsEveryMatchingFragment(self):
        self.touch("Big Buck Bunny.mp4")
        self.touch("Big Buck Bunny.f401.mp4")
        self.touch("Something Else.mp4")
        self.assertEqual(self.names("Big Buck Bunny"),
                         ["Big Buck Bunny.f401.mp4", "Big Buck Bunny.mp4"])

    def test_descendsIntoSubfolders(self):
        self.touch("sub", "deeper", "My Title.mp4")
        self.assertEqual(self.names("My Title"), ["My Title.mp4"])

    def test_hiddenFoldersAreSkipped(self):
        self.touch(".trash", "My Title.mp4")
        self.assertEqual(self.names("My Title"), [])

    def test_noMatchGivesAnEmptyList(self):
        self.touch("whatever.mp4")
        self.assertEqual(self.names("absent"), [])

    def test_resultIsCapped(self):
        for i in range(10):
            self.touch(f"Clip {i}.mp4")
        self.assertEqual(len(OSTools().findFiles(self.tmp, "Clip", maxFiles=4)), 4)

    def test_numbersSortNaturally(self):
        """a file manager puts Clip 9 before Clip 10, strcmp does not"""
        for i in (1, 2, 9, 10, 20):
            self.touch(f"Clip {i}.mp4")
        self.assertEqual(self.names("Clip"),
                         ["Clip 1.mp4", "Clip 2.mp4", "Clip 9.mp4", "Clip 10.mp4", "Clip 20.mp4"])


class ConfigAccessorTest(unittest.TestCase):
    """the ini goes into ~/.config/<folder>/, beside the log"""

    def setUp(self):
        self.home = tempfile.mkdtemp()
        patcher = mock.patch.object(ConfigAccessor, 'homeDir', self.home)
        patcher.start()
        self.addCleanup(patcher.stop)

    def path(self, *parts):
        return os.path.join(self.home, ".config", *parts)

    def test_folderIsCreatedUpFront(self):
        """without this store() raises IOError and silently loses everything"""
        ConfigAccessor("MyApp", "my.ini", "DATA")
        self.assertTrue(os.path.isdir(self.path("MyApp")))

    def test_storeAndReadRoundTrip(self):
        cfg = ConfigAccessor("MyApp", "my.ini", "DATA")
        cfg.set("DEST_VIDEO", "/home/somebody/Videos")
        self.assertTrue(cfg.store(), "store() must succeed on a fresh install")
        again = ConfigAccessor("MyApp", "my.ini", "DATA")
        again.read()
        self.assertEqual(again.get("DEST_VIDEO"), "/home/somebody/Videos")

    def test_fileLandsInsideTheAppFolder(self):
        cfg = ConfigAccessor("MyApp", "my.ini", "DATA")
        cfg.set("k", "v")
        cfg.store()
        self.assertTrue(os.path.isfile(self.path("MyApp", "my.ini")))

    def test_missingKeysReturnTheDefault(self):
        cfg = ConfigAccessor("MyApp", "my.ini", "DATA")
        self.assertIsNone(cfg.get("ABSENT"))
        self.assertEqual(cfg.get("ABSENT", "fallback"), "fallback")
        self.assertIsNone(cfg.getInt("ABSENT"))


if __name__ == '__main__':
    unittest.main()
