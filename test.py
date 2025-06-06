import streamlit as st
import google.generativeai as genai

# Streamlit page setup
st.set_page_config(page_title="Streamlit Chat", page_icon="💬")
st.title("Interview Simulator")

# Setup completion flag
if "setup_complete" not in st.session_state:
    st.session_state["setup_complete"] = False

def complete_setup():
    st.session_state["setup_complete"] = True

# Setup phase
if not st.session_state["setup_complete"]:
    st.subheader("Personal Information:", divider="rainbow")

    st.session_state["name"] = st.text_input("Name", value=st.session_state.get("name", ""), placeholder="Enter your name")
    st.session_state["experience"] = st.text_area("Experience", value=st.session_state.get("experience", ""), placeholder="Describe your experience")
    st.session_state["skills"] = st.text_area("Skills", value=st.session_state.get("skills", ""), placeholder="List your skills")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state["level"] = st.radio("Choose Your Level", options=["Junior", "Intermediate", "Senior"], index=0)
    with col2:
        st.session_state["job_title"] = st.selectbox("Select Job Title", ("Data Scientist", "Data Engineer", "ML Engineer", "BI Analyst", "Financial Analyst"))

    st.session_state["company"] = st.selectbox("Select Company", ("Amazon", "Meta", "Udemy", "365 Company", "Nestle", "LinkedIn", "Spotify"))

    if st.button("Start Interview", on_click=complete_setup):
        st.write("Setup Complete. Starting interview...")

# Chat phase
if st.session_state["setup_complete"]:
    st.info(f"Hello {st.session_state['name']}, it is a pleasure to meet you. Let's start with your introduction.")

    # Configure Gemini
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

    # Initialize chat only once
    if "chat" not in st.session_state:
        system_message = (
            f"You are an HR executive interviewing {st.session_state['name']}, "
            f"who has experience: {st.session_state['experience']}, and skills: {st.session_state['skills']}. "
            f"The position is {st.session_state['level']} {st.session_state['job_title']} at {st.session_state['company']}. "
            "Ask questions like in a real job interview, one at a time."
        )
        model = genai.GenerativeModel("gemini-1.5-flash")
        st.session_state.chat = model.start_chat(history=[{"role": "user", "parts": [system_message]}])
        st.session_state.messages = []  # only for display, optional

    # Display message history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Get user input
    if prompt := st.chat_input("Your Answer."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Gemini response
        response = st.session_state.chat.send_message(prompt)
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
