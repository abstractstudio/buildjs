"""Command line wrapper library."""

import os


class Argument:
    """A basic container for any command line argument."""

    def __init__(self, name: str):
        """Initialize a new argument with its name."""

        self.prefix = name[:len(name) - len(name.lstrip("-"))]
        self.name = name.lstrip("--")


class ValueArgument(Argument):
    """A command line argument container class."""

    def __init__(self, name, value=None, multiple=False):
        """Initialize a new argument."""

        super().__init__(name)
        self.values = [] if value is None else [value]
        self.multiple = multiple
        self.assigned = value is not None
        self.set(value)

    def formatted(self):
        """Convert the argument to a string."""

        if self.values is None or self.values == [None]:
            return None
        if isinstance(self.values, list) and len(self.values) == 0:
            return None
        return [[self.prefix + self.name, value] for value in self.values]

    def set(self, value):
        """Set the value of the argument."""

        self.values = [value] if self.multiple else [value]
        self.assigned = True

    def add(self, value):
        """Add a value to the argument."""

        if self.multiple or len(self.values) == 0:
            self.values.append(value)
            self.assigned = True
            return
        raise SyntaxError("Single option cannot occur twice.")

    def remove(self, value=None):
        """Remove a value from the list."""

        if value is None and len(self.values) == 0:
            self.values.pop(0)
        self.values.remove(value)

    def get(self):
        """Get the value of the argument."""

        return self.values if self.multiple else self.values[0]


class OptionArgument(ValueArgument):
    """Command line argument that must be one of a set of options."""

    def __init__(self, name, options, value=None, multiple=False):
        """Initialize a new option argument with option list."""

        super().__init__(name, value, multiple)
        self.options = options

    def set(self, value):
        """Set the value of the argument."""

        if value not in self.options:
            raise TypeError(format("Option {} must be in {}.",
                                   self.name, ", ".join(self.values)))
        super().set(value)


class FlagArgument(Argument):
    """Argument that doesn't have a value."""

    def __init__(self, name):
        """Initialize a new flag argument."""

        super().__init__(name)
        self.enabled = False
        self.assigned = False

    def formatted(self):
        """Convert the argument to a string."""

        return [self.prefix + "%s" % self.name] if self.enabled and self.assigned else None

    def set(self, enabled=True):
        """Set whether the flag is enabled."""

        self.enabled = enabled
        self.assigned = True

    def get(self):
        """Get if the flag is enabled."""

        return self.enabled


class Arguments:
    """Argument manager for the compilation call."""

    def __init__(self):
        """Initialize a new arguments manager."""

        self.arguments = {}

    def __getitem__(self, item):
        """Return a argument by its name."""

        return self.arguments[item]

    def add(self, argument):
        """Override mutating addition"""

        if not isinstance(argument, Argument):
            raise TypeError("Object must be argument.")
        self.arguments[argument.name] = argument

    def get(self):
        """Get the argument list."""

        everything = filter(None, map(lambda x: x.formatted(), self.arguments.values()))
        return sum(sum(everything, []), [])


class Command:
    """Command line wrapper."""

    def __init__(self, executable):
        """Initialize a new command line wrapper."""

        self.executable = os.path.abspath(executable)
        self.arguments = Arguments()
        doc = str(type(self).__doc__)
        for line in doc.split("\n"):
            line = line.strip()
            if line.startswith("-"):
                command, kind, *rest = line.split()
                if kind == "flag":
                    argument = FlagArgument(command)
                elif kind == "value":
                    argument = ValueArgument(command)
                elif kind == "multiple":
                    argument = ValueArgument(command, multiple=True)
                elif kind == "option":
                    argument = OptionArgument(command, rest)
                else:
                    raise TypeError(format("Invalid command type '{}'", kind))
                self.arguments.add(argument)
