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
