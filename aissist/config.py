from typing import Any, Type
import os
import sys

import dataclasses

from tomlkit import comment, document, table, nl, parse

@dataclasses.dataclass
class Parameter:

    type: Type
    value: Any
    comment: str = ""

    def __str__(self):
        return f"{self.name}={self.value}"
    
    def set(self, value):
        if not isinstance(value, self.type):
            raise TypeError(f"Expected {self.type}, got {type(value)}")
        self.value = value

class Config:

    def __init__(self):

        self.parameters: list[Parameter] = []
        self.config_file = os.path.join(os.path.expanduser("~"),
                  ".aissistrc")
        self.populate_default_parameters()

        # If the config file does not exist, write the
        # defaults there.
        if not os.path.exists(self.config_file):
            self.write_config()
        else:
            # The configuration file was already present, read form it and overwrite
            # any parameters
            self.read_config()


    def populate_default_parameters(self) -> None:

        self.parameters: dict[str, Parameter] = {
            "model": Parameter(
                str,
                "gpt-3.5-turbo",
                comment="The default OpenAI model name to use"),
            "temperature": Parameter(
              float,
              0.0,
              comment="A number in the range 0 to 1. Higher values lead to more unpredictable but creative outputs.")
        }


    def write_config(self) -> None:

        doc = document()
        doc.add(comment("Configuration file for aissist."))

        parameters = table()
        for name, param in self.parameters.items():
            parameters.add(nl())
            if len(param.comment) > 0:
                parameters.add(comment(param.comment))
            parameters.add(name, param.value)

        doc.add("parameters", parameters)

        with open(self.config_file, "w") as f:
            f.write(doc.as_string())


    def read_config(self) -> None:

        with open(self.config_file, "r") as f:
            doc = parse(f.read())

        config_parameters = doc["parameters"]

        for name, param in config_parameters.items():
            if name not in self.parameters:
                raise ValueError(f"Unknown parameter {name}. Allowed parameters are: {', '.join(self.parameters.keys())}")
            self.parameters[name].set(param)

    def get(self, parameter_name: str) -> Any:
        return self.parameters[parameter_name].value