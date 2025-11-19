"""A reproducible nuitka build command."""

import os
import subprocess
import sys

cmd = [
    "entrypoint.py",
    "--onefile",
    "--plugin-enable=pyqt6",
    "--enable-plugin=anti-bloat",
    "--include-qt-plugins=all",
    "--include-data-dir=src/resources/=src/resources/",
    "--output-dir=dist",
]

if os.name == "nt":
    cmd += ["--windows-console-mode=disable"]

subprocess.call([sys.executable, "-m", "nuitka", *cmd])
