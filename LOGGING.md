# Logging and Audit Rules

All scripts must log every action to `logs/IT_Audit_Log.csv`.  
Health and connectivity checks also write to `logs/health_checks.csv`.  
Use the shared `scripts/logger.py` module — do not write CSV rows manually.

-----

## IT_Audit_Log.csv Schema

|Column       |Description                             |Example                        |
|-------------|----------------------------------------|-------------------------------|
|**Timestamp**|ISO format — auto-generated             |2026-05-27T09:14:32            |
|**Action**   |Short string describing what was done   |ProvisionUser                  |
|**Status**   |success / failure / simulated           |success                        |
|**Ticket_ID**|ServiceNow INC number or placeholder    |INC0012345                     |
|**Actor**    |Manual or script filename               |provision_user.py              |
|**Target**   |User, hostname, IP, or domain           |sarah.blake                    |
|**Notes**    |Evidence path, error message, or context|AD object created in corp.local|

-----

## Health_Checks.csv Schema

|Column          |Description                         |Example                        |
|----------------|------------------------------------|-------------------------------|
|**Timestamp**   |ISO format                          |2026-05-27T09:20:11            |
|**Check**       |Type of check                       |ping                           |
|**Target**      |IP or FQDN                          |192.168.128.130                |
|**Result**      |ok / fail                           |ok                             |
|**EvidencePath**|Path to saved output file or snippet|logs/evidence/ping_20260527.txt|

-----

## Rules

1. **Every task gets a log row.** If you did it manually, log it manually using the logger script — pass in `actor = Manual`
1. **Every log row needs a Ticket_ID.** Open a ServiceNow Incident first, get the ID, then run the script
1. **Save evidence for connectivity and health checks.** Save at least the first 200 characters of stdout to a file in `logs/evidence/`
1. **Do not edit the CSV directly.** Always go through the logger script
1. **Weekly review.** Open `IT_Audit_Log.csv` in Excel once a week — check your task completion rate and that no rows have missing fields

-----

## Log Rotation

At the end of each month, move that month’s logs to `logs/archive/YYYY-MM/`.  
Start a fresh `IT_Audit_Log.csv` for the new month.  
The archive folder should be committed to GitHub so you have a full history.

-----

## Example Logger Script (scripts/logger.py)

```python
import csv
import os
from datetime import datetime

LOG_PATH = "logs/IT_Audit_Log.csv"
HEADERS = ["Timestamp", "Action", "Status", "Ticket_ID", "Actor", "Target", "Notes"]

def log_action(action, status, ticket_id, actor, target, notes=""):
    os.makedirs("logs", exist_ok=True)
    file_exists = os.path.isfile(LOG_PATH)
    with open(LOG_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "Timestamp": datetime.now().isoformat(timespec="seconds"),
            "Action": action,
            "Status": status,
            "Ticket_ID": ticket_id,
            "Actor": actor,
            "Target": target,
            "Notes": notes
        })
    print(f"[LOGGED] {action} | {status} | {target}")
```

Copy this into `scripts/logger.py` and import it in every other script:

```python
from scripts.logger import log_action
```