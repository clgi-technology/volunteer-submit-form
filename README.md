# 🙌 Volunteer Submit Form

This project collects volunteer availability using a **free Tally form**, and processes each submission via a local `make` command that sends data directly to GitHub using the `repository_dispatch` API. GitHub Actions then appends the data to a YAML file, submits data to a calendar via github pages and (optionally) sends an SMS reminder using ClickSend.

---
## Directory Tree

```
Volunteer-Submit-Form/
├── .github/
│   └── workflows/
│       └── handle-dispatch.yml      # Handles repository_dispatch events from make / webhook
├── docs/
│   ├── calendar.html                # Generated calendar page, served via GitHub Pages
│   └── volunteer_schedule.json     # (optional) JSON data for calendar
├── scripts/
│   ├── process_submission.py       # Process and append submissions to volunteer_input.yaml
│   └── generate_calendar.py        # Generate calendar.html from volunteer_input.yaml
├── volunteer_input.yaml            # Stores volunteer data
├── Makefile                       # Command to send submission payload via curl
├── README.md                      # Docs and setup info
├── requirements.txt               # Python dependencies (PyYAML, requests, etc.)
└── .env                          # For local secrets (optional, not committed)


```

## 📒 Directory Tree Notes

- `.github/workflows/handle-dispatch.yml` — GitHub Action triggered by `repository_dispatch`
- `scripts/` — Python utilities that run inside the GitHub Action
- `examples/` — Holds test payloads for easy reuse or local testing
- `Makefile` — Sends form data to GitHub via `curl`
- `volunteer_input.yaml` — Appended file of all volunteer submissions

---
## 🚀 How It Works

1. A volunteer fills out the Tally form
2. A coordinator runs `make submit` with form data
3. This triggers a GitHub Action via `repository_dispatch`
4. The Action:
   - Appends data to `volunteer_input.yaml`
   - Optionally sends an SMS if enabled

---

## 📋 Form Fields (via Tally)

| **Field**           | **Type**               | **Required** | **Notes**                                              |
|---------------------|------------------------|--------------|--------------------------------------------------------|
| Volunteer Name      | Short Text             | ✅           |                                                        |
| Event Name          | Short Text             | ✅           |                                                        |
| Position Title      | Dropdown               | ✅           | e.g., Usher, Greeter, Organizer                        |
| Date                | Date                   | ✅           |                                                        |
| Time                | Time                   | ✅           |                                                        |
| Year                | Dropdown or Short Text | ✅           | e.g., 2025, 2026, etc.                                 |
| Phone Number        | Phone                  | ❌           | Used only for SMS reminders                            |
| Email Address       | Email                  | ❌           | Used only for optional email alerts                    |
| Notify by SMS?      | Checkbox               | ❌           | If checked, will trigger SMS via ClickSend             |

---

## 🔧 Setup Instructions

### 1. Clone This Repo

```bash
git clone https://github.com/<your-username>/volunteer-submit-form
cd volunteer-submit-form
```

### 2. Add Your GitHub Token
Create a GitHub Personal Access Token with repo and workflow scopes.

Set it in your environment:
```
export GITHUB_TOKEN=ghp_abc123yourtoken
```

### 3. Prepare payload.json
Manually create or generate payload.json with form data:

```json

{
  "event_type": "volunteer_submission",
  "client_payload": {
    "volunteer_name": "Alice Smith",
    "event_name": "Community Cleanup",
    "position_title": "Greeter",
    "date": "2025-08-01",
    "year": "2025",
    "time": "10:00 AM",
    "phone": "+15551234567",
    "email": "alice@example.com",
    "notify_sms": "true"
  }
}
```
You can write your own script to export this from a spreadsheet or YAML.

### 4. Use make to Submit
```
make submit
```
This will trigger the GitHub Action via curl using your token and the payload.json.


## 🧪 Makefile
```
submit:
	curl -X POST https://api.github.com/repos/<your-username>/volunteer-submit-form/dispatches \
	-H "Authorization: Bearer $(GITHUB_TOKEN)" \
	-H "Accept: application/vnd.github.everest-preview+json" \
	-H "Content-Type: application/json" \
	-d @payload.json

```
Replace <your-username> with your actual GitHub username or org.

## 🔄 GitHub Action
The .github/workflows/handle-dispatch.yml workflow:

Listens for repository_dispatch events

Appends data to volunteer_input.yaml

Sends SMS if enabled

See full script in .github/workflows/handle-dispatch.yml

## 📄 volunteer_input.yaml Format
```
- volunteer_name: Alice Smith
  event_name: Community Cleanup
  position_title: Greeter
  date: 2025-08-01
  year: 2025
  time: 10:00 AM
  phone: +15551234567
  email: alice@example.com

```
## 🔐 GitHub Secrets (for SMS)
| Name               | Description            |
|--------------------|------------------------|
| `CLICKSEND_USERNAME` | Your ClickSend username |
| `CLICKSEND_API_KEY`  | ClickSend API key       |


If SMS is not used, you can omit these.

## ✅ Next Steps

- [ ] Automate `payload.json` generation (from YAML or CSV)
- [ ] Add Google Calendar export
- [ ] Build dashboard UI (optional)
- [ ] Add form validation



## 📝 License
MIT License


