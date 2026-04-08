import streamlit as st
from core.orchestrator import run_agent_turn, initialize_session_state

st.set_page_config(page_title="Industrial AI Copilot", page_icon="🤖", layout="wide")
st.title("Industrial AI Copilot")

initialize_session_state(st.session_state)

for msg in st.session_state["full_chat_history"]:
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


user_input = st.chat_input("Please enter your question:")

if user_input:
    run_agent_turn(user_input, st.session_state)
    st.rerun()


with st.sidebar:
    st.header("Trace Panel")

    with st.expander("Current Summary", expanded=False):
        st.text(st.session_state.get("summary", ""))

    with st.expander("Current Structured Memory", expanded=True):
        st.json(st.session_state.get("memory", {}))

    trace = st.session_state.get("last_trace")

    with st.expander("Last Plan", expanded=True):
        if trace and trace.get("plan"):
            st.json(trace["plan"])
        else:
            st.info("No plan yet.")

    with st.expander("Last Execution Trace", expanded=False):
        if trace:
            st.write("### Turn Count")
            st.write(trace.get("turn_count"))

            st.write("### User Input")
            st.write(trace.get("user_input"))

            st.write("### Pre-turn State")
            st.json(trace.get("pre_turn_state", {}))

            st.write("### Steps")
            for step in trace.get("steps", []):
                st.write(f"#### {step['step']}")
                if isinstance(step["detail"], dict):
                    st.json(step["detail"])
                else:
                    st.write(step["detail"])
            
            if trace.get("execution_result"): 
                st.write("### Observations")
                for obs in trace["execution_result"].get("observations", []):
                    st.write(f"- {obs}")

            st.write("### Post-turn State")
            st.json(trace.get("post_turn_state", {}))

            st.write("### Final Answer")
            st.write(trace.get("final_answer", ""))
        else:
            st.info("No trace yet. Ask a question to generate one.")