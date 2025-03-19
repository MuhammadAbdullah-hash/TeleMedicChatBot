import time
import streamlit as st
from bot import TeleMedicBot



# Define translations
translations = {
    "en": {
        "title": "AI Tele-Medic",
        "subtitle": "Chat with TeleMedic – Get Instant Answers to Your Symptoms!",
        "ask_placeholder": "Ask Something...",
        "typing_message": "Type your message...",
        "processing": "Processing...",
    },
    "es": {
        "title": "AI Tele-Médico",
        "subtitle": "Chatea con TeleMedic – ¡Obtén respuestas instantáneas sobre tus síntomas!",
        "ask_placeholder": "Pregunta algo...",
        "typing_message": "Escribe tu mensaje...",
        "processing": "Procesando...",
    }
}

# Function to handle streaming responses
def get_bot_response(user_input):
    response_text = ""
    
    for chunk in st.session_state.TELEMEDIC_BOT.chat(user_input, stream=True):
        response_text += chunk
        yield response_text

# Main Chat Screen
def chat_screen():

    if "TELEMEDIC_BOT" not in st.session_state:
        st.session_state.TELEMEDIC_BOT = TeleMedicBot(lang="en")  # Default language

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "waiting_for_response" not in st.session_state:
        st.session_state.waiting_for_response = False

    if "language" not in st.session_state:
        st.session_state.language = "en"  # Default to English

    # Language Toggle
    lang_choice = st.toggle("🇺🇸 English / 🇪🇸 Español", value=(st.session_state.language == "es"))
    st.session_state.language = "es" if lang_choice else "en"
    lang = st.session_state.language

    # Get translated text
    t = translations[lang]

    # Update bot language if changed
    if st.session_state.TELEMEDIC_BOT.lang != lang:
        st.session_state.TELEMEDIC_BOT = TeleMedicBot(lang=lang)
        st.session_state.chat_history = []


    st.title(t["title"])
    st.write(t["subtitle"])

    user_input = None  # Initialize input variable

    # **Apply CSS for Styling**
    st.markdown("""
        <style>
        .chat-container {
            position: relative;
            display: flex;
            align-items: center;
        }
        .borderless-textarea textarea {
            width: 100% !important;
            height: 50px !important;
            font-size: 16px !important;
            border-radius: 20px !important;
            padding-right: 40px !important; /* Space for send button */
            resize: none !important;
        }
        .send-button {
            position: absolute;
            right: 3px;
            bottom: 30px;
            background-color: #0084ff;
            color: white;
            border: none;
            border-radius: 50%;
            width: 35px;
            height: 35px;
            font-size: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)


    # **First Message Input**
    if not st.session_state.chat_history:
        user_input = st.text_area("Ask Something", placeholder=t["ask_placeholder"], key="first_input", label_visibility="collapsed")

        # **Custom HTML for the Send Button Inside Text Area**
        st.markdown("""
        <div class="chat-container">
            <button class="send-button" onclick="sendMessage()">➤</button>
        </div>
        <script>
            function sendMessage() {
                var textArea = document.querySelector("textarea");
                if (textArea && textArea.value.trim() !== "") {
                    textArea.form.requestSubmit();
                }
            }
        </script>
        """, unsafe_allow_html=True)


        if user_input and user_input.strip():
            st.session_state.chat_history.append({"role": "user", "message": user_input})
            st.session_state.waiting_for_response = True
            st.rerun()
    else:
        # **Use chat_input after the first message**
        user_input = st.chat_input(t["typing_message"])

    # **Chat History Display**
    if st.session_state.chat_history:
        chat_placeholder = st.container()
        with chat_placeholder:
            for chat in st.session_state.chat_history:
                if chat["role"] == "user":
                    st.markdown(f"<div style='text-align: right; background-color: #dcf8c6; padding: 10px; border-radius: 10px; margin: 5px; width: fit-content; max-width: 70%; margin-left: auto; word-wrap: break-word; overflow-wrap: break-word;'>"
                                f"{chat['message']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align: left; background-color: #e8e8e8; padding: 10px; border-radius: 10px; margin: 5px; width: fit-content; max-width: 70%; margin-right: auto; word-wrap: break-word; overflow-wrap: break-word;'>"
                                f"{chat['message']}</div>", unsafe_allow_html=True)

    # **Show Processing Spinner if Waiting for Response**
    if st.session_state.waiting_for_response:
        with st.spinner(t["processing"]):
            last_message = st.session_state.chat_history[-1]
            if last_message["role"] == "user":
                with st.empty():
                    bot_response = ""
                    for chunk in get_bot_response(last_message["message"]):
                        bot_response = chunk
                        st.markdown(f"<div style='text-align: left; background-color: #e8e8e8; padding: 10px; border-radius: 10px; margin: 5px; width: fit-content; max-width: 70%; margin-right: auto; word-wrap: break-word; overflow-wrap: break-word;'>"
                                    f"{bot_response}</div>", unsafe_allow_html=True)

                # Append final bot response to chat history
                st.session_state.chat_history.append({"role": "bot", "message": bot_response})
                st.session_state.waiting_for_response = False
                st.rerun()

    # **Handle chat input submission after first message**
    if user_input and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "message": user_input})
        st.session_state.waiting_for_response = True
        st.rerun()



# import time
# import streamlit as st
# from bot import TeleMedicBot

# # Initialize the bot
# TELEMEDIC_BOT = TeleMedicBot()

# # Function to handle streaming responses
# def get_bot_response(user_input):
#     response_text = ""
    
#     for chunk in TELEMEDIC_BOT.chat(user_input, stream=True):
#         response_text += chunk
#         yield response_text

# # Main Chat Screen
# def chat_screen():
#     # Initialize chat history
#     if "chat_history" not in st.session_state:
#         st.session_state.chat_history = []
    
#     if "waiting_for_response" not in st.session_state:
#         st.session_state.waiting_for_response = False  # Track if bot response is pending

#     st.title("AI Tele-Medic")
#     st.write("Chat with TeleMedic – Get Instant Answers to Your Symptoms!")

#     user_input = None  # Initialize input variable

#     # **Apply CSS for Styling**
#     st.markdown("""
#         <style>
#         .chat-container {
#             position: relative;
#             display: flex;
#             align-items: center;
#         }
#         .borderless-textarea textarea {
#             width: 100% !important;
#             height: 50px !important;
#             font-size: 16px !important;
#             border-radius: 20px !important;
#             padding-right: 40px !important; /* Space for send button */
#             resize: none !important;
#         }
#         .send-button {
#             position: absolute;
#             right: 3px;
#             bottom: 30px;
#             background-color: #0084ff;
#             color: white;
#             border: none;
#             border-radius: 50%;
#             width: 35px;
#             height: 35px;
#             font-size: 18px;
#             display: flex;
#             align-items: center;
#             justify-content: center;
#             cursor: pointer;
#         }
#         </style>
#     """, unsafe_allow_html=True)

#     # **First Message Input with Send Button Inside Text Area**
#     if not st.session_state.chat_history:
#         user_input = st.text_area("", placeholder="Ask Something...", key="first_input", label_visibility="collapsed")

#         # **Custom HTML for the Send Button Inside Text Area**
#         st.markdown("""
#         <div class="chat-container">
#             <button class="send-button" onclick="sendMessage()">➤</button>
#         </div>
#         <script>
#             function sendMessage() {
#                 var textArea = document.querySelector("textarea");
#                 if (textArea && textArea.value.trim() !== "") {
#                     textArea.form.requestSubmit();
#                 }
#             }
#         </script>
#         """, unsafe_allow_html=True)

#         if user_input and user_input.strip():
#             st.session_state.chat_history.append({"role": "user", "message": user_input})
#             st.session_state.waiting_for_response = True
#             st.rerun()
#     else:
#         # **Use chat_input after the first message**
#         user_input = st.chat_input("Type your message...")

#     # **Chat History Display**
#     if st.session_state.chat_history:
#         chat_placeholder = st.container()
#         with chat_placeholder:
#             for chat in st.session_state.chat_history:
#                 if chat["role"] == "user":                    
#                     st.markdown(f"<div style='text-align: right; background-color: #dcf8c6; padding: 10px; border-radius: 10px; margin: 5px; width: fit-content; max-width: 70%; margin-left: auto; word-wrap: break-word; overflow-wrap: break-word;'>"
#                                 f"{chat['message']}</div>", unsafe_allow_html=True)
#                 else:
#                     st.markdown(f"<div style='text-align: left; background-color: #e8e8e8; padding: 10px; border-radius: 10px; margin: 5px; width: fit-content; max-width: 70%; margin-right: auto; word-wrap: break-word; overflow-wrap: break-word;'>"
#                                 f"{chat['message']}</div>", unsafe_allow_html=True)

#     # **Show Processing Spinner if Waiting for Response**
#     if st.session_state.waiting_for_response:
#         with st.spinner("Processing..."):
#             last_message = st.session_state.chat_history[-1]
#             if last_message["role"] == "user":  # Ensure only processing user messages
#                 with st.empty():  # Placeholder for real-time updating
#                     bot_response = ""
#                     for chunk in get_bot_response(last_message["message"]):
#                         bot_response = chunk  # Update message dynamically
#                         st.markdown(f"<div style='text-align: left; background-color: #e8e8e8; padding: 10px; border-radius: 10px; margin: 5px; width: fit-content; max-width: 70%; margin-right: auto; word-wrap: break-word; overflow-wrap: break-word;'>"
#                                     f"{bot_response}</div>", unsafe_allow_html=True)
#                         # time.sleep(0.01)  # Simulate typing effect

#                 # Append final bot response to chat history
#                 st.session_state.chat_history.append({"role": "bot", "message": bot_response})
#                 st.session_state.waiting_for_response = False
#                 st.rerun()

#     # **Handle chat input submission after first message**
#     if user_input and user_input.strip():
#         st.session_state.chat_history.append({"role": "user", "message": user_input})
#         st.session_state.waiting_for_response = True
#         st.rerun()









