# Importing Important Packages:
import google.generativeai as genai
import streamlit as st

# Streamlit page setup
st.set_page_config(page_title="Streamlit Chat", page_icon="💬")
st.header("Chatbot", divider = True)

# Configure Gemini with your API key from Streamlit secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Set default model in session
if "gemini_model" not in st.session_state:
    st.session_state["gemini_model"] = "gemini-1.5-flash"

# Load the model
model = genai.GenerativeModel(st.session_state["gemini_model"])

# Initialize message memory
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display previous messages
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Your Answer."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Compose the initial prompt as a single user message with system instructions + few-shot examples
initial_prompt = """
You are an HR Executive that is taking an interview from a person named Ali Sina Ghulami. He has applied for
an intermediate level data scientist in your company Amazon. He mentioned that he has 2 years of experience at Google.
He said that he has the following skills, "I have skills in Python, R, and SQL, along with expertise in machine learning, statistics, and data wrangling. I’m also proficient in data visualization, deep learning, NLP, and time series analysis. Additionally, I’m familiar with big data tools like Spark and Hadoop, cloud platforms such as AWS and GCP, and I have strong communication, critical thinking, and data storytelling abilities."
take an interview of 6 questions related to the context provided.
Ask each question only once in a time after the Ali Sina's responses. You shouldn't respond unless he answers to your questions
"""

# Prepare the chat history WITHOUT system role
chat_history = [
    {"role": "user", "parts": [initial_prompt]}
]

# Append the real conversation
chat_history.extend(
    {"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages
)

# Generate response with streaming
response = model.generate_content(chat_history, stream=True)

full_response = ""
placeholder = st.empty()

for chunk in response:
    if chunk.text:
        full_response += chunk.text
        placeholder.markdown(full_response)

st.session_state.messages.append({"role": "assistant", "content": full_response})
