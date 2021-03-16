import json
import vulture
import subprocess
from typing import List, Dict, Any
from abc import ABC, abstractmethod
from . import StaticError, StaticAnalyzer, StaticTool


class VultureTool(StaticTool):
    """Vulture static analysis tool
    Vulture is a static analysis tool designed to detect dead code or code that is not executed
    when a script or function is run.
    """

    def __init__(self):
        super(VultureTool, self).__init__("vulture")

    def load_config(self, config: Dict[str, Any]) -> None:
        """Loads the specified ``configs`` for Vulture
        Configs:
            file_path (str): The relative path to the file to run vulture on. This must be a ".py" file
        Args:
            config (Dict[str, Any]): Configs for vulture, (see above)
        Raises:
            ValueError: If "file_path" config is not included in the config file
            ValueError: If "file_path" config is not a python file (".py" extension)
        """
        if not "file_path" in config:
            raise ValueError('Invalid config file. [file_type] not defined.')

        self.file_path = config["file_path"]

        if not '.py' in self.file_path:
            raise ValueError('Invalid file type provided. File must have the extension ".py"')

    def run(self) -> List[StaticError]:
        """Runs Vulture with the given configs set by `load_config`
        Returns:
            [StaticError]: a list of all dead code errors reported by Vulture
        """

        process = subprocess.Popen(
            "vulture " + self.file_path, shell=True, stdout=subprocess.PIPE
        )
        stdout, _ = process.communicate()

        # list of static errors reported by vulture
        error_lst = []
        
        # Vulture returns output string in this form:
        # folder/file.py:[line number]: unused [function, property, variable] '[name of said dead code type]' ([probability of false positive] confidence)
        # We parse the output string into parameters defined by StaticError        
        for output_encoded in stdout.splitlines():

            # decode the string output
            output = output_encoded.decode()

            # extracts line number from output string
            fp: str = (output.partition(":"))[0]
            output = (output.partition(":"))[2]
            # line number
            ln: int = int((output.partition(":"))[0])
            output = (output.partition(": "))[2]
            # error type
            error_type: str = (output.partition(" '"))[0]
            output = (output.partition(" '"))[2]
            # error type namet
            error_type_name: str = (output.partition("'"))[0]

            static_error: StaticError = StaticError(
                file_path=fp,
                line_no=ln,
                error_name=error_type,
                error_description=f"Error in '{error_type_name}'",
            )
            error_lst.append(static_error)

        return error_lst