import os
import sys
from prompt_toolkit import PromptSession
import threading
import time
import openai
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import TerminalFormatter

try:
    openai.api_key = os.environ["OPENAI_API_KEY"]
except KeyError:
    print("Please put your API key in the OPENAI_API_KEY environment variable.")
    sys.exit(1)

prompt = """You are a helpful but succinct chatbot that assists an impatient programmer by directly answering questions. You understand that the programmer is advanced enough to understand succinct phrases and prefers direct answers with little boilerplate.
"""

session = PromptSession()

spinner_flag = True  # Flag to control the spinner

def spinner():
    while spinner_flag:
        for char in '|/-\\':
            sys.stdout.write('\r' + char)
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write("\r")

def stop_spinner():
    global spinner_flag
    spinner_flag = False

def start_spinner():
    global spinner_flag
    spinner_flag = True

def prompt_continuation(width: int,
                        line_number,
                        is_soft_wrap):
    return '.' * (width-1) + " "


def bold_single_backticks(text):
    """Formats a given string by making text enclosed in single backticks bold,
    using ANSI escape codes.
    """
    in_backticks = False
    result = ''
    for indx, c in enumerate(text):
        if c == '`':
            
            if in_backticks:
                result += '\033[0m'  # Reset text formatting
                in_backticks = False
            else:
                result += '\033[1m'  # Bold text
                in_backticks = True
        else:
            result += c

    if in_backticks:
        result += '\033[0m'  # Reset text formatting

    return result


def highlight_codeblocks(markdown):
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
            print(line)

def loop(messages):
    """Main loop for the program"""
    
    result = session.prompt(">>> ", multiline=True,
                prompt_continuation=prompt_continuation)

    messages.append(
        {"role": "user", "content": result}
    )

    start_spinner()
    spinner_thread = threading.Thread(target=spinner)
    spinner_thread.start()

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    message = response["choices"][0]["message"]
    stop_spinner()
    spinner_thread.join()

    messages.append(message)
    print(" ")
    highlight_codeblocks(message["content"])
    print(" ")

    return messages

def main():

    print("ESCAPE followed by ENTER to send. Ctrl-C to quit")

    messages = [
        {"role": "system", "content": prompt}
    ]

    try:
        while True:
            messages = loop(messages)
    except (KeyboardInterrupt, EOFError):
        # Ctrl-C and Ctrl-D
        sys.exit(0)
    except Exception:
        raise

if __name__ == "__main__":
    main()