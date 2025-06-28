import os
import pickle
import json
from datetime import datetime, timedelta
from fastapi import Request as FastAPIRequest
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

# Constants
SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_FILE = "app/token.pickle"  # You can change this path
TIMEZONE = 'Asia/Kolkata'

def get_calendar_service():
    creds = None

    # Load token if exists
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # Refresh or re-authenticate if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_config = json.loads(os.environ["GOOGLE_CLIENT_SECRET_JSON"])
            flow = Flow.from_client_config(
                client_config,
                scopes=SCOPES,
                redirect_uri=os.environ["REDIRECT_URI"]
            )
            auth_url, _ = flow.authorization_url(prompt='consent')
            print(f"Please visit this URL to authorize: {auth_url}")
            raise Exception("Authorization required. Please complete OAuth first.")

        # Save new credentials
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)

def check_availability(start_time: str, end_time: str) -> bool:
    service = get_calendar_service()
    events = service.events().list(
        calendarId='primary',
        timeMin=start_time,
        timeMax=end_time,
        singleEvents=True,
        orderBy='startTime'
    ).execute().get('items', [])
    return len(events) == 0

def book_meeting(start_time: str, end_time: str, summary="AI Scheduled Meeting"):
    service = get_calendar_service()
    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': TIMEZONE},
        'end': {'dateTime': end_time, 'timeZone': TIMEZONE},
    }
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return f"Event created: {created_event.get('htmlLink')}"

def force_login():
    client_config = json.loads(os.environ["GOOGLE_CLIENT_SECRET_JSON"])
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=os.environ["REDIRECT_URI"]
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    return auth_url

def handle_callback(request: FastAPIRequest):
    client_config = json.loads(os.environ["GOOGLE_CLIENT_SECRET_JSON"])
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=os.environ["REDIRECT_URI"]
    )
    flow.fetch_token(authorization_response=str(request.url))
    creds = flow.credentials

    # Save token for future use
    with open(TOKEN_FILE, 'wb') as token:
        pickle.dump(creds, token)

    return True
