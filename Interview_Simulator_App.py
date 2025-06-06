# IMPORTING IMPORTANT PACKAGES:
import streamlit as st
import google.generativeai as genai 
from streamlit_js_eval import streamlit_js_eval

# STREAMLIT PAGE SETUP
st.set_page_config(page_title= "Streamlit Chat", page_icon="💬")
st.title("Interview Simulator")

# Initialize session state variable to track setup completion
if "setup_complete" not in st.session_state:
    st.session_state["setup_complete"] = False

if "user_message_count" not in st.session_state:
    st.session_state["user_message_count"] = 0

if "feedback_shown" not in st.session_state:
    st.session_state["feedback_shown"] = False

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "chat_complete" not in st.session_state:
    st.session_state["chat_complete"] = False

# HELPER FUNCTION FOR SETUP ACTIVATION
def complete_setup():
    st.session_state["setup_complete"] = True

# HELPER FUNCTION FOR FEEDBACK SETUP ACTIVATION
def show_feedback():
    st.session_state.feedback_shown = True

# SETUP STAGE FOR COLLECTING USER DETAILS
if not st.session_state.setup_complete:
    
    # PERSONAL INFORMATION SET UP 
    st.subheader("Personal Information:", divider = "rainbow")
    if "name" not in st.session_state:
        st.session_state["name"] = ""

    if "experience" not in st.session_state:
        st.session_state["experience"] = ""

    if "skills" not in st.session_state:
        st.session_state["skills"] = ""

    st.session_state["name"] = st.text_input(label= "Name", 
                        max_chars = 40,
                        value =  st.session_state["name"],
                        placeholder = "Enter Your Name")

    st.session_state["experience"] = st.text_area(label = "Experience", 
                            value = st.session_state["experience"], 
                            height = None, 
                            max_chars = 200, 
                            placeholder = "Describe Your Experience")

    st.session_state["skills"] = st.text_area(label = "Skills", 
                            value = st.session_state["skills"], 
                            height = None, 
                            max_chars = 200, 
                            placeholder = "List Your Skills")


    # COMPANY, LEVEL AND JOB TITLE
    col1, col2 = st.columns(2)

    if "level" not in st.session_state:
        st.session_state["level"] = "Junior"
    if "job_title" not in st.session_state:
        st.session_state["job_title"] = "Data Scientist"
    if "company" not in st.session_state:
        st.session_state["company"] = "Amazon"

    with col1:
        st.session_state["level"] = st.radio(
            "Choose Your Level",
            key = "Visibility",
            options = ["Junior", "Intermediate", "Senior"]
        )

    with col2:
        st.session_state["job_title"] = st.selectbox(
            "Select The Job Title",
            ("Data Scientist", "Data engineer", "ML Engineer", "BI Analyst", "Financial Analyst")
        )

    st.session_state["company"] = st.selectbox(
        "Select Your Company",
        ("Amazon", "Meta", "Udemy", "365 Company", "Nestle", "LinkedIn", "Spotify")
    )

    if st.button("Start Interview", on_click=complete_setup):
        st.write("Setup Complete. Starting the Interview...")

# Chat phase
if st.session_state["setup_complete"] and not st.session_state.feedback_shown and not st.session_state.chat_complete:
    st.info(f"Hello {st.session_state['name']}, it is a pleasure to meet you. Let's start with your introduction.")

    # Configure Gemini
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

    # Initialize chat only once
    if "chat" not in st.session_state:
        system_message = (
            f"You are an HR executive interviewing {st.session_state['name']}, "
            f"who has experience: {st.session_state['experience']}, and skills: {st.session_state['skills']}. "
            f"The position is {st.session_state['level']} {st.session_state['job_title']} at {st.session_state['company']}. "
            "Ask questions like in a real job interview, one at a time. You Should Ask 5 Questions and end the conversation when reached to the fifth question"
        )
        model = genai.GenerativeModel("gemini-1.5-flash")
        st.session_state.chat = model.start_chat(history=[{"role": "user", "parts": [system_message]}])
        st.session_state.messages = []  # only for display, optional

    # Display message history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if st.session_state.user_message_count < 5:
        # Get user input
        if prompt := st.chat_input("Your Answer.", max_chars=1000):
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            if st.session_state.user_message_count < 4:
                # Gemini response
                response = st.session_state.chat.send_message(prompt)
                with st.chat_message("assistant"):
                    st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
        
            st.session_state.user_message_count += 1

    # Check if the user message count reaches 5
    if st.session_state.user_message_count >= 5:
        st.session_state.chat_complete = True

# Show "Get Feedback" 
if st.session_state.chat_complete and not st.session_state.feedback_shown:
    if st.button("Get Feedback", on_click=show_feedback):
        st.write("Fetching feedback...")

if st.session_state.feedback_shown:
    st.subheader("Feedback", divider="rainbow")

    conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])

    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

    # Initialize the Gemini model (use 'gemini-pro' or 'gemini-1.5-pro' if available)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Generate feedback using the stored conversation history
    feedback_prompt = f"""You are a helpful tool that provides feedback on an interviewee's performance.
    Before the Feedback, give a score of 1 to 10.
    Follow this format:
    Overall Score: //Your score
    Feedback: //Here you put your feedback
    Give only the feedback; do not ask any additional questions.

    This is the interview you need to evaluate. Keep in mind that you are only a tool, and you shouldn't engage in any conversation:
    {conversation_history}"""

    # Generate the feedback response
    feedback_response = model.generate_content(feedback_prompt)

    # Display the feedback
    st.write(feedback_response.text)

    # Button to restart the interview
    if st.button("Restart Interview", type="primary"):
            streamlit_js_eval(js_expressions="parent.window.location.reload()")