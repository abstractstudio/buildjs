"""A lightweight Javascript build service.

BuildJS is the all-in-one Javascript build service. BuildJS uses the
latest version of Google's Closure compiler to compile your javascript
files every time a file in the target directory has been modified.
"""

import os
import sys
import colorama
import re
import zipfile
import urllib.request
import watchdog.events
import closure


colorama.init()

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT)

CLOSURE_URL = "https://dl.google.com/closure-compiler/compiler-latest.zip"
CLOSURE_PATTERN = r"closure-compiler-v.+\.jar"
CLOSURE_ZIP = os.path.join(ROOT, "closure.zip")
CLOSURE_JAR = os.path.join(ROOT, "closure.jar")
BUILD_CONFIG = os.path.join(os.path.dirname(ROOT), "closure.cfg")

CLOSURE_OPTIONS = """\
targets:
source:
ignore:
arguments:
"""


def download_closure():
    """Download the latest version of the Closure compiler."""

    # Download the zip file
    source = urllib.request.urlopen(CLOSURE_URL)
    with open(CLOSURE_ZIP, "wb") as file:
        file.write(source.read())
    source.close()
    compressed = zipfile.ZipFile(CLOSURE_ZIP)

    # Guess which is the right file
    for name in compressed.namelist():
        if re.match(CLOSURE_PATTERN, name):
            target = name
            break
    else:
        print(colorama.Fore.RED + "Could not locate Closure jar." + colorama.Fore.RESET)
        return
        
    # Extract and delete the zip file
    compressed.extract(name, ".")
    compressed.close()
    os.remove(CLOSURE_ZIP)

    # Rename the compiler
    if os.path.isfile(CLOSURE_JAR):
        os.remove(CLOSURE_JAR)
    os.rename(target, CLOSURE_JAR)


def check_closure():
    """Check if the compiler is downloaded."""

    if not os.path.isfile(CLOSURE_JAR):
        print(colorama.Fore.GREEN + "Downloading closure..." + colorama.Fore.RESET)
        download_closure()
    return 0


def write_configuration():
    """Create the custom configuration."""

    with open(BUILD_CONFIG, "w") as file:
        file.write(CLOSURE_OPTIONS)


def check_configuration():
    """Check if the configuration is created."""

    if not os.path.isfile(BUILD_CONFIG):
        print("Creating config file...")
        print(colorama.Fore.RED + "No configuration!" + colorama.Fore.RESET)
        write_configuration()
        return 1


def load_configuration():
    """Load the command line arguments."""

    builds = closure.closure(BUILD_CONFIG)
    if len(builds) == 0:
        print(colorama.Fore.RED + "No build targets specified." + colorama.Fore.RESET)
    return builds


class BuildHandler(watchdog.events.FileSystemEventHandler):
    """An automatic build tool that monitors the file system."""

    def __init__(self):
        """Initialize the build handler."""

        super().__init__()
        self.builds = load_configuration()

    def on_any_event(self, event: watchdog.events.FileSystemMovedEvent):
        for build in self.builds:
            if build.includes_file(event.src_path):
                print("Rebuilding " + build.output_path)


def main():
    """Loop recompilation or configuration as needed."""

    pass


if __name__ == "__main__":
    main()
