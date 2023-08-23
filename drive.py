from __future__ import print_function
import os.path
import json
import time  # Add time module for rate limiting
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/admin.reports.audit.readonly']

def main():
    """Shows basic usage of the Admin SDK Reports API.
    Prints all available fields for Google Drive activity logs in the domain.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('admin', 'reports_v1', credentials=creds)

    # Call the Admin SDK Reports API
    print('Getting all Drive activity logs')

    drive_logs = []

    next_page_token = None
    while True:
        try:
            results = service.activities().list(
                userKey='all',
                applicationName='drive',
                maxResults=500,  # Adjust maxResults as needed
                pageToken=next_page_token
            ).execute()
            activities = results.get('items', [])

            if not activities:
                break

            for activity in activities:
                drive_event = {
                    'time': activity['id']['time'],
                    'event': activity['events'][0]
                }
                drive_logs.append(drive_event)
                print(json.dumps(drive_event, indent=4))  # Print the entire event

            next_page_token = results.get('nextPageToken')
            if not next_page_token:
                break

            # Add a delay to avoid hitting rate limits too quickly
            time.sleep(5)  # You can adjust the sleep duration as needed

        except Exception as e:
            print(f"An error occurred: {e}")
            break

    # Save Google Drive activity logs to a JSON file
    with open('drive_events.json', 'w') as json_file:
        json.dump(drive_logs, json_file, indent=4)

if __name__ == '__main__':
    main()
