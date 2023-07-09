"""Contains the Model class, which represents an OpenAI model."""
from typing import Generator, TypedDict, cast

import openai
import tiktoken
from retry import retry

from .config import Config
from .exceptions import InvalidParameterError


class OpenAIMessage(TypedDict):
    """Structure of an element in a conversation with the OpenAI API."""

    role: str
    content: str


class Model:
    # Map model to context length.
    model_lookup: dict[str, int] = {
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
        except KeyError as exc:
            raise InvalidParameterError(f"Invalid model name: {self.name}") from exc

    @property
    def encoding(self) -> tiktoken.Encoding:
        return tiktoken.encoding_for_model(self.name)

    @retry(
        (
            openai.error.APIError,
            openai.error.APIConnectionError,
            openai.error.RateLimitError,
            openai.error.ServiceUnavailableError,
        ),
        tries=3,
        delay=2,
        backoff=2,
    )
    def call(self, messages: list[OpenAIMessage], config: Config) -> OpenAIMessage:
        self.trim_messages_to_context(messages, config.get("max_tokens"))

        # n.b. ignoring types because
        # error: Call to untyped function "create" of "ChatCompletion" in typed context
        response = openai.ChatCompletion.create(  # type: ignore
            model=self.name,
            temperature=config.get("temperature"),
            max_tokens=config.get("max_tokens"),
            messages=messages,
            stream=False,
        )

        message = response["choices"][0]["message"]
        return cast(OpenAIMessage, message)

    @retry(
        (
            openai.error.APIError,
            openai.error.APIConnectionError,
            openai.error.RateLimitError,
            openai.error.ServiceUnavailableError,
        ),
        tries=3,
        delay=2,
        backoff=2,
    )
    def stream_call(
        self, messages: list[OpenAIMessage], config: Config
    ) -> Generator[str, None, str]:
        self.trim_messages_to_context(messages, config.get("max_tokens"))

        # n.b. ignoring types because
        # error: Call to untyped function "create" of "ChatCompletion" in typed context
        response = openai.ChatCompletion.create(  # type: ignore
            model=self.name,
            temperature=config.get("temperature"),
            max_tokens=config.get("max_tokens"),
            messages=messages,
            stream=True,
        )

        buffer = ""
        for chunk in response:
            if chunk.choices[0]["finish_reason"] is not None:
                return buffer

            delta = chunk.choices[0]["delta"]["content"]
            yield delta

        return ""

    def messages_to_tokens(
        self, messages: list[OpenAIMessage], model: str = "gpt-3.5-turbo-0613"
    ) -> int:
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
                num_tokens += len(self.encoding.encode(cast(str, value)))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    def trim_messages_to_context(
        self, messages: list[OpenAIMessage], max_tokens: int
    ) -> list[OpenAIMessage]:
        """Given a list of messages, discard old messages until the total number of
        tokens in the messages plus the max tokens in the completion is less than the
        context length of the model.
        """

        message_tokens = self.messages_to_tokens(messages, self.name)

        total_tokens = message_tokens + max_tokens

        if total_tokens > self.context:
            messages.pop(0)
            return self.trim_messages_to_context(messages, max_tokens)

        return messages
