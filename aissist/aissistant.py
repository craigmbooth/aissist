import os
import sys

import openai
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from pygments import highlight
from pygments.formatters import TerminalTrueColorFormatter
from pygments.lexers import guess_lexer

from .code_formatter import CodeFormatter
from .config import Config
from .spinner import Spinner
from .version import __version__

try:
    openai.api_key = os.environ["OPENAI_API_KEY"]
except KeyError:
    print("Please put your API key in the OPENAI_API_KEY environment variable.")
    sys.exit(1)


def prompt_continuation(width: int, line_number, is_soft_wrap):
    return "." * (width - 1) + " "


def loop(messages, config: Config, session, code_formatter: CodeFormatter):
    """Main loop for the program"""

    result = session.prompt(
        ">>> ", multiline=True, prompt_continuation=prompt_continuation
    )

    messages.append({"role": "user", "content": result})

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
    code_formatter.highlight_codeblocks(message["content"], columns=terminal_width)
    print("\n")

    return messages


def main():
    print(f"AIssist v.{__version__}. ESCAPE followed by ENTER to send. Ctrl-C to quit")
    print("\n")
    config = Config()

    prompt = config.get_prompt()

    style = Style.from_dict({"prompt": "#aaaaaa"})
    session = PromptSession(style=style)

    messages = [{"role": "system", "content": prompt}]

    code_formatter = CodeFormatter(config)

    try:
        while True:
            messages = loop(messages, config, session, code_formatter)
    except (KeyboardInterrupt, EOFError):
        # Ctrl-C and Ctrl-D
        sys.exit(0)
    except Exception:
        raise


if __name__ == "__main__":
    main()
