import json
import subprocess
from time import sleep

import requests


class LlamacppClient:
    def __init__(self):
        self.client = None
        
    def generate_response(self, model, messages):
        if self.client is None:
            subprocess.Popen(["server.exe", "-m", "Starling-LM-7B-beta.Q8_0.gguf"], creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        sleep(10)
        
        stream = requests.post(
            "http://localhost:8080/completion",
            headers={
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                'prompt': self.convert_openchat(messages),
                # 'temperature': st.session_state.temperature,
                # 'top_k': st.session_state.top_k,
                # 'top_p': st.session_state.top_p,
                # 'repeat_penalty': st.session_state.repetition_penalty,
                # 'n_predict': st.session_state.n_predict,
                'stop': ["<|end_of_turn|>"],
                'stream': True
            }),
            stream=True
            )

        for chunk in stream.iter_lines():
            if chunk.startswith(b'data: '):
                j = json.loads(chunk[6:].decode())
                yield j.get("content", "")

    def convert_vicuna(self, messages):
        prompt = ""
        for message in messages:
            if message["role"] == "user":
                prompt += f"USER: {message['content']}\n"
            elif message["role"] == "assistant":
                prompt += f"ASSISTANT: {message['content']}\n"

        prompt += "ASSISTANT:"
        return prompt

    def convert_openchat(self, messages):
        prompt = ""
        for message in messages:
            if message["role"] == "user":
                prompt += f"GPT4 Correct User: {message['content']}<|end_of_turn|>"
            elif message["role"] == "assistant":
                prompt += f"GPT4 Correct Assistant: {message['content']}<|end_of_turn|>"

        prompt += "GPT4 Correct Assistant:"
        return prompt

    def convert_openchat_for_code(self, messages):
        prompt = f"Code User: {messages[-1]['content']}<|end_of_turn|>Code Assistant:"
        return prompt
