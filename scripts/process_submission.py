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

def parse_shifts(shift_lines):
    shifts = []
    # Expect shift lines as: "Saturday July 12, 2025, 11:15 PM – Livestream"
    pattern = re.compile(r"^(.*?),\s*(\d{1,2}:\d{2}\s*[APMapm\.]{2,4})\s*[-–—]\s*(.*)$")
    for line in shift_lines:
        m = pattern.match(line)
        if not m:
            continue
        date_str, time_str, role = m.groups()
        # Convert date to ISO format YYYY-MM-DD
        try:
            dt_date = datetime.strptime(date_str.strip(), "%A %B %d, %Y")
            date_fmt = dt_date.strftime("%Y-%m-%d")
        except ValueError:
            continue
        # Convert time to 24h HH:MM format
        try:
            dt_time = datetime.strptime(time_str.strip().replace('.', ''), "%I:%M %p")
            time_fmt = dt_time.strftime("%H:%M")
        except ValueError:
            continue
        shifts.append({
            'date': date_fmt,
            'time': time_fmt,
            'role': role.strip()
        })
    if not shifts:
        sys.exit("❌ No valid shifts parsed.")
    return shifts

def parse_payload(payload):
    # Payload fields from GitHub event client_payload
    # Expected keys: volunteer_name, event_name, position_title, date, time, year, phone, email, notify_sms
    # Convert to our internal structure
    name = payload.get('volunteer_name') or payload.get('name') or ""
    phone = payload.get('phone') or ""
    notify_sms = str(payload.get('notify_sms', '')).lower() in ('true', 'yes', '1')
    
    # Compose a single shift from payload fields
    date = payload.get('date') or ""
    time = payload.get('time') or ""
    role = payload.get('position_title') or ""

    if not (name and date and time and role):
        sys.exit("❌ Missing required volunteer or shift data in payload.")
    
    shifts = [{
        'date': date,
        'time': time,
        'role': role
    }]
    return name, phone, notify_sms, shifts

def main():
    parser = argparse.ArgumentParser(description="Process volunteer submission")
    parser.add_argument('--issue-body', type=str, help="Full issue body text")
    parser.add_argument('--payload-json', type=str, help="JSON payload string from webhook / dispatch")
    parser.add_argument('--name', type=str, help="Volunteer name (if no issue body or payload)")
    parser.add_argument('--phone', type=str, help="Phone number (if no issue body or payload)")
    parser.add_argument('--shifts', type=str, nargs='*', help="Shifts (if no issue body or payload)")
    parser.add_argument('--notify-sms', action='store_true', help="Send SMS notification")
    args = parser.parse_args()

    if args.issue_body:
        # parse old style issue body text (optional)
        # You can keep or remove this if not used
        print("⚠️ Warning: issue_body parsing is deprecated in this setup.")
        # Could call parse_issue_body here if implemented
        sys.exit("❌ Issue body parsing not implemented for this project.")
    
    elif args.payload_json:
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
            # Expecting the shift line in "Date, Time – Role" format
            shifts.extend(parse_shifts([shift_line]))

    schedule = load_schedule()
    # Remove any existing entries for this volunteer (match by name and phone)
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
