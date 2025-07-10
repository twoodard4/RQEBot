from openai import OpenAI
import streamlit as st

# ✅ App configuration
st.set_page_config(page_title="RQEBot: Root Question Explorer", layout="wide")
st.title("🧠 RQEBot — Root Question Explorer")
st.markdown("_Modeling deeper inquiry through reflective questioning._")

# ✅ Use your Streamlit Cloud secret key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ✅ Editable scenario field
scenario = st.text_area(
    "📘 Scenario (editable):", 
    height=100, 
    value=(
        "Multiple parents have requested IEEs citing disagreement with district evaluations. "
        "Documentation is inconsistent, and escalation procedures vary across campuses."
    )
)

# ✅ Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []  # List of tuples (speaker, text)
if "summary" not in st.session_state:
    st.session_state.summary = []  # List of strings (questions asked)

# ✅ User question input
user_input = st.text_input("💬 Ask a question about this scenario:")

# ✅ GPT call logic
def reframe_with_gpt(user_input, summary, scenario, question, history):
    summary_text = "\n".join(summary) if isinstance(summary, list) else str(summary)
    history_text = "\n".join(text for _, text in history) if history else ""

    prompt = f"""
You are RQEBot, a facilitative AI designed to support root cause analysis. Here's the current scenario:

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

Your response:
"""

    response = client.chat.completions.create(
        model="gpt-4o",  # or "gpt-3.5-turbo" if you aren't on GPT-4 API tier,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()

# ✅ When a question is asked
if user_input:
    with st.spinner("RQEBot is thinking..."):
        response = reframe_with_gpt(
            user_input,
            st.session_state.summary,
            scenario,
            user_input,  # question param is same
            st.session_state.history
        )
        st.session_state.summary.append(user_input)
        st.session_state.history.append(("You", user_input))
        st.session_state.history.append(("RQEBot", response))

# ✅ Display chat history
for speaker, text in st.session_state.history:
    st.markdown(f"**{speaker}:** {text}")

# ✅ Show summary after 6+ questions
if len(st.session_state.summary) >= 6:
    st.markdown("---")
    st.subheader("🧩 Inquiry Summary")
    st.markdown("\n".join(f"- {q}" for q in st.session_state.summary))
    st.success("You’ve asked multiple deep questions. Consider shifting into action planning based on emerging patterns.")
