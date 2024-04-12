from dotenv import load_dotenv
import streamlit as st

from provider.anthropic_client import AnthropicClient
from provider.llamacpp_client import LlamacppClient
from provider.openai_client import OpenAIClient


model_dict = {
    "GPT-4": "gpt-4-turbo",
    "GPT-3.5": "gpt-3.5-turbo",
    "Claude 3 Opus": "claude-3-opus-20240229",
    "Claude 3 Sonnet": "claude-3-sonnet-20240229",
    "Claude 3 Haiku": "claude-3-haiku-20240307",
    "Starling-LM-7B-beta": "Starling-LM-7B-beta",
    "RakutenAI-7B-chat": "RakutenAI-7B-chat"
}


st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "load_env" not in st.session_state:
    load_dotenv()
    st.session_state["load_env"] = True

if "openai_client" not in st.session_state:
    st.session_state["openai_client"] = OpenAIClient()
if "anthropic_client" not in st.session_state:
    st.session_state["anthropic_client"] = AnthropicClient()
if "llamacpp_client" not in st.session_state:
    st.session_state["llamacpp_client"] = LlamacppClient()

if "model" not in st.session_state:
    st.session_state["model"] = "GPT-4"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.8
if "top_k" not in st.session_state:
    st.session_state.top_k = 40
if "top_p" not in st.session_state:
    st.session_state.top_p = 0.95
if "repeat_penalty" not in st.session_state:
    st.session_state.repetition_penalty = 1.1
if "n_predict" not in st.session_state:
    st.session_state.n_predict = -1


def reset_param():
    st.session_state.temperature = 0.8
    st.session_state.top_k = 40
    st.session_state.top_p = 0.95
    st.session_state.repetition_penalty = 1.1
    st.session_state.n_predict = -1

    st.session_state.messages = []


# ===== UI =====
st.title(":speech_balloon: Chat")

chat_area, param_area = st.columns([0.7, 0.3], gap="large")

with chat_area:
    messages_container = st.container(height=620)

    for message in st.session_state.messages:
        with messages_container.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Message LLM..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with messages_container.chat_message("user"):
            st.markdown(prompt)

        with messages_container.chat_message("assistant"):
            stream = st.session_state.llamacpp_client.generate_response(
                model=model_dict[st.session_state["model"]],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
            )
            response = st.write_stream(stream)

        st.session_state.messages.append({"role": "assistant", "content": response})

with param_area:
    with st.container(border=True):
        model_selectbox = st.selectbox(
            label="Model",
            options=model_dict.keys(),
            key="model"
        )

        with st.container(border=True):
            temperature = st.slider(
                label="Temperature",
                min_value=0.0,
                max_value=1.0,
                step=0.1,
                key="temperature"
            )

            top_k = st.slider(
                label="Top-k",
                min_value=1,
                max_value=100,
                step=1,
                key="top_k"
            )

            top_p = st.slider(
                label="Top-p",
                min_value=0.0,
                max_value=1.0,
                step=0.05,
                key="top_p"
            )

            repetition_penalty = st.slider(
                label="Repetition Penalty",
                min_value=1.0,
                max_value=2.0,
                step=0.1,
                key="repetition_penalty"
            )

            n_predict = st.slider(
                label="N Predict",
                min_value=-1,
                max_value=256,
                step=1,
                key="n_predict"
            )

            st.button("Reset", on_click=reset_param)
