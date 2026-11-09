"""Import paths for the test suite.

FFMPEGTools.py is deliberately not part of this project's src: VideoCut holds
the master and build/build.xml vendors it in at build time, so the two can
never drift apart. The tests inherit that requirement - VideoCut has to be
checked out next to this project, exactly as the build expects it.

    cd /home/matze/git/YoutubeDownloader && python3 -m unittest discover -s tests
"""
import os
import sys

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJECT, 'src')
#same relative location build.xml uses for ${ffmpegTools}
SHARED = os.path.join(os.path.dirname(PROJECT), 'VideoCut', 'src')


def setupPath():
    if not os.path.isfile(os.path.join(SHARED, 'FFMPEGTools.py')):
        raise RuntimeError(
            f"FFMPEGTools.py not found in {SHARED}\n"
            "The shared code lives in VideoCut, which has to be checked out "
            "next to this project (same parent directory).")
    for path in (SHARED, SRC):
        if path not in sys.path:
            sys.path.insert(0, path)
