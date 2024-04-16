import json
import os

from anthropic import Anthropic
from anthropic import AuthenticationError, BadRequestError


class AnthropicClient:
    def __init__(self):
        try:
            self.client = Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
        except KeyError:
            self.client = None
        except AuthenticationError:
            self.client = None
        
    def generate_response(self, model, system_prompt, messages, temperature, repeat_penalty):
        if self.client is None:
            yield f"You can not use {model}. Please add `ANTHROPIC_API_KEY` to `/.env`."
        
        else:
            try:
                with self.client.messages.stream(
                    model=model,
                    messages=messages,
                    max_tokens=4096,
                    system=system_prompt,
                    temperature=temperature
                ) as stream:
                    for text in stream.text_stream:
                        yield text
                        
            except BadRequestError as e:
                if e.status_code == 400:
                    j = json.loads(e.response.text)
                    error_message = j['error']['message']
                    if "credit" in error_message:
                        yield f"**<!!!ERROR!!!>** \n\n{j['error']['message']}\n\n[Plans & Billing](https://console.anthropic.com/settings/plans)"
