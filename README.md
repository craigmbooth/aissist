# AI Assistant

[![Test AIssist](https://github.com/craigmbooth/aissist/actions/workflows/on-push.yml/badge.svg?branch=master&event=push)](https://github.com/craigmbooth/aissist/actions/workflows/on-push.yml)

AIssist is a simple, but capable command-line-interface (CLI) to chat with OpenAI's cutting-edge AI models.

Install me with `pip install aissist`.  Set the `OPENAI_API_KEY` environment variable to be your OpenAI API key, then type `ai`.

## Why AIssist?

This library was written to scratch a personal itch.  I have found GPT 3.5 to be incredibly useful in my day-to-day coding activities, but also found that having to go to a web browser and interact there was tedious.  What I really wanted was a tool that would:

1. Be accessible from a simple command line prompt (`ai`)
1. That single command should open up a shell to interact with ChatGPT, with the system already prompted to respond tersely but helpfully to coding questions
1. Have chat history accessible with the up arrow
1. Have syntax highlighting on ChatGPT responses
1. Have multi-line editing capabilities on multi-line prompts

This library is precisely that.

## Installation

Install using pypi with

```bash
pip install aissist
```

There is one required environment variable, `OPENAI_API_KEY`, which should contain an OpenAI API key. `aissist` will prompt you if the key is not set or is invalid.

## Usage

Invoke the program with `ai`.  Various pieces of configuration can be edited with command-line parameters, list these with `ai --help`.

Once launched, simply enter a prompt, and hit ESCAPE then ENTER to submit the prompt.

Inside of each session there is a history, and you can use the up arrow to revisit and edit previous prompts.

Here is a simple example

![An example of using aissist to write Python](https://github.com/craigmbooth/aissist/raw/master/images/screenshot.png)

## Configuration

On first run, `aissist` will write a configuration file (`.aissist`) to your home directory.  This file contains a number of configuration options that can be edited.  Each configuration option matches precisely to a command-line argument.  The orde of precedence for taking an option value is

1. Command-line argument
2. `.aissist` setting
3. Default setting

## Versioning

AIssist follows semantic versioning thus you should expect that:

* If the patch version is increased, only bugfixes have taken place
* If the minor version is increased, only additive changes have been made to the program.  Your existing workflows will work fine.
* If the major version is increased, the user may notice backward incompatible changes, or feature deprecations.