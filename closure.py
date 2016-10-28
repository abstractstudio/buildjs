"""A Python 3 wrapper for Google's Closure compiler."""

import colorama
import subprocess


class Argument:
    """A command line argument container class."""

    def __init__(self, name, value=None):
        """Initialize a new argument."""

        self.name = name
        self.value = None
        self.set(value)

    def __str__(self):
        """Convert the argument to a string."""

        return "--%s %s" % (self.name, self.value)

    def set(self, value):
        """Set the value of the argument."""

        self.value = value

    def get(self):
        """Get the value of the argument."""

        return self.value


class Arguments:
    """Argument manager for the compilation call."""

    def __init__(self):
        """Initialize a new arguments manager."""

        self._ = []

    def __iadd__(self, argument):
        """Override mutating addition"""

        if not isinstance(argument, Argument):
            raise TypeError("Object must be argument.")
        self._.append(argument)

    def get(self):
        """Get the argument list."""

        return self._


class Compilation:
    """A wrapper for a call to the compiler."""

    def __init__(self):
        """Initialize a new Closure compilation."""

        self.arguments = Arguments()

    def argument(self, name, value):
        """Add an argument to the compilation."""

        self.arguments += Argument(name, value)

    def target(self, entry, output):
        """Set the target for the compilation."""

        self.arguments += Argument("entry_point", entry)
        self.arguments += Argument("js_output_file", output)

    def source(self, path):
        """Add a source to the compiler."""

        self.arguments += Argument("js", path)

    def ignore(self, path):
        """Ignore a source during compilation."""

        self.arguments += Argument("js", "!" + path)

    def execute(self):
        """Execute compilation."""

        popen = subprocess.Popen(
            self.arguments.get(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        return popen.communicate()


class ClosureArgumentError(BaseException):
    """Raised when there is an issue in the configuration."""


def compiler(instructions):
    """Run compilations based on instructions."""

    for target in instructions["targets"]:
        compilation = Compilation()

        if not ("entry" in target and "output" in target):
            raise ClosureArgumentError("Target must define an entry and output file.")
        if not (isinstance(target["entry"], str) and isinstance(target["output"], str)):
            raise ClosureArgumentError("Entry and output must be strings.")
        compilation.target(target["entry"], target["output"])

        if "override" in target:
            if target["entry"] == "all":
                pass
            elif isinstance(target["entry"], str):
                compilation.source(target["entry"])
            elif isinstance(target["entry"], list):
                for path in target["entry"]:
                    compilation.source(path)
            else:
                raise ClosureArgumentError("Cannot parse override.")

        # do all sources
        # add all other arguments


