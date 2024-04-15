import os

from anthropic import Anthropic, AuthenticationError


class AnthropicClient:
    def __init__(self):
        try:
            self.client = Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
        except KeyError:
            self.client = None
        except AuthenticationError:
            self.client = None
        
    def generate_response(self, model, system_prompt, messages):
        if self.client is None:
            yield f"You can not use {model}. Please add `ANTHROPIC_API_KEY` to `/.env`."
        
        else:
            with self.client.messages.stream(
                max_tokens=4096,
                messages=messages,
                model=model,
                system=system_prompt
            ) as stream:
                for text in stream.text_stream:
                    yield text
