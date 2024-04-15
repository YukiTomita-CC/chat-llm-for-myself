import json


class ChatLogger:
    def __init__(self, log_file_path) -> None:
        self.log_file_path = log_file_path

    def save_chat_log(self, system_prompt, messages):
        data = {
            "system_prompt": system_prompt,
            "messages": messages
        }
        
        with open(self.log_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
