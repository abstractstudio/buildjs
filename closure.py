"""A Python 3 wrapper for Google's Closure compiler."""

import colorama
import subprocess
import command


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

        self.arguments["js"].add(path)

    def execute(self):
        """Execute compilation."""

        print(self.executable, self.arguments.get())
        return

        popen = subprocess.Popen(
            self.arguments.get(),
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

        if "override" in target:
            if target["entry"] == "all":
                pass
            elif isinstance(target["entry"], str):
                compilation.source(target["entry"])
            elif isinstance(target["entry"], list):
                for path in target["entry"]:
                    compilation.source(path)
            else:
                raise ClosureError("Cannot parse override.")

        compilation.execute()

        # do all sources
        # add all other arguments


