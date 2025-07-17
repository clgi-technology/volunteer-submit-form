import os
import sys
import yaml
import clicksend_client
from clicksend_client import SMSApi, SmsMessage, SmsMessageCollection
from clicksend_client.rest import ApiException

SCHEDULE_YAML = 'volunteer_input.yaml'

def send_sms(to_phone, message_body):
    username = os.getenv('CLICKSEND_USERNAME')
    api_key = os.getenv('CLICKSEND_API_KEY')

    if not username or not api_key:
        print("Missing CLICKSEND_USERNAME or CLICKSEND_API_KEY environment variables.")
        sys.exit(1)

    configuration = clicksend_client.Configuration()
    configuration.username = username
    configuration.password = api_key
    sms_api = SMSApi(clicksend_client.ApiClient(configuration))

    sms = SmsMessage(
        source="python",
        body=message_body,
        to=to_phone
    )

    sms_collection = SmsMessageCollection(messages=[sms])
    try:
        response = sms_api.sms_send_post(sms_collection)
        print(f"SMS sent successfully to {to_phone}: {response}")
    except ApiException as e:
        print(f"Failed to send SMS to {to_phone}: {e}")

def send_bulk_sms():
    try:
        with open(SCHEDULE_YAML, 'r') as f:
            volunteers = yaml.safe_load(f) or []
    except FileNotFoundError:
        print(f"{SCHEDULE_YAML} not found. Nothing to send.")
        return

    for vol in volunteers:
        if vol.get('notify_sms') and vol.get('phone'):
            phone = vol['phone']
            name = vol.get('name', 'Volunteer')
            message = f"Hi {name}, thank you for signing up to volunteer! We'll remind you of your shifts soon."
            send_sms(phone, message)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        # CLI mode for sending one SMS
        phone_number = sys.argv[1]
        name = sys.argv[2]
        message = f"Hi {name}, thank you for signing up to volunteer! We'll remind you of your shifts soon."
        send_sms(phone_number, message)
    else:
        # Bulk mode: send SMS to all volunteers who requested notification
        send_bulk_sms()
