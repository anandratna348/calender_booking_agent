import streamlit as st
import requests
import webbrowser

st.set_page_config(page_title="Calendar Booking Assistant")
st.title("Calendar Booking Assistant")

# -- Session State Initialization --
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -- Check Login Status --
login_status = requests.get("http://localhost:8000/is_logged_in").json()
logged_in = login_status.get("logged_in", False)

# -- Login Prompt or Confirmation --
if not logged_in:
    st.markdown("### 🔐 Authorization Required")
    if st.button("Login with Google Calendar", key="login_button"):
        webbrowser.open_new_tab("http://localhost:8000/authorize")
        st.info("Login window opened. Complete Google authorization.")
else:
    st.success("You are logged in with Google Calendar!")

st.markdown("---")

# -- Chat Input --
user_input = st.chat_input("Ask me to book something...", key="chat_box")

if user_input:
    try:
        res = requests.post("http://localhost:8000/chat", json={"message": user_input})
        response = res.json()["response"]
    except Exception as e:
        response = f"Error: {e}"
    st.session_state.chat_history.append((user_input, response))

# -- Display Chat History --
for user, bot in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(user)
    with st.chat_message("assistant"):
        st.markdown(bot)
