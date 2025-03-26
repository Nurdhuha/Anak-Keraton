import streamlit as st

# Title of the app
st.title("Chat with Doctor")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Input field for user to type messages
user_input = st.text_input("You:", key="user_input")

# Display chat messages from session state
for message in st.session_state.messages:
    if message["user"] == "user":
        st.markdown(f"**You:** {message['text']}")
    else:
        st.markdown(f"**Doctor:** {message['text']}")

# Define a simple doctor response function
def get_doctor_response(user_message):
    # In a real application, you would have a more complex logic here
    return "I'm sorry, but I can't give medical advice. Please consult a licensed healthcare professional."

# When user submits a message
if st.button("Send"):
    if user_input:
        # Add user message to session state
        st.session_state.messages.append({"user": "user", "text": user_input})
        
        # Get doctor's response
        doctor_response = get_doctor_response(user_input)
        
        # Add doctor's response to session state
        st.session_state.messages.append({"user": "doctor", "text": doctor_response})
        
        # Clear the input field
        st.session_state.user_input = ""
