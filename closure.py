"""A Python 3 wrapper for Google's Closure compiler."""

import subprocess
import glob
import fnmatch
import yaml
import os


ROOT = os.path.abspath(os.path.dirname(__file__))
CLOSURE_NAME = "closure.jar"
CLOSURE_PATH = os.path.join(ROOT, CLOSURE_NAME)


def matches_any(path, patterns):
    """Check if a path matches any patterns."""

    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def glob_all(paths):
    """Glob multiple paths together into a set."""

    total = set()
    for path in paths:
        path = path.replace("**", "**" + os.sep + "*")
        total = total | set(glob.glob(path, recursive=True))
    return total


class ClosureBuild:
    """Wrapper class for the closure compiler."""

    def __init__(self, path):
        """Initialize a new closure build."""

        self.path = os.path.abspath(path)
        self.entry_point = None
        self.output_path = None
        self.source_patterns = set()
        self.ignore_patterns = set()
        self.options = []

    def __repr__(self):
        """Return a string representation of the build."""

        return "Build[{}=>{}]".format(self.entry_point, self.output_path)

    @property
    def name(self):
        """Get the name of the build."""

        if self.entry_point:
            return os.path.basename(self.output_path).split(os.path.extsep)[0]
        return None

    def set_target(self, entry, output):
        """Set the build target."""

        self.entry_point = os.path.abspath(entry)
        self.output_path = os.path.abspath(output)

    def add_source_pattern(self, path):
        """Add source files. Can be a glob."""

        if not os.path.isabs(path):
            path = os.path.abspath(os.path.join(self.path, path))
        self.source_patterns.add(path)

    def add_ignore_pattern(self, path):
        """Add ignore files. Can be a glob."""

        if not os.path.isabs(path):
            path = os.path.abspath(os.path.join(self.path, path))
        self.ignore_patterns.add(path)

    def add_option(self, name, value):
        """Add a custom option to be build."""

        self.options.append([name, value])

    def includes_file(self, path):
        """Check if a build includes a file."""

        path = os.path.abspath(path)
        return (matches_any(path, self.source_patterns) and
                not matches_any(path, self.ignore_patterns))

    def arguments(self):
        """Execute the build command."""

        arguments = ["java", "-jar", CLOSURE_PATH]
        arguments.extend(("--entry_point", self.entry_point))
        arguments.extend(("--js_output_file", self.output_path))
        source_files = glob_all(self.source_patterns)
        ignore_files = glob_all(self.ignore_patterns)
        for source in source_files - ignore_files:
            arguments.extend(("--js", source))
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

    instructions["targets"] = instructions.get("targets", [])
    instructions["source"] = instructions.get("source", [])
    instructions["ignore"] = instructions.get("ignore", [])
    instructions["arguments"] = instructions.get("arguments", {})

    builds = []

    for target in (instructions["targets"]):

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
            build.add_source_pattern(source)
        for source in instructions.get("ignore", []) + ignore:
            build.add_ignore_pattern(source)

        for argument in instructions["arguments"]:
            build.add_option(argument, instructions["arguments"][argument])

        builds.append(build)

    return builds
