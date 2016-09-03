"""A lightweight Javascript build service.

BuildJS is the all-in-one Javascript build service. BuildJS uses the
latest version of Google's Closure compiler to compile your javascript
files every time a file in the target directory has been modified.
"""

import os
import sys
import time
import re
import subprocess
import zipfile
import urllib2
import tempfile

CLOSURE_URL = "https://dl.google.com/closure-compiler/compiler-latest.zip"
CLOSURE_ZIP = "closure.zip"
CLOSURE_PATTERN = r"closure-compiler-v.+\.jar"
CLOSURE_JAR = "closure.jar"


def download_closure():
    """Download the latest version of the Closure compiler."""

    # Download the zip file
    source = urllib2.urlopen(CLOSURE_URL)
    with open(CLOSURE_ZIP, "wb") as download:
        download.write(source.read())
    source.close()
    compressed = zipfile.ZipFile(CLOSURE_ZIP)

    # Guess which is the right file
    target = ""
    for name in compressed.namelist():
        if re.match(CLOSURE_PATTERN, name):
            target = name
            break
    else:
        sys.stderr.write("Could not locate Closure jar.\n")
        return

    # Extract and delete the zip file
    compressed.extract(name, ".")
    compressed.close()
    os.remove(CLOSURE_ZIP)

    # Rename the compiler
    if os.path.isfile(CLOSURE_JAR):
        os.remove(CLOSURE_JAR)
    os.rename(target, CLOSURE_JAR)
    

def create_configuration():
    """Create the custom configuration."""

    pass
