import streamlit as st
import requests

# Backend URL for deployed API
BACKEND_API_URL = "https://calender-booking-agent-8ecg.onrender.com"

st.set_page_config(page_title="Calendar Booking Assistant")
st.title("Calendar Booking Assistant")

# -- Session State Initialization --
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -- Check Login Status --
try:
    login_status = requests.get(f"{BACKEND_API_URL}/is_logged_in").json()
    logged_in = login_status.get("logged_in", False)
except Exception as e:
    st.error("❌ Unable to connect to backend.")
    st.stop()

# -- Login / Logout Logic --
if not logged_in:
    st.markdown("### 🔐 Authorization Required")

    # Login button with styled HTML link
    login_url = f"{BACKEND_API_URL}/authorize"
    st.markdown(
        f"""
        <a href="{login_url}" target="_blank">
            <button style="padding:10px 20px; font-size:16px;">Login with Google Calendar</button>
        </a>
        """,
        unsafe_allow_html=True
    )

    # Manual check after user logs in on new tab
    if st.button("✅ I have logged in"):
        try:
            login_status = requests.get(f"{BACKEND_API_URL}/is_logged_in").json()
            logged_in = login_status.get("logged_in", False)
            if logged_in:
                st.success("🎉 Logged in successfully!")
                st.experimental_rerun()
            else:
                st.warning("⚠️ Still not logged in. Complete login in the opened tab.")
        except:
            st.error("❌ Could not verify login status.")
else:
    st.success("✅ You are logged in with Google Calendar!")

    # Logout button
    if st.button("Logout"):
        try:
            response = requests.get(f"{BACKEND_API_URL}/logout")
            if response.ok:
                st.success("🔓 Logged out successfully.")
                st.session_state.chat_history = []
                st.experimental_rerun()
            else:
                st.error("❌ Logout failed.")
        except Exception as e:
            st.error(f"Error during logout: {e}")

st.markdown("---")

# -- Chat Input --
user_input = st.chat_input("Ask me to book something...", key="chat_box")

if user_input:
    try:
        res = requests.post(f"{BACKEND_API_URL}/chat", json={"message": user_input})
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
