Excellent — here’s your full project foundation for the new repo volunteer-submit-form, including:

⸻

📦 Repo Structure

volunteer-submit-form/
├── .github/
│   └── workflows/
│       └── handle-dispatch.yml
├── scripts/
│   ├── process_submission.py
│   └── send_clicksend_sms.py
├── volunteer_input.yaml
├── generate_calendar.py  # optional for future
├── README.md
└── requirements.txt


⸻

✅ Tally Form Template

Here’s a structure to build in Tally.so:

Field	Type	Required	Notes
Volunteer Name	Short Text	✅	
Event Name	Short Text	✅	
Position Title	Dropdown	✅	(e.g., Usher, Greeter, Organizer)
Date	Date	✅	
Time	Time	✅	
Year	Dropdown or Short Text	✅	2025, 2026, etc.
Phone Number	Phone	❌	Used only for SMS reminders
Email Address	Email	❌	Used only for optional email alerts
Notify by SMS?	Checkbox	❌	If checked, will send via ClickSend


⸻

🔁 Tally Webhook Settings

Webhook URL (GitHub Dispatch):

https://api.github.com/repos/<your-username>/volunteer-submit-form/dispatches

Headers:

Authorization: Bearer <your-GitHub-PAT>
Content-Type: application/json
Accept: application/vnd.github.everest-preview+json

Payload Template:

{
  "event_type": "volunteer_submission",
  "client_payload": {
    "volunteer_name": "@Volunteer Name",
    "event_name": "@Event Name",
    "position_title": "@Position Title",
    "date": "@Date",
    "year": "@Year",
    "time": "@Time",
    "phone": "@Phone Number",
    "email": "@Email Address",
    "notify_sms": "@Notify by SMS?"
  }
}


⸻

🔧 GitHub Action: .github/workflows/handle-dispatch.yml

name: Handle Volunteer Submission

on:
  repository_dispatch:
    types: [volunteer_submission]

jobs:
  append-entry:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repo
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install pyyaml requests

      - name: Save and process submission
        run: |
          echo '${{ toJSON(github.event.client_payload) }}' > payload.json
          python scripts/process_submission.py payload.json

      - name: Commit changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add volunteer_input.yaml
          git commit -m "Add new volunteer entry"
          git push

      - name: Send SMS via ClickSend
        if: ${{ github.event.client_payload.notify_sms == 'true' }}
        run: python scripts/send_clicksend_sms.py payload.json
        env:
          CLICKSEND_USERNAME: ${{ secrets.CLICKSEND_USERNAME }}
          CLICKSEND_API_KEY: ${{ secrets.CLICKSEND_API_KEY }}


⸻

🐍 scripts/process_submission.py

import sys
import json
import yaml

with open(sys.argv[1], 'r') as f:
    payload = json.load(f)

entry = {
    "volunteer_name": payload["volunteer_name"],
    "event_name": payload["event_name"],
    "position_title": payload["position_title"],
    "date": payload["date"],
    "year": payload["year"],
    "time": payload["time"],
    "phone": payload.get("phone"),
    "email": payload.get("email")
}

file_path = "volunteer_input.yaml"

try:
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f) or []
except FileNotFoundError:
    data = []

data.append(entry)

with open(file_path, 'w') as f:
    yaml.dump(data, f)


⸻

📲 scripts/send_clicksend_sms.py

import sys
import json
import os
import requests

with open(sys.argv[1], 'r') as f:
    payload = json.load(f)

phone = payload.get("phone")
if not phone:
    print("No phone number provided.")
    exit(0)

message = f"""Hi {payload['volunteer_name']}, you're confirmed for:
Event: {payload['event_name']}
Position: {payload['position_title']}
Date: {payload['date']} {payload['year']} at {payload['time']}
"""

response = requests.post(
    "https://rest.clicksend.com/v3/sms/send",
    auth=(os.environ["CLICKSEND_USERNAME"], os.environ["CLICKSEND_API_KEY"]),
    headers={"Content-Type": "application/json"},
    json={
        "messages": [{
            "to": phone,
            "body": message
        }]
    }
)

print("ClickSend response:", response.text)


⸻

📄 requirements.txt

pyyaml
requests


⸻

📘 README.md

# 🙌 Volunteer Submit Form

This project collects volunteer shift availability using a no-login **Tally form**, and processes submissions automatically via **GitHub Actions**. Optional SMS reminders are sent using ClickSend.

---

## 🚀 How It Works

1. Volunteer fills out a form (Tally)
2. Tally sends data via webhook to GitHub
3. GitHub Action:
   - Appends to `volunteer_input.yaml`
   - Sends optional SMS reminder
   - (Optional) Generates calendar or dashboard

---

## 📋 Fields Collected

- Volunteer Name
- Event Name
- Position Title
- Date
- Year
- Time
- Phone (optional, for SMS)
- Email (optional)
- Checkbox: Send SMS Reminder?

---

## 🔧 Setup

### 1. Create GitHub PAT
With `repo` + `workflow` scope.

### 2. Add GitHub Secrets
| Name | Description |
|------|-------------|
| `CLICKSEND_USERNAME` | ClickSend account username |
| `CLICKSEND_API_KEY`  | ClickSend API key |

### 3. Configure Tally Webhook
Use your repo’s dispatch URL with Authorization and JSON payload.

---

## 📄 Data Format (`volunteer_input.yaml`)

```
yaml
- volunteer_name: Alice
  event_name: Community Cleanup
  position_title: Organizer
  date: 2025-08-01
  year: 2025
  time: 10:00 AM
  phone: +15551234567
  email: alice@example.com
```

⸻

✅ Future Enhancements
	•	Email confirmations
	•	Admin dashboard
	•	iCal or Google Calendar exports

⸻

📄 License

MIT License

---

Here’s a fully scaffolded setup that you can create in your new volunteer-submit-form GitHub repo. You can copy-paste the content into your files:

⸻

📁 Repository Structure

```
volunteer-submit-form/
├── .github/
│   └── workflows/
│       └── handle-dispatch.yml
├── scripts/
│   ├── process_submission.py
│   └── send_clicksend_sms.py
├── volunteer_input.yaml
├── requirements.txt
└── README.md
```

⸻

```
🔧 1. .github/workflows/handle-dispatch.yml

name: Handle Volunteer Submission

on:
  repository_dispatch:
    types: [volunteer_submission]

jobs:
  append-entry:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - run: pip install pyyaml requests
        name: Install dependencies

      - name: Save and process submission
        run: |
          echo '${{ toJSON(github.event.client_payload) }}' > payload.json
          python scripts/process_submission.py payload.json

      - name: Commit changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add volunteer_input.yaml
          git commit -m "Add new volunteer entry" || echo "No changes to commit"
          git push

      - name: Send SMS via ClickSend
        if: ${{ github.event.client_payload.notify_sms == 'true' }}
        run: python scripts/send_clicksend_sms.py payload.json
        env:
          CLICKSEND_USERNAME: ${{ secrets.CLICKSEND_USERNAME }}
          CLICKSEND_API_KEY: ${{ secrets.CLICKSEND_API_KEY }}

```
⸻

🔧 2. scripts/process_submission.py

```
import sys, json, yaml

with open(sys.argv[1], 'r') as f:
    payload = json.load(f)

entry = {
    "volunteer_name": payload.get("volunteer_name"),
    "event_name": payload.get("event_name"),
    "position_title": payload.get("position_title"),
    "date": payload.get("date"),
    "year": payload.get("year"),
    "time": payload.get("time"),
    "phone": payload.get("phone"),
    "email": payload.get("email")
}

file_path = "volunteer_input.yaml"
try:
    existing = yaml.safe_load(open(file_path)) or []
except FileNotFoundError:
    existing = []

existing.append(entry)

with open(file_path, 'w') as f:
    yaml.dump(existing, f)

```
⸻

🔧 3. scripts/send_clicksend_sms.py

```
import sys, json, os, requests

with open(sys.argv[1], 'r') as f:
    payload = json.load(f)

phone = payload.get("phone")
if not phone:
    print("❗ No phone number provided. Skipping SMS.")
    sys.exit(0)

message = (
    f"Hi {payload['volunteer_name']}, you’re confirmed:\n"
    f"{payload['event_name']} – {payload['position_title']} on {payload['date']} "
    f"{payload['year']} at {payload['time']}."
)

response = requests.post(
    "https://rest.clicksend.com/v3/sms/send",
    auth=(os.environ["CLICKSEND_USERNAME"], os.environ["CLICKSEND_API_KEY"]),
    headers={"Content-Type": "application/json"},
    json={"messages": [{"to": phone, "body": message}]}
)

print("ClickSend response:", response.text)

```
⸻

🧹 4. volunteer_input.yaml
```

Start with an empty YAML array:

[]

```
⸻

📦 5. requirements.txt

```
pyyaml
requests

```
⸻

📘 6. README.md

# 🙌 Volunteer Submit Form

Collect volunteer submissions via a no‑login **Tally form**, processed server‑side by **GitHub Actions**. Optional SMS reminders are sent via **ClickSend**.

---

## 🚀 How It Works

1. Volunteer submits your Tally form.
2. Tally sends a webhook payload to the GitHub API.
3. GitHub Action appends data to `volunteer_input.yaml` and optionally sends an SMS.
4. (Optional) Later, use this data to build a calendar or admin UI.

---

## 📋 Fields Collected

- Volunteer Name
- Event Name
- Position Title
- Date, Year, Time
- [Optional] Phone (for SMS reminders)
- [Optional] Email
- Checkbox: Send SMS Reminder?

---

## 🔧 Setup

1. **Create a GitHub PAT** with `repo` + `workflow` scopes.
2. In GitHub repo settings → **Secrets**, add:
   - `CLICKSEND_USERNAME`
   - `CLICKSEND_API_KEY`
3. **Create your Tally form** and configure the webhook:
   - POST to:
     ```
     https://api.github.com/repos/<you>/volunteer-submit-form/dispatches
     ```
   - Headers:
     ```
     Authorization: Bearer <your‑PAT>
     Content-Type: application/json
     Accept: application/vnd.github.everest-preview+json
     ```
   - Payload:
     ```json
     {
       "event_type": "volunteer_submission",
       "client_payload": {
         "volunteer_name": "@Volunteer Name",
         "event_name": "@Event Name",
         "position_title": "@Position Title",
         "date": "@Date",
         "year": "@Year",
         "time": "@Time",
         "phone": "@Phone Number",
         "email": "@Email Address",
         "notify_sms": "@Notify by SMS?"
       }
     }
     ```
4. Submit a test via Tally — check GitHub Actions run, and see a new entry appear in `volunteer_input.yaml`.

---

## ✅ Next Steps

- Build calendar/dashboard (e.g., with `generate_calendar.py`)
- Add email confirmations
- Create administrative dashboard
- Export iCal or integrate with Google Calendar

---

## 📝 License

This project is released under the MIT License.


⸻

✅ Next Actions for You
	•	Copy this scaffolding into your GitHub repo
	•	Create your Tally form with the specified fields
	•	Configure the webhook URL and headers
	•	Add GitHub secrets (CLICKSEND_USERNAME, CLICKSEND_API_KEY)
	•	Submit a test and verify the Action runs and appends data

⸻

Would you like help generating the Tally form link or assistance adding calendar generation in the next step?
