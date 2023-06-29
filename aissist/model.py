import openai
import tiktoken

from .exceptions import InvalidParameterError


class Model:
    # Map model to
    model_lookup = {
        "gpt-3.5-turbo": 4096,
        "gpt-3.5-turbo-16k": 16384,
        "gpt-3.5-0613": 4096,
        "gpt-3.5-16k-0613": 16384,
        "gpt-4": 8192,
        "gpt-4-0613": 8192,
        "gpt-4-32k": 32768,
        "gpt-4-32k-0613": 32768,
    }

    def __init__(self, name: str):
        self.name = name
        try:
            self.context = self.model_lookup[self.name]
        except KeyError:
            raise InvalidParameterError(f"Invalid model name: {self.name}")

    @property
    def encoding(self):
        return tiktoken.encoding_for_model(self.name)

    def call(self, messages, config):
        self.trim_messages_to_context(messages, config.get("max_tokens"))

        response = openai.ChatCompletion.create(
            model=self.name,
            temperature=config.get("temperature"),
            max_tokens=config.get("max_tokens"),
            messages=messages,
            stream=False,
        )

        message = response["choices"][0]["message"]
        return message

    def messages_to_tokens(self, messages, model="gpt-3.5-turbo-0613"):
        """Return the number of tokens used by a list of messages.

        https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
        """

        if model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
        }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = (
                4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            )
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif "gpt-3.5-turbo" in model:
            return self.messages_to_tokens(messages, model="gpt-3.5-turbo-0613")
        elif "gpt-4" in model:
            return self.messages_to_tokens(messages, model="gpt-4-0613")
        else:
            raise NotImplementedError(
                f"""messages_to_tokens() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            )
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(self.encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    def trim_messages_to_context(self, messages, max_tokens):
        message_tokens = self.messages_to_tokens(messages, self.name)

        total_tokens = message_tokens + max_tokens

        if total_tokens > self.context:
            messages.pop(0)
            return self.trim_messages_to_context(messages, max_tokens)
        else:
            return messages
