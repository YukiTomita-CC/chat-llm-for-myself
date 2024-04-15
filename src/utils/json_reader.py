import json


class JsonReader:
    @staticmethod
    def get_filepath_and_stop_tokens(model) -> tuple[str, list[str]]:
        with open("model_info.json", "r") as f:
            model_info = json.load(f)

        for m in model_info['models']:
            if m['name'] == model:
                return (m['gguf_file_path'], m['stop_tokens'])
        
        return ("", [])
