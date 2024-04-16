import os

from openai import OpenAI, AuthenticationError


class OpenAIClient:
    def __init__(self):
        try:
            self.client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        except KeyError:
            self.client = None
        except AuthenticationError:
            self.client = None
        
    def generate_response(self, model, system_prompt, messages, temperature, repeat_penalty):
        if self.client is None:
            yield f"You can not use {model}. Please add `OPENAI_API_KEY` to `/.env`."
        
        else:
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages
                
            stream = self.client.chat.completions.create(
                messages=messages,
                model=model,
                stream=True,
                temperature=temperature
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    output = chunk.choices[0].delta.content
                    yield output
