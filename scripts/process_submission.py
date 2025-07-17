import sys
import argparse
import yaml
import json
import re
from datetime import datetime

SCHEDULE_YAML = 'volunteer_input.yaml'
SCHEDULE_JSON = 'docs/volunteer_schedule.json'

def load_schedule():
    try:
        with open(SCHEDULE_YAML, 'r') as f:
            data = yaml.safe_load(f)
            return data if data else []
    except FileNotFoundError:
        return []

def save_schedule(schedule):
    with open(SCHEDULE_YAML, 'w') as f:
        yaml.safe_dump(schedule, f, sort_keys=False)

def export_json(schedule):
    json_data = []
    for vol in schedule:
        for shift in vol.get('shifts', []):
            json_data.append({
                "date": shift.get('date'),
                "time": shift.get('time'),
                "volunteer": vol.get('name'),
                "role": shift.get('role')
            })
    with open(SCHEDULE_JSON, 'w') as f:
        json.dump(json_data, f, indent=2)

def parse_payload(payload):
    name = payload.get('volunteer_name') or payload.get('name') or ""
    phone = payload.get('phone') or ""
    notify_sms = str(payload.get('notify_sms', '')).lower() in ('true', 'yes', '1')

    date = payload.get('date') or ""
    time = payload.get('time') or ""
    role = payload.get('position_title') or ""

    if not (name and date and time and role):
        print("⚠️ Payload content:", payload)
        sys.exit("❌ Missing required volunteer or shift data in payload.")

    shifts = [{
        'date': date,
        'time': time,
        'role': role
    }]
    return name, phone, notify_sms, shifts

def main():
    parser = argparse.ArgumentParser(description="Process volunteer submission")
    parser.add_argument('--payload-json', type=str, help="Path to JSON payload file")
    parser.add_argument('--name', type=str, help="Volunteer name (fallback)")
    parser.add_argument('--phone', type=str, help="Phone number (fallback)")
    parser.add_argument('--shifts', type=str, nargs='*', help="Shifts (fallback)")
    parser.add_argument('--notify-sms', action='store_true', help="Send SMS notification")
    args = parser.parse_args()

    if args.payload_json:
        try:
            with open(args.payload_json, 'r') as f:
                payload = json.load(f)
        except Exception as e:
            sys.exit(f"❌ Failed to load JSON payload: {e}")
        name, phone, notify_sms, shifts = parse_payload(payload)

    elif args.name and args.shifts:
        name = args.name.strip()
        phone = (args.phone or "").strip()
        notify_sms = args.notify_sms
        shifts = []
        for shift_line in args.shifts:
            shifts.extend(parse_shifts([shift_line]))
    else:
        sys.exit("❌ Must provide either --payload-json or --name and --shifts")

    schedule = load_schedule()
    schedule = [v for v in schedule if not (v.get('name') == name and v.get('phone') == phone)]

    new_volunteer = {
        'name': name,
        'phone': phone,
        'shifts': shifts
    }
    if notify_sms:
        new_volunteer['notify_sms'] = True

    schedule.append(new_volunteer)
    save_schedule(schedule)
    export_json(schedule)

    print(f"✅ Recorded {name} with {len(shifts)} shift(s).")

if __name__ == "__main__":
    main()
