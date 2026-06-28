import csv
import os
from datetime import datetime

LOG_PATH = "logs/IT_Audit_Log.csv"
HEADERS = ["Timestamp", "Action", "Status", "Ticket_ID", "Actor", "Target", "Notes"]

def log_action(action, status, ticket_id, actor, target, notes=""):
    os.makedirs("logs", exist_ok=True)
    file_exists = os.path.isfile(LOG_PATH)
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
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


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Log actions to the audit log.")
    parser.add_argument("--action", required=True, help="Action performed")
    parser.add_argument("--status", required=True, help="Status of the action")
    parser.add_argument("--ticket", required=True, help="Ticket ID")
    parser.add_argument("--actor", required=True, help="Actor performing the action")
    parser.add_argument("--target", required=True, help="Target of the action")
    parser.add_argument("--notes", default="", help="Optional notes")
    args = parser.parse_args()
    
    log_action(
        action=args.action,
        status=args.status,
        ticket_id=args.ticket,
        actor=args.actor,
        target=args.target,
        notes=args.notes
    )

