import streamlit as st
from core.llm_client import ask_llm
from core.orchestrator import initialize_session_state, run_agent_turn


st.set_page_config(page_title="Industrial AI Copilot", page_icon="🤖")
st.title("industrial AI Copilot")

initialize_session_state(st.session_state)

for msg in st.session_state["chat_history"]:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.write(msg["content"])
        if msg.get("tool_results"):
            with st.expander("Tool Details"):
                st.write("### 🔧 Tools Used")
                for tool_name in msg.get("tools_used", []):
                    st.write(f"- {tool_name}")

                st.write("### 📦 Tool Results")
                for tool_name, tool_result in msg["tool_results"].items():
                    st.write(f"#### {tool_name}")
                    st.json(tool_result)
        if msg.get("trace"):
            with st.expander("Execution Trace"):
                trace = msg["trace"]

                st.write(f"Turn: {trace.get('turn_count')}")
                st.write(f"User Input: {trace.get('user_input')}")

                st.write("### Steps")
                for step in trace.get("steps", []):
                    st.write(f"#### {step['step']}")
                    if isinstance(step["detail"], dict):
                        st.json(step["detail"])
                    else:
                        st.write(step["detail"])
        

user_input = st.chat_input("Please enter your question: ")



if user_input:

    with st.chat_message("user"):
        st.write(user_input)
         
    run_agent_turn(user_input, st.session_state)
    st.rerun()

