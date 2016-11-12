"""A Python 3 wrapper for Google's Closure compiler."""

import colorama
import subprocess
import glob
import yaml
import os


ROOT = os.path.abspath(os.path.dirname(__file__))
CLOSURE_NAME = "closure.jar"
CLOSURE_PATH = os.path.join(ROOT, CLOSURE_NAME)


class ClosureBuild:
    """Wrapper class for the closure compiler."""

    def __init__(self, path):
        """Initialize a new closue build."""

        self.path = os.path.abspath(path)
        self.entry = None
        self.output = None
        self.source = set()
        self.ignore = set()
        self.options = []

    def __repr__(self):
        """Return a string representation of the build."""

        return "Build[{}=>{}]".format(self.entry, self.output)

    def set_target(self, entry, output):
        """Set the build target."""

        self.entry = entry
        self.output = output

    def add_source(self, path):
        """Add source files. Can be a glob."""

        if not os.path.isabs(path):
            path = os.path.abspath(os.path.join(self.path, path))
        for _ in glob.glob(path, recursive=True):
            self.source.add(_)

    def add_ignore(self, path):
        """Add ignore files. Can be a glob."""

        if not os.path.isabs(path):
            path = os.path.abspath(os.path.join(self.path, path))
        for _ in glob.glob(path, recursive=True):
            self.ignore.add(_)

    def add_option(self, name, value):
        """Add a custom option to be build."""

        self.options.append([name, value])

    def includes_file(self, path):
        """Check if a build includes a file."""

        return os.path.abspath(path) in self.source - self.ignore

    def arguments(self):
        """Execute the build command."""

        arguments = [self.path]
        arguments.extend(("--entry_point", self.entry))
        arguments.extend(("--js_output_file", self.output))
        for source in self.source - self.ignore:
            arguments.extend(("--js", source))
        for ignore in self.ignore:
            arguments.extend(("--js", "!" + ignore))
        for option in self.options:
            arguments.extend(option)
        return arguments

    def execute(self):
        """Execute the Closure compilation."""

        popen = subprocess.Popen(
            self.arguments(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        return popen.communicate()


class ClosureError(BaseException):
    """An error in the Closure compiler command."""


def closure(file, path="."):
    """Run compilations based on instructions."""

    with open(file) as f:
        instructions = yaml.load(f)

    for target in instructions["targets"]:

        build = ClosureBuild(path)
        build.set_target(target["entry"], target["output"])

        ignore = []
        if "override" not in target or target["override"] != "all":
            ignore = [target["entry"] for target in instructions["targets"]]
            ignore.remove(target["entry"])
            if "override" in target:
                for path in target["override"]:
                    if path in ignore:
                        ignore.remove(path)

        for source in instructions["source"]:
            build.add_source(source)
        for source in instructions["ignore"] + ignore:
            build.add_ignore(source)

        for argument in instructions["arguments"]:
            build.add_option(argument, instructions["arguments"][argument])

        yield build
