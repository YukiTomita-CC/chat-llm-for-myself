import json
import os
import subprocess
from time import sleep

import psutil
import requests

from utils.json_reader import JsonReader


class LlamacppClient:
    def __init__(self, model):
        self._kill_process_using_port(8080)

        model_info = JsonReader.get_filepath_and_stop_tokens(model)
        self.model_stop_tokens = model_info[1]

        server_path = os.environ['LLAMACPP_SERVER_PATH'] + "/server.exe"
        file_path = model_info[0]
        cpu_threads_num = os.environ['CPU_THREADS_NUM']
        subprocess.Popen([server_path, "-m", file_path, "-c", "4096", "--mlock", "-t", cpu_threads_num, "-ngl", "20"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    
    def __del__(self):
        self._kill_process_using_port(8080)
        print("del")
        
    def generate_response(self, model, system_prompt, messages):
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
                'stop': self.model_stop_tokens,
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
    
    def _kill_process_using_port(self, port):
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        proc.kill()
                        sleep(1)
                        
            except psutil.AccessDenied:
                pass
