import sys
import argparse
import yaml
import json
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

    shifts = []

    # Preferred: structured shifts list
    if 'shifts' in payload and isinstance(payload['shifts'], list):
        for s in payload['shifts']:
            date = s.get('date')
            time = s.get('time')
            role = s.get('role') or s.get('position_title')
            if date and time and role:
                shifts.append({'date': date, 'time': time, 'role': role})

    else:
        # Fallback: single shift
        date = payload.get('date')
        time = payload.get('time')
        roles = payload.get('position_title')

        if isinstance(roles, str):
            roles = [r.strip() for r in roles.split(',') if r.strip()]
        elif not isinstance(roles, list):
            roles = []

        for role in roles:
            if date and time and role:
                shifts.append({'date': date, 'time': time, 'role': role})

    if not (name and shifts):
        sys.exit("❌ Missing required volunteer name or shift data.")

    return name, phone, notify_sms, shifts

def main():
    parser = argparse.ArgumentParser(description="Process volunteer submission")
    parser.add_argument('--payload-json', type=str, help="JSON payload string from webhook / dispatch")
    parser.add_argument('--name', type=str, help="Volunteer name (fallback)")
    parser.add_argument('--phone', type=str, help="Phone number (fallback)")
    parser.add_argument('--shifts', type=str, nargs='*', help="Shifts (fallback)")
    parser.add_argument('--notify-sms', action='store_true', help="Send SMS notification")
    args = parser.parse_args()

    if args.payload_json:
        try:
            payload = json.loads(args.payload_json)
        except json.JSONDecodeError:
            sys.exit("❌ Invalid JSON payload provided.")
        name, phone, notify_sms, shifts = parse_payload(payload)

    else:
        if not args.name or not args.shifts:
            sys.exit("❌ Missing required --name or --shifts")
        name = args.name.strip()
        phone = (args.phone or "").strip()
        notify_sms = args.notify_sms
        shifts = []
        for shift_line in args.shifts:
            try:
                date_part, rest = shift_line.split(',', 1)
                time_part, role_part = rest.split('–', 1)
                shifts.append({
                    'date': date_part.strip(),
                    'time': time_part.strip(),
                    'role': role_part.strip()
                })
            except ValueError:
                continue

    if not shifts:
        sys.exit("❌ No valid shifts found.")

    schedule = load_schedule()

    # Remove duplicates for same volunteer (optional logic)
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
