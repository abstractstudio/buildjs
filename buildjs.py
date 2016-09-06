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
import configparser
import shlex
import zipfile
import urllib.request

ROOT = os.path.dirname(__file__)
CLOSURE_URL = "https://dl.google.com/closure-compiler/compiler-latest.zip"
CLOSURE_PATTERN = r"closure-compiler-v.+\.jar"
CLOSURE_ZIP = os.path.join(ROOT, "closure.zip")
CLOSURE_JAR = os.path.join(ROOT, "closure.jar")
CLOSURE_CFG = os.path.join(ROOT, "closure.cfg")
CLOSURE_ARGS = ["java", "-jar", CLOSURE_JAR]

CLOSURE_OPTIONS = """\
# BuildJS configuration
[compiler]

# Filesystem checking target directory
# Add multiple by using tabbed newlines
target: 

# Filesystem refresh time in seconds
refresh: 

# Command line arguments
arguments:
"""

options = {
    "arguments": CLOSURE_ARGS.copy(),
    "target": "",
    "refresh": 1,
}


def lines(string):
    """Crossplatform split lines."""

    return re.split(r"\r\n?|\n", string)


def download():
    """Download the latest version of the Closure compiler."""

    # Download the zip file
    source = urllib.request.urlopen(CLOSURE_URL)
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
    

def configuration():
    """Create the custom configuration."""

    with open("closure.cfg", "w") as file:
        file.write(CLOSURE_OPTIONS)


def reconfigure():
    """Load the command line arguments."""

    global options
    options["arguments"].clear()
    options["arguments"].extend(CLOSURE_ARGS)
    
    if not os.path.isfile(CLOSURE_CFG):
        configuration()
        return
    with open(CLOSURE_CFG) as file:
        config = configparser.ConfigParser()
        config.read_file(file)

        if not "compiler" in config:
            print("No compiler section in config!", sys.stderr)
            return
        
        options["target"] = config["compiler"].get("target", "")
        options["refresh"] = max(config["compiler"].getint("refresh", 1), 0.5)
        options["arguments"].extend(shlex.split(
            config["compiler"].get("arguments", "")))
    
        
def compiler():
    """Run the closure compiler."""

    global options
    popen = subprocess.Popen(
        options["arguments"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    out = popen.communicate()

    print("Recompiled at " + time.strftime("%H:%M:%S %p"))
    # Print output
    if out is not None:
        if out[0]: print(o[0].decode())
        if out[1]: print(o[1].decode() + "\n", file=sys.stderr)
        if out[0] or out[1]: print()


def search(lookup, path):
    """Update all edit times."""

    if os.path.isfile(path):
        lookup[path] = os.path.getmtime(path)
        return lookup
    for p in filter(lambda x: not x.startswith("."), os.listdir(path)):
        p = os.path.join(path, p)
        search(lookup, p)
    return lookup


def main():
    """Loop recompilation or configuration as needed."""

    global options

    if not os.path.isfile(CLOSURE_JAR):
        print("Downloading closure...")
        download()
    if not os.path.isfile(CLOSURE_CFG):
        print("Creating config file...")
        print("No configuration!", file=sys.stderr)
        configuration()
        return 

    reconfigure()

    if options["target"] == "":
        print("No target directory.", sys.stderr)
        print("Compiling once...")
        recompile()

    if "--js" not in options["arguments"]:
        print("No Javascript files specified!\n", sys.stderr)
        return
    elif "--js_output_file" not in options["arguments"]:
        print("No Javascript output file specified!\n", sys.stderr)
        return

    old = {}
    cfg = os.path.getmtime(CLOSURE_CFG)
    
    while True:
        try:

            # Check if configuration changed
            c = os.path.getmtime(CLOSURE_CFG) > cfg
            if c > cfg:
                reconfigure()
                print("Reconfigured the compiler!")

            # Search for new or edited files
            new = {}
            for path in lines(options["target"]):
                search(new, path)

            # Recompile if new or edited files
            o = None
            if len(new) != len(old):
                o = compiler()
            else:
                for p in new:
                    if p not in old or new[p] > old[p]:
                        o = compiler()
                        break

            old = new
            time.sleep(options["refresh"])

        except KeyboardInterrupt:
            return


if __name__ == "__main__":
    main()
