"""Configuation class for aissist."""

import argparse
import dataclasses
import os
from typing import Any, Type, TypeVar, cast

from tomlkit import comment, document, nl, parse, table

from .code_formatter import CodeFormatter
from .prompts import DEFAULT_PROMPTS

T = TypeVar("T")


@dataclasses.dataclass
class Parameter:
    type: Type
    value: Any
    comment: str = ""

    def __str__(self) -> str:
        return f"{self.value}"

    def set(self, value: T) -> None:
        if not isinstance(value, self.type):
            raise TypeError(f"Expected {self.type}, got {type(value)}")
        self.value = value


class Config:
    # The parameters known to AIssist.
    default_parameters: dict[str, Parameter] = {
        "model": Parameter(
            str, "gpt-3.5-turbo", comment="The default OpenAI model name to use"
        ),
        "prompt": Parameter(
            str,
            "code",
            comment="The default prompt to use. See the prompts.py file for a list of available prompts.",
        ),
        "no-stream": Parameter(
            bool, True, comment="Don't stream the output from the API."
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
        "max_tokens": Parameter(
            int,
            1000,
            comment="The maximum number of tokens to generate. Requests can use up to the model maximum tokens shared between prompt and response.",
        ),
    }

    def __init__(self) -> None:
        self.prompts: dict[str, str] = {}

        self.config_file = os.path.join(os.path.expanduser("~"), ".aissistrc")

        # Load the default parameters into self.parameters
        self.parameters: dict[str, Parameter] = self.default_parameters.copy()

        # If the config file does not exist, write the
        # defaults there.
        if not os.path.exists(self.config_file):
            self.write_config()
        else:
            # The configuration file was already present, read from it and overwrite
            # any parameters
            self.read_config()

        # Finally, if there are any command line parameters, overwrite the config
        # with them.
        self.add_command_line_args()

    @property
    def code_formatter(self) -> CodeFormatter:
        return CodeFormatter(self.parameters["color-scheme"].value)

    @property
    def prompt(self) -> str:
        prompt = self.parameters["prompt"].value
        return self.prompts[prompt]

    def add_command_line_args(self) -> None:
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        for name, param in self.default_parameters.items():
            if param.type == bool:
                # For a bool we need to add a store true and store false
                parser.add_argument(
                    f"--{name}",
                    action="store_true",
                    default=False,
                    help=param.comment,
                )
            else:
                parser.add_argument(
                    f"--{name}",
                    type=param.type,
                    default=param.value,
                    metavar=f"<{name}>",
                    help=param.comment,
                )
        args = parser.parse_args()

        for name, param in self.parameters.items():
            param.set(getattr(args, name.replace("-", "_")))

    def write_config(self) -> None:
        """Write the default configuration to the config file."""

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

        with open(self.config_file, "w", encoding="utf-8") as f:
            f.write(doc.as_string())

    def read_config(self) -> None:
        """Read the configuration from the config file."""

        with open(self.config_file, "r", encoding="utf-8") as f:
            doc = parse(f.read())

        for name, param in cast(dict, doc["parameters"]).items():
            if name not in self.parameters:
                raise ValueError(
                    f"Unknown parameter {name}. Allowed parameters are: {', '.join(self.parameters.keys())}"
                )
            self.parameters[name].set(param)

        for name, prompt in cast(dict, doc["prompts"]).items():
            self.prompts[name] = prompt

    def get(self, parameter_name: str) -> Any:
        return self.parameters[parameter_name].value
