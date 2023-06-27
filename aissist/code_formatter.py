import shutil
import sys
import textwrap

from pygments import highlight
from pygments.formatters import TerminalTrueColorFormatter
from pygments.lexers import guess_lexer


class CodeFormatter:
    def __init__(self, config):
        self.config = config

    def bold_single_backticks(self, text):
        """Formats a given string by making text enclosed in single backticks bold,
        using ANSI escape codes.
        """
        in_backticks = False
        result = ""
        for indx, c in enumerate(text):
            if c == "`":
                if in_backticks:
                    result += "\033[0m"  # Reset text formatting
                    in_backticks = False
                else:
                    result += "\033[1m"  # Bold text
                    in_backticks = True
            else:
                result += c

        if in_backticks:
            result += "\033[0m"  # Reset text formatting

        return result

    def highlight_codeblocks(self, markdown, columns: int):
        """Highlights code blocks in a markdown string and prints them to the console
        using pygments library.
        """

        terminal_size = shutil.get_terminal_size()
        terminal_width = terminal_size.columns
        inside_block = False
        current_block = ""
        for line in markdown.split("\n"):
            if line.startswith("```"):
                if inside_block is True:
                    # We are exiting a block, print it
                    lexer = guess_lexer(current_block.rstrip("\n"))
                    formatted_code = highlight(
                        current_block,
                        lexer,
                        TerminalTrueColorFormatter(
                            style=self.config.get("color-scheme")
                        ),
                    )
                    print(formatted_code)
                else:
                    # We are entering a block
                    current_block = ""
                inside_block = not inside_block

            elif inside_block is True:
                current_block += line + "\n"
            else:
                line = self.bold_single_backticks(line)
                line = textwrap.fill(line, terminal_width - 1)
                print(line)
