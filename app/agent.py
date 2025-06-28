import dateparser
from datetime import datetime, timedelta
from app.calender import check_availability, book_meeting

# Session memory
session_state = {
    "intent": None,
    "time_range": None,
    "confirmed": False,
    "last_booked": None
}

# Intent & time extractor
def extract_intent_and_time(user_input):
    intent = "book_meeting" if any(w in user_input.lower() for w in ["book", "schedule", "meeting", "call"]) else "check_availability"
    parsed_time = dateparser.parse(user_input)

    if not parsed_time:
        return intent, None

    time_range = {
        "start": parsed_time.isoformat(),
        "end": (parsed_time + timedelta(minutes=30)).isoformat()
    }
    return intent, time_range

# Core agent
def run_agent(user_input):
    global session_state

    # Handle confirmation
    if session_state["confirmed"] and session_state["time_range"]:
        if user_input.lower() in ["yes", "y", "confirm", "okay", "ok", "sure"]:
            start = datetime.fromisoformat(session_state["time_range"]["start"]).astimezone().isoformat()
            end = datetime.fromisoformat(session_state["time_range"]["end"]).astimezone().isoformat()

            if session_state["last_booked"] == (start, end):
                return "This meeting was already booked."

            booking_response = book_meeting(start, end)
            session_state = {
                "intent": None,
                "time_range": None,
                "confirmed": False,
                "last_booked": (start, end)
            }
            return booking_response

        elif user_input.lower() in ["no", "n", "cancel", "stop"]:
            session_state = {
                "intent": None,
                "time_range": None,
                "confirmed": False,
                "last_booked": session_state.get("last_booked")
            }
            return "Booking canceled. Let me know if you'd like to try another time."

        else:
            return "Please reply with 'yes' to confirm or 'no' to cancel."

    # Intent and time parsing
    intent, time_range = extract_intent_and_time(user_input)
    if intent:
        session_state["intent"] = intent
    if time_range:
        session_state["time_range"] = time_range

    if not session_state["time_range"]:
        return "I couldn't understand the time. Try something like 'tomorrow at 3pm'."

    # Check availability
    start = datetime.fromisoformat(session_state["time_range"]["start"]).astimezone().isoformat()
    end = datetime.fromisoformat(session_state["time_range"]["end"]).astimezone().isoformat()

    if not check_availability(start, end):
        return f"That time ({start} to {end}) is booked. Try another slot."

    session_state["confirmed"] = True
    return f"You're free from {start} to {end}. Should I book it?"
