import os
import sys

import openai
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from pygments import highlight
from pygments.formatters import TerminalTrueColorFormatter
from pygments.lexers import guess_lexer

from .config import Config
from .exceptions import AIssistError
from .model import Model
from .spinner import Spinner
from .version import __version__

try:
    openai.api_key = os.environ["OPENAI_API_KEY"]
except KeyError:
    print("Please put your API key in the OPENAI_API_KEY environment variable.")
    sys.exit(1)


def prompt_continuation(width: int, line_number, is_soft_wrap):
    return "." * (width - 1) + " "


def loop(config: Config, model: Model):
    """Main loop for the program"""

    # Move the fdollowing two lines into config, too
    style = Style.from_dict({"prompt": "#aaaaaa"})
    session = PromptSession(style=style)
    prompt = config.get_prompt()

    messages = [{"role": "system", "content": prompt}]

    while True:
        result = session.prompt(
            ">>> ", multiline=True, prompt_continuation=prompt_continuation
        )

        messages.append({"role": "user", "content": result})

        spinner = Spinner()
        spinner.start()

        new_message = model.call(messages, config)
        spinner.stop()

        messages.append(new_message)

        print(" ")
        terminal_width = os.get_terminal_size().columns
        config.code_formatter.highlight_codeblocks(
            new_message["content"], columns=terminal_width
        )
        print("\n")


def main():
    print(f"AIssist v.{__version__}. ESCAPE followed by ENTER to send. Ctrl-C to quit")
    print("\n")

    config = Config()
    model = Model(config.get("model"))

    try:
        while True:
            loop(config, model)
    except (KeyboardInterrupt, EOFError):
        # Ctrl-C and Ctrl-D
        sys.exit(0)
    except AIssistError as e:
        print(e)
        sys.exit(1)
    except Exception:
        raise


if __name__ == "__main__":
    main()
