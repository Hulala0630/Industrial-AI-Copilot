import streamlit as st
from core.llm_client import ask_llm

st.title("industrial AI Copilot")

user_input = st.text_input("Please enter your question: ")

if user_input:
    result = ask_llm(user_input)
    st.write(result)