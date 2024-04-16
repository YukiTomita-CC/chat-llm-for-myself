import json
import os


class JsonReader:
    @staticmethod
    def get_chat_logs() -> list[str]:
        return ["New Chat"] + [os.path.splitext(file)[0] for file in os.listdir("chat_log") if file.endswith('.json')]
    
    @staticmethod
    def get_register_models_dict() -> dict[str, str]:
        with open("assets/model_info.json", "r", encoding="utf-8") as f:
            model_info = json.load(f)

        model_dict = {}
        for model in model_info['commercial_models']:
            model_dict[model['display_name']] = model['api_name']
        for model in model_info['local_models']:
            model_dict[model['name']] = model['name']

        return model_dict

    @staticmethod
    def get_chat_log_from_target(target: str) -> dict[str, str]:
        with open(f"chat_log/{target}.json", 'r', encoding="utf-8") as file:
            data = json.load(file)
            return data
    
    @staticmethod
    def save_log(target: str, messages: list[dict[str, str]], model="", system_prompt="") -> None:
        if model == "":
            with open(f"chat_log/{target}.json", 'r', encoding="utf-8") as file:
                data = json.load(file)
            
            data['messages'] = messages
        else:
            data = {
                "model": model,
                "system_prompt": system_prompt,
                "messages": messages
            }

        with open(f"chat_log/{target}.json", 'w', encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    @staticmethod
    def get_filepath_and_stop_tokens(model) -> tuple[str, list[str]]:
        with open("assets/model_info.json", "r", encoding="utf-8") as f:
            model_info = json.load(f)

        for m in model_info['local_models']:
            if m['name'] == model:
                return (m['gguf_file_path'], m['stop_tokens'])
        
        return ("", [])
