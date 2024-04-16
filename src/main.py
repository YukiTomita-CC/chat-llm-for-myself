from datetime import datetime

from dotenv import load_dotenv
import streamlit as st
from streamlit_feedback import streamlit_feedback

from utils.json_reader import JsonReader
from provider.anthropic_client import AnthropicClient
from provider.llamacpp_client import LlamacppClient
from provider.openai_client import OpenAIClient


# ===== Initialize State =====
st.set_page_config(layout="wide")

if 'load_env' not in st.session_state:
    load_dotenv()
    st.session_state['load_env'] = True

if 'selectable_models' not in st.session_state:
    st.session_state['selectable_models'] = JsonReader.get_register_models_dict()

if 'client' not in st.session_state:
    st.session_state['client'] = OpenAIClient()
if 'model' not in st.session_state:
    st.session_state['model'] = "GPT-4"

if 'chat_logs' not in st.session_state:
    st.session_state['chat_logs'] = JsonReader.get_chat_logs()
if 'selected_chat_log' not in st.session_state:
    st.session_state['selected_chat_log'] = "New Chat"
if 'is_new_chat' not in st.session_state:
    st.session_state['is_new_chat'] = True
if 'temp_log_name_for_new_chat' not in st.session_state:
    st.session_state['temp_log_name_for_new_chat'] = ""
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

if 'system_prompt' not in st.session_state:
    st.session_state['system_prompt'] = ""
if 'temperature' not in st.session_state:
    st.session_state['temperature'] = 0.8
if 'repeat_penalty' not in st.session_state:
    st.session_state['repeat_penalty'] = 1.1


# ===== Function =====
def changed_model():
    del st.session_state['client']

    st.session_state.messages = []

    change_client()

def change_client():
    if st.session_state['model'] in ["GPT-4", "GPT-3.5"]:
        st.session_state['client'] = OpenAIClient()
    elif st.session_state['model'] in ["Claude 3 Opus", "Claude 3 Sonnet", "Claude 3 Haiku"]:
        st.session_state['client'] = AnthropicClient()
    else:
        st.session_state['client'] = LlamacppClient(st.session_state['model'])

def change_chat_log():
    if st.session_state['selected_chat_log'] == "New Chat":
        start_new_chat()
    
    else:
        st.session_state['is_new_chat'] = False
        
        log = JsonReader.get_chat_log_from_target(st.session_state['selected_chat_log'])

        st.session_state['model'] = log['model']
        st.session_state['system_prompt'] = log['system_prompt']
        st.session_state['messages'] = log['messages']

        change_client()

def save_log():
    if st.session_state['is_new_chat']:
        log_name = datetime.now().strftime("%Y-%m-%d_%H-%M")
        st.session_state['temp_log_name_for_new_chat'] = log_name

        JsonReader.save_log(
            target=log_name,
            messages=st.session_state['messages'],
            model=st.session_state['model'],
            system_prompt=st.session_state['system_prompt']
        )

        st.session_state['is_new_chat'] = False

    else:
        if st.session_state['selected_chat_log'] == "New Chat":
            target = st.session_state['temp_log_name_for_new_chat']
        else:
            target = st.session_state['selected_chat_log']

        JsonReader.save_log(
            target=target,
            messages=st.session_state['messages']
        )

def start_new_chat():
    st.session_state['selected_chat_log'] = "New Chat"
    st.session_state['is_new_chat'] = True
    st.session_state['temp_log_name_for_new_chat'] = ""
    st.session_state['model'] = "GPT-4"

    st.session_state['system_prompt'] = ""

    st.session_state['temperature'] = 0.8
    st.session_state['repeat_penalty'] = 1.1

    st.session_state['messages'] = []

    st.session_state['chat_logs'] = JsonReader.get_chat_logs()


# ===== UI =====
with st.sidebar:
    st.button("Start New Chat", on_click=start_new_chat)

    st.selectbox(
        label="Chat Log",
        options=st.session_state['chat_logs'],
        key='selected_chat_log',
        on_change=change_chat_log
        )


    st.selectbox(
        label="Model",
        options=st.session_state['selectable_models'].keys(),
        key='model',
        on_change=changed_model
    )

    st.text_area(
        label="System Prompt",
        key='system_prompt'
        )

    st.slider(
        label="Temperature",
        min_value=0.0,
        max_value=1.0,
        step=0.1,
        key='temperature'
    )

    st.slider(
        label="repeat_penalty",
        min_value=1.0,
        max_value=2.0,
        step=0.1,
        key='repeat_penalty'
    )
    
    st.button(
        label="Reset",
        on_click=start_new_chat
    )

messages_container = st.container()

for message in st.session_state['messages']:
    with messages_container.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Message LLM..."):
    st.session_state['messages'].append({"role": "user", "content": prompt})
    save_log()
    with messages_container.chat_message("user"):
        st.markdown(prompt)

    with messages_container.chat_message("assistant"):
        stream = st.session_state['client'].generate_response(
            model=st.session_state['selectable_models'][st.session_state['model']],
            system_prompt=st.session_state['system_prompt'],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state['messages']
            ],
            temperature=st.session_state['temperature'],
            repeat_penalty=st.session_state['repeat_penalty']
        )
        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})
    save_log()
