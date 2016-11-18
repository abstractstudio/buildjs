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
import watchdog.observers
import time
import closure


colorama.init()

ROOT = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.abspath(os.getcwd())
sys.path.append(ROOT)

CLOSURE_URL = "https://dl.google.com/closure-compiler/compiler-latest.zip"
CLOSURE_PATTERN = r"closure-compiler-v.+\.jar"
CLOSURE_ZIP = os.path.join(ROOT, "closure.zip")
CLOSURE_JAR = os.path.join(ROOT, "closure.jar")
DEFAULT_CONFIG = os.path.join(ROOT, "default.yaml")
BUILD_CONFIG = os.path.join(TARGET, "closure.yaml")


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


def write_configuration():
    """Create the custom configuration."""

    with open(BUILD_CONFIG, "w") as write:
        with open(DEFAULT_CONFIG) as read:
            write.write(read.read())


def check_configuration():
    """Check if the configuration is created."""

    if not os.path.isfile(BUILD_CONFIG):
        print("Creating config file...")
        print(colorama.Fore.RED + "No configuration!" + colorama.Fore.RESET)
        write_configuration()


def load_configuration():
    """Load the command line arguments."""

    builds = closure.closure(BUILD_CONFIG)
    if len(builds) == 0:
        print(colorama.Fore.RED + "No build targets specified." + colorama.Fore.RESET)
    return builds


def common_path(paths):
    """Get the common path among a list of paths."""

    path = os.path.abspath(os.path.commonpath(paths))
    parts = path.split(os.sep)[1:]
    for i in range(len(parts)):
        if "*" in parts[i]:
            return "/" + os.path.join(*parts[:i])
    return "/" + path


def execute_and_print(build):
    """Run a build and print the results."""

    name = os.path.split(build.output_path)[1]
    print("Building {}...".format(name))
    result = build.execute()
    if result[0]:
        print(colorama.Fore.GREEN + result[0].decode() + colorama.Fore.RESET)
    if result[1]:
        print(colorama.Fore.RED + result[1].decode() + colorama.Fore.RESET)
    print("Done at {}!\n".format(time.strftime("%H:%M:%S %p")))


class BuildHandler(watchdog.events.FileSystemEventHandler):
    """An automatic build tool that monitors the file system."""

    def __init__(self, build: closure.ClosureBuild):
        """Initialize the build handler."""

        super().__init__()
        self.build = build
        self.cache = {}

    def on_any_event(self, event: watchdog.events.FileSystemMovedEvent):
        """Called when a file in the system is modified."""

        path = os.path.realpath(event.src_path)

        if not self.build.includes_file(path):
            return

        modify_time = os.stat(path).st_mtime
        if path not in self.cache:
            self.cache[path] = modify_time
        elif modify_time == self.cache[path]:
            print("Already updated.")
            return

        print("Detected modified file:")
        print(colorama.Fore.GREEN + os.path.abspath(path) + colorama.Fore.RESET)
        execute_and_print(self.build)


def main():
    """Loop recompilation or configuration as needed."""

    check_closure()
    check_configuration()

    handles = []
    observer = watchdog.observers.Observer()
    builds = load_configuration()
    for build in builds:
        execute_and_print(build)
        handler = BuildHandler(build)
        path = common_path(list(build.source_patterns))
        handles.append(observer.schedule(handler, path, recursive=True))
    observer.start()
    print("Waiting for changes...\n")

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            break


if __name__ == "__main__":
    print()
    main()
