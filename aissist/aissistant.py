import os
import sys

import openai
from prompt_toolkit import PromptSession
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import guess_lexer

from .config import Config
from .spinner import Spinner
from .version import __version__

try:
    openai.api_key = os.environ["OPENAI_API_KEY"]
except KeyError:
    print("Please put your API key in the OPENAI_API_KEY environment variable.")
    sys.exit(1)

prompt = """You are a helpful but succinct chatbot that assists an impatient programmer by directly answering questions. You understand that the programmer is advanced enough to understand succinct phrases and prefers direct answers with little boilerplate.
"""

session = PromptSession()


def prompt_continuation(width: int, line_number, is_soft_wrap):
    return "." * (width - 1) + " "


def bold_single_backticks(text):
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


def highlight_codeblocks(markdown, columns: int):
    """Highlights code blocks in a markdown string and prints them to the console
    using pygments library.
    """

    inside_block = False
    current_block = ""
    for line in markdown.split("\n"):
        if line.startswith("```"):
            if inside_block is True:
                # We are exiting a block, print it
                lexer = guess_lexer(current_block)
                formatted_code = highlight(current_block, lexer, TerminalFormatter())
                print(formatted_code)
            else:
                # We are entering a block
                current_block = ""
            inside_block = not inside_block

        elif inside_block is True:
            current_block += line + "\n"
        else:
            line = bold_single_backticks(line)
            sys.stdout.write(line)


def loop(messages, config: Config):
    """Main loop for the program"""

    result = session.prompt(
        ">>> ", multiline=True, prompt_continuation=prompt_continuation
    )

    messages.append({"role": "user", "content": result})

    import pdb; pdb.set_trace()

    spinner = Spinner()
    spinner.start()

    response = openai.ChatCompletion.create(
        model=config.get("model"),
        temperature=config.get("temperature"),
        messages=messages,
    )
    message = response["choices"][0]["message"]

    spinner.stop()

    messages.append(message)

    print(" ")
    terminal_width = os.get_terminal_size().columns
    highlight_codeblocks(message["content"], columns=terminal_width)
    print(" ")

    return messages


def main():
    print(f"AIssist v.{__version__}. ESCAPE followed by ENTER to send. Ctrl-C to quit")

    config = Config()

    messages = [{"role": "system", "content": prompt}]

    try:
        while True:
            messages = loop(messages, config)
    except (KeyboardInterrupt, EOFError):
        # Ctrl-C and Ctrl-D
        sys.exit(0)
    except Exception:
        raise


if __name__ == "__main__":
    main()
