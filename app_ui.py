"""Web chat UI:  streamlit run app_ui.py"""
import streamlit as st
from assistant import brain, config

st.set_page_config(page_title=f"{config.NAME} Assistant", page_icon="🎙️")
st.title(f"🎙️ {config.NAME} – Mini Alexa")
st.caption("Try: 'time kya hai', 'weather in Delhi', 'calculate 12 plus 8', 'note buy milk', 'open youtube'")

if "chat" not in st.session_state:
    st.session_state.chat = [("assistant", f"Namaste! Main {config.NAME} hu. 'help' bolo.")]

for role, msg in st.session_state.chat:
    st.chat_message(role).write(msg)

if prompt := st.chat_input("Kuch poochho..."):
    st.session_state.chat.append(("user", prompt))
    st.chat_message("user").write(prompt)
    reply = brain.respond(prompt)
    st.session_state.chat.append(("assistant", reply))
    st.chat_message("assistant").write(reply)
