import openai
import streamlit as st
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="RQEBot: Root Question Explorer", layout="wide")
st.title("🧠 RQEBot — Root Question Explorer")
st.markdown("_Modeling deeper inquiry through reflective questioning._")

api_key = st.sidebar.text_input("🔐 Enter your OpenAI API key", type="password")
if not api_key:
    st.stop()
openai.api_key = api_key

scenario = st.text_area(
    "📘 Scenario (editable):", 
    height=100, 
    value=(
        "Multiple parents have requested IEEs citing disagreement with district evaluations. "
        "Documentation is inconsistent, and escalation procedures vary across campuses."
    )
)

if "history" not in st.session_state:
    st.session_state.history = []  # List of tuples (speaker, text)
if "summary" not in st.session_state:
    st.session_state.summary = []  # List of strings (questions asked)

user_input = st.text_input("💬 Ask a question about this scenario:")

def reframe_with_gpt(user_input, summary, scenario, question, history):
    # Convert summary list to string with newlines
    summary_text = "\n".join(summary) if isinstance(summary, list) else str(summary)
    # Extract just the text from history tuples for prompt
    history_text = "\n".join(text for _, text in history) if history else ""
    
    prompt = f"""Your prompt here using:
User input: {user_input}
Summary: {summary_text}
Scenario: {scenario}

"{scenario}"

The user just asked:
"{question}"

Here is the history of previous questions:
{history_text}

Respond as follows:
- Interpret the intent of the question
- Affirm its relevance and insight
- Reframe the question one level deeper using systems thinking
- Use a warm, reflective tone modeled on professional coaching language
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content

if user_input:
    with st.spinner("RQEBot is thinking..."):
        response = reframe_with_gpt(
            user_input,
            st.session_state.summary,
            scenario,
            user_input,              # question param is the same as user_input
            st.session_state.history
        )
        st.session_state.summary.append(user_input)
        st.session_state.history.append(("You", user_input))
        st.session_state.history.append(("RQEBot", response))

for speaker, text in st.session_state.history:
    st.markdown(f"**{speaker}:** {text}")

if len(st.session_state.summary) >= 6:
    st.markdown("---")
    st.subheader("🧩 Inquiry Summary")
    st.markdown("\n".join(f"- {q}" for q in st.session_state.summary))
    st.success("You’ve asked multiple deep questions. Consider shifting into action planning based on emerging patterns.")
