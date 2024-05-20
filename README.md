# Chat LLM for Myself
## Overview
...

## ToDo
- [ ] Automatically create a template file if `assets/model_info.json` does not exist.
- [x] Get list from `assets/model_info.json` for Model's options other than OpenAI and Anthropic in `src/main.py`.
- [ ] Move information other than the API key stored in `.env` to a newly created `conf.py`.
- [ ] Separate the logger functionality currently in `src/utils/json_reader.py`.
- [ ] Change the JsonReader class in `src/utils/json_reader.py` to a normal class instead of static, as it will hold an instance for testing DI and have file paths as its members.
- [ ] `src/main.py` should hold instances of JsonReader, Logger, and Client.
    - For testing, Client can be None, but how should we handle DI in production?
    - It might be fine to use OpenAIClient as the default, but some users may not use it.
    - Should we create something like `conf.py`, import all clients, and let the user choose?
- [ ] Currently, the default model is GPT-4, but is this the best choice?
    - If we allow users to select the default client as mentioned in the previous issue, should we also let them choose the default model?