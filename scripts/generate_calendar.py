import yaml
import json

SCHEDULE_FILE = 'volunteer_input.yaml'
CALENDAR_HTML = 'docs/calendar.html'
JSON_FILE = 'docs/volunteer_schedule.json'

def load_schedule():
    with open(SCHEDULE_FILE, 'r') as f:
        return yaml.safe_load(f) or []

def generate_json(schedule):
    entries = []
    for volunteer in schedule:
        name = volunteer.get('volunteer_name') or volunteer.get('name', '')
        for shift in volunteer.get('shifts', []):
            entries.append({
                'date': shift['date'],
                'time': shift['time'],
                'volunteer': name,
                'role': shift.get('role') or shift.get('position_title', ''),
                'event': shift.get('event') or ""
            })
    return entries

def generate_html(entries):
    roles = sorted(set(e['role'] for e in entries if e['role']))
    roles_options = '\n'.join(f'<option value="{r}">{r}</option>' for r in roles)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Volunteer Schedule Calendar</title>
<style>
  body {{ font-family: Arial, sans-serif; padding: 1em; background: #f9f9f9; }}
  h1 {{ text-align: center; color: #333; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 1em; }}
  th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
  th {{ background-color: #28a745; color: white; }}
  tr:nth-child(even) {{ background-color: #f2f2f2; }}
  select, input[type="date"] {{ margin: 0 0.5em 1em 0; padding: 0.5em; font-size: 1em; }}
  .filters {{ text-align: center; margin-bottom: 1em; }}
  .back-link {{ text-align: center; margin-top: 2em; }}
</style>
</head>
<body>

<h1>Volunteer Schedule Calendar</h1>

<div class="filters">
  <label for="date-filter">Filter by Date:</label>
  <input type="date" id="date-filter" onchange="filterCalendar()" />

  <label for="role-filter">Filter by Role:</label>
  <select id="role-filter" onchange="filterCalendar()">
    <option value="All">All</option>
    {roles_options}
  </select>
</div>

<table>
  <thead>
    <tr>
      <th>Date (Event)</th>
      <th>Time</th>
      <th>Volunteer</th>
      <th>Role</th>
    </tr>
  </thead>
  <tbody id="calendar-body"></tbody>
</table>

<div class="back-link">
  <a href="index.html">← Back to Sign-Up Page</a>
</div>

<script>
let volunteerData = {json.dumps(entries)};

function renderCalendar(data) {{
  const tableBody = document.getElementById('calendar-body');
  tableBody.innerHTML = '';
  data.forEach(entry => {{
    const eventPart = entry.event ? ` (${{
      entry.event
    }})` : '';
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${{entry.date}}${{eventPart}}</td>
      <td>${{entry.time}}</td>
      <td>${{entry.volunteer}}</td>
      <td>${{entry.role}}</td>
    `;
    tableBody.appendChild(row);
  }});
}}

function filterCalendar() {{
  const selectedRole = document.getElementById('role-filter').value;
  const selectedDate = document.getElementById('date-filter').value;

  let filtered = volunteerData;

  if (selectedRole !== 'All') {{
    filtered = filtered.filter(e => e.role === selectedRole);
  }}

  if (selectedDate) {{
    filtered = filtered.filter(e => e.date === selectedDate);
  }}

  renderCalendar(filtered);
}}

window.onload = () => renderCalendar(volunteerData);
</script>

</body>
</html>"""
    return html

def main():
    schedule = load_schedule()
    entries = generate_json(schedule)

    with open(JSON_FILE, 'w') as jf:
        json.dump(entries, jf, indent=2)

    with open(CALENDAR_HTML, 'w') as hf:
        hf.write(generate_html(entries))

if __name__ == '__main__':
    main()
