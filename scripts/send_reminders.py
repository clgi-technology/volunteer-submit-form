import os
import yaml
from datetime import datetime, timedelta
import clicksend_client
from clicksend_client import SMSApi, SmsMessage, SmsMessageCollection
from clicksend_client.rest import ApiException

# Load volunteer data
with open("volunteer_input.yaml", "r") as f:
    volunteers = yaml.safe_load(f) or []

# Current UTC time rounded to minute + 1 hour (the reminder time)
now = datetime.utcnow().replace(second=0, microsecond=0)
reminder_time = now + timedelta(hours=1)

# Initialize ClickSend API client
configuration = clicksend_client.Configuration()
configuration.username = os.getenv('CLICKSEND_USERNAME')
configuration.password = os.getenv('CLICKSEND_API_KEY')
sms_api = SMSApi(clicksend_client.ApiClient(configuration))

def send_sms(to_phone, message_body):
    sms = SmsMessage(source="python", body=message_body, to=to_phone)
    sms_collection = SmsMessageCollection(messages=[sms])
    try:
        response = sms_api.sms_send_post(sms_collection)
        print(f"✅ SMS sent to {to_phone}: {response}")
    except ApiException as e:
        print(f"❌ Failed to send SMS to {to_phone}: {e}")

for volunteer in volunteers:
    name = volunteer.get("name", "Volunteer")
    phone = str(volunteer.get("phone", "") or "").strip()  # handles None, int, or missing
    shifts = volunteer.get("shifts", [])
    wants_sms = volunteer.get("notify_sms", False)

    if not phone or not wants_sms:
        print(f"ℹ️ Skipping {name} — no SMS notification requested or phone number missing.")
        continue

    for shift in shifts:
        try:
            shift_datetime = datetime.strptime(f"{shift['date']} {shift['time']}", "%Y-%m-%d %H:%M")
        except Exception as e:
            print(f"⚠️ Skipping shift with bad format: {shift} ({e})")
            continue

        if shift_datetime == reminder_time:
            message = (
                f"Hi {name}, reminder: your volunteer shift as {shift['role']} "
                f"starts at {shift['time']} on {shift['date']}."
            )
            send_sms(phone, message)
