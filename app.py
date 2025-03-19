import streamlit as st
from chat_screen import chat_screen

# ----- Page Configuration -----
st.set_page_config(page_title="TeleMedicine Chatbot" , page_icon=":hospital:")

# ----- Custom CSS for Styling -----
st.markdown(
    """
    <style>
    /* Set the background color to white */
    .reportview-container {
        background-color: white;
    }
    /* Center the container */
    .centered-container {
        max-width: 800px;
        margin: auto;
        padding: 2rem;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    /* Input field styling */
    .stTextInput > div > input {
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ddd;
        width: 100%;
    }
    /* Button styling */
    .stButton > button {
       
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        width: 100%;
    }
    .stButton > button:hover {

    }
    /* Title styling */
    .title {
        font-family: 'Arial', sans-serif;
        color: #333;
        margin-top: 20px;
    }
    /* Subtitle styling */
    .subtitle {
        font-family: 'Arial', sans-serif;
        color: #666;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----- Dummy User Database -----
USERS = {
    "admin": "admin",
}


# ----- Initialize Session State -----
query_params = st.query_params

if "logged_in" not in st.session_state:
    st.session_state.logged_in = query_params.get("logged_in", "False") == "True"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ----- Login Screen -----
def login_screen():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>Welcome to Tele Medicine</h1>", unsafe_allow_html=True)
        
    st.markdown('<h4 class="subtitle">Sign In</h4>', unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Go To Chat", type="primary"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.query_params["logged_in"] = "True"
            st.rerun()
        else:
            st.error("Invalid username or password. Please try again.")

# ----- App Routing -----
if not st.session_state.logged_in:
    login_screen()
else:
    chat_screen()



