import os

from openai import OpenAI


class OpenAIClient:
    def __init__(self):
        try:
            self.client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        except KeyError:
            self.client = None
        
    def generate_response(self, model, messages):
        if self.client is None:
            yield f"You can not use {model}. Please add `OPENAI_API_KEY` to `/.env`."
        
        else:
            stream = self.client.chat.completions.create(
                messages=messages,
                model=model,
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    output = chunk.choices[0].delta.content
                    yield output
