import streamlit as st
from core.llm_client import ask_llm

st.set_page_config(page_title="Industrial AI Copilot", page_icon="🤖")
st.title("industrial AI Copilot")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "last_tool_info" not in st.session_state:
    st.session_state["last_tool_info"] = None

for msg in st.session_state["chat_history"]:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.write(msg["content"])

user_input = st.chat_input("Please enter your question: ")

if user_input:

    st.session_state["chat_history"].append({
    "role": "user",
    "content": user_input
    })
    with st.chat_message("user"):
        st.write(user_input)

    result = ask_llm(st.session_state["chat_history"])

    with st.chat_message("assistant"):
        st.write(result["answer"])

        if result["tools_used"]:
            with st.expander("Tool Details"):
                st.write("### 🔧 Tools Used")
                for tool_name in result["tools_used"]:
                    st.write(f"- {tool_name}")

                st.write("### 📦 Tool Results")
                for tool_name, tool_result in result["tool_results"].items():
                    st.write(f"#### {tool_name}")
                    st.json(tool_result)

    st.session_state["chat_history"].append({
    "role": "assistant",
    "content": result["answer"]
    })

    st.session_state["chat_history"] = st.session_state["chat_history"][-8:]