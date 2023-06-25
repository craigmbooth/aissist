# AI Assistant

This library was written to scratch a personal itch.  I have found GPT 3.5 to be incredibly useful in my day-to-day coding activities, but also found that having to go to a web browser and interact there was tedious.  What I really wanted was a tool that would:

1. Be accessible from a simple command line prompt (`ai`)
1. Open up a shell to talk to ChatGPT, with the system already prompted to respond tersely but helpfully to coding questions
1. Have chat history accessible with the up arrow
1. Have syntax highlighting on ChatGPT responses
1. Have multi-line editing capabilities on multi-line prompts

THis library is just that.

## Installation

Via pypi

```bash
pip install aissistant
```

There is one required environment variable, `OPENAI_API_KEY`, which should contain an OpenAI API key.

## Usage

Invoke the program with `ai`.  There are few controls. Simply enter a prompt, and hit Escape THEN Enter to submit the prompt.

Inside of each session there is a history, and you can use the up arrow to revisit and edit previous prompts.