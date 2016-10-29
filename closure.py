"""A Python 3 wrapper for Google's Closure compiler."""

import colorama
import subprocess
import command
import yaml


class Closure(command.Command):
    """A wrapper for a call to the Closure compiler.

    --compilation_level                 value
    --env                               value
    --externs                           value
    --js                                multiple
    --js_output_file                    value
    --language_in                       value
    --language_out                      value
    --warning_level                     value
    --conformance_configs               value
    --extra_annotation_name             value
    --hide_warnings_for                 multiple
    --jscomp_error                      multiple
    --jscomp_off                        multiple
    --jscomp_warning                    multiple
    --new_type_inf                      flag
    --warnings_whitelist_file           value
    --assume_function_wrapper           flag
    --export_local_property_definitions flag
    --formatting                        value
    --generate_exports                  flag
    --output_wrapper                    value
    --output_wrapper_file               value
    --dependency_mode                   value
    --entry_point                       value
    --js_module_root                    value
    --process_common_js_modules         flag
    --transform_amd_modules             flag
    --angular_pass                      flag
    --dart_pass                         flag
    --polymer_pass                      flag
    --process_closure_primitives        flag
    --rewrite_polyfills                 flag
    --module                            multiple
    --module_output_path_prefix         multiple
    --module_wrapper                    value
    --create_source_map                 value
    --output_manifest                   value
    --output_module_dependencies        value
    --property_renaming_report          value
    --source_map_location_mapping       value
    --variable_renaming_report          value
    --charset                           value
    --checks_only                       flag
    --define                            multiple
    --third_party                       flag
    --use_types_for_optimization        flag
    """

    def __init__(self):
        """Initialize a new Closure compilation."""

        super().__init__("closure.jar")

    def __getitem__(self, item):
        """Get an argument from the argument list."""

        return self.arguments[item]

    def argument(self, name, value):
        """Add an argument to the compilation."""

        if name not in self.arguments:
            raise TypeError(format("Invalid option '{}'", name))
        self.arguments[name].set(value)

    def target(self, entry, output):
        """Set the target for the compilation."""

        self.arguments["entry_point"].set(entry)
        self.arguments["js_output_file"].set(output)

    def source(self, path):
        """Add a source to the compiler."""

        self.arguments["js"].add(path)

    def ignore(self, path):
        """Ignore a source during compilation."""

        self.arguments["js"].add("!" + path)

    def execute(self):
        """Execute compilation."""

        print([self.executable] + self.arguments.get())
        return
        popen = subprocess.Popen(
            None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        return popen.communicate()


class ClosureError(BaseException):
    """An error in the Closure compiler command."""


def closure(instructions):
    """Run compilations based on instructions."""

    for target in instructions["targets"]:
        compilation = Closure()

        if not ("entry" in target and "output" in target):
            raise ClosureError("Target must define an entry and output file.")
        if not (isinstance(target["entry"], str) and isinstance(target["output"], str)):
            raise ClosureError("Entry and output must be strings.")
        compilation.target(target["entry"], target["output"])

        ignore = [target["entry"] for target in instructions["targets"]]
        ignore.remove(target["entry"])
        if "override" in target:
            if target["override"] == "all":
                ignore.clear()
            elif isinstance(target["override"], list):
                for path in target["override"]:
                    if path in ignore:
                        ignore.remove(path)
                    else:
                        raise ClosureError("Override is only for including other targets.")
            else:
                raise ClosureError("Cannot parse override, must be list.")

        print(instructions["source"])
        for source in instructions["source"]:
            compilation.source(source)
        for source in instructions["ignore"] + ignore:
            compilation.ignore(source)

        arguments = {k: v for d in instructions["arguments"] for k, v in d.items()}
        for argument in arguments:
            compilation.argument(argument, arguments[argument])

        compilation.execute()

        # do all sources
        # add all other arguments


def build(file):
    """Build directly from a file."""

    with open(file) as f:
        instructions = yaml.load(f)
    closure(instructions)
