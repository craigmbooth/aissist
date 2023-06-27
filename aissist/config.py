import argparse
import dataclasses
import os
from typing import Any, Type

from tomlkit import comment, document, nl, parse, table

from .prompts import DEFAULT_PROMPTS


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
    default_parameters: "dict[str, Parameter]" = {
        "model": Parameter(
            str, "gpt-3.5-turbo", comment="The default OpenAI model name to use"
        ),
        "prompt": Parameter(
            str,
            "code",
            comment="The default prompt to use. See the prompts.py file for a list of available prompts.",
        ),
        "color-scheme": Parameter(
            str,
            "paraiso-dark",
            comment="The default color scheme to use for code highlighting. See the pygments documentation for a list of available color schemes.",
        ),
        "temperature": Parameter(
            float,
            0.0,
            comment="A number in the range 0 to 1. Higher values lead to more unpredictable but creative outputs.",
        ),
    }

    def __init__(self):
        self.parameters: list[Parameter] = []
        self.prompts: dict[str, str] = {}

        self.config_file = os.path.join(os.path.expanduser("~"), ".aissistrc")

        self.populate_default_parameters()

        # If the config file does not exist, write the
        # defaults there.
        if not os.path.exists(self.config_file):
            self.write_config()
        else:
            # The configuration file was already present, read from it and overwrite
            # any parameters
            self.read_config()

        self.add_command_line_args()

    def get_prompt(self) -> str:
        prompt = self.parameters["prompt"].value
        return self.prompts[prompt]

    def add_command_line_args(self) -> None:
        parser = argparse.ArgumentParser()
        for name, param in self.default_parameters.items():
            parser.add_argument(
                f"--{name}", type=param.type, default=param.value, help=param.comment
            )
        args = parser.parse_args()

        for name, param in self.parameters.items():
            param.set(getattr(args, name.replace("-", "_")))

    def populate_default_parameters(self) -> None:
        self.parameters = self.default_parameters.copy()

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

        prompts = table()

        for prompt, (prompt_description, prompt_str) in DEFAULT_PROMPTS.items():
            prompts.add(nl())
            prompts.add(comment(prompt_description))
            prompts.add(prompt, prompt_str)
            self.prompts[prompt] = prompt_str

        doc.add("prompts", prompts)

        with open(self.config_file, "w") as f:
            f.write(doc.as_string())

    def read_config(self) -> None:
        with open(self.config_file, "r") as f:
            doc = parse(f.read())

        for name, param in doc["parameters"].items():
            if name not in self.parameters:
                raise ValueError(
                    f"Unknown parameter {name}. Allowed parameters are: {', '.join(self.parameters.keys())}"
                )
            self.parameters[name].set(param)

        for name, prompt in doc["prompts"].items():
            self.prompts[name] = prompt

    def get(self, parameter_name: str) -> Any:
        return self.parameters[parameter_name].value
