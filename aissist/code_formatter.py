import shutil
import textwrap

from pygments import highlight

# I do not understand this, but pylint (2.17.4) raises
# aissist/code_formatter.py:5:0: E0611: No name 'TerminalTrueColorFormatter' in module 'pygments.formatters' (no-name-in-module)
# Nevertheless, the code works fine so I am ignoring it.
from pygments.formatters import TerminalTrueColorFormatter  # pylint: disable=E0611
from pygments.lexers import guess_lexer


class CodeFormatter:
    def __init__(self, color_scheme: str) -> None:
        self.color_scheme = color_scheme

    def bold_single_backticks(self, text: str) -> str:
        """Formats a given string by making text enclosed in single backticks bold,
        using ANSI escape codes.
        """
        in_backticks = False
        result = ""
        for c in text:
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

    def highlight_codeblocks(self, markdown: str) -> None:
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
                        TerminalTrueColorFormatter(style=self.color_scheme),
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
