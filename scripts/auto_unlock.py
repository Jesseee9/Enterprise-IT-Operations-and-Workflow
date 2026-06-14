import argparse
import os
from datetime import datetime
from dotenv import load_dotenv
import winrm
from logger import log_action
from servicenow_api import create_servicenow_incident, resolve_incident

load_dotenv()

def get_locked_accounts(session):
    result = session.run_ps("Search-ADAccount -LockedOut | Select-Object -ExpandProperty SamAccountName")
    accounts = [a.strip() for a in result.std_out.decode().strip().splitlines() if a.strip()]
    return accounts

def unlock_account(session, username):
    result = session.run_ps(f"Unlock-ADAccount -Identity {username}")
    return result.status_code == 0

def main():
    parser = argparse.ArgumentParser(description="Auto Unlock Locked AD Accounts")
    parser.parse_args()

    server_ip = os.getenv("SERVER_IP", "192.168.10.10")
    admin_user = os.getenv("ADMIN_USER", "Administrator")
    admin_pass = os.getenv("ADMIN_PASS")

    if not admin_pass:
        print("[!] ERROR: ADMIN_PASS not set in .env")
        return

    session = winrm.Session(
        f"http://{server_ip}:5985/wsman",
        auth=(f"{admin_user}", admin_pass),
        transport="basic"
    )

    locked = get_locked_accounts(session)

    if not locked:
        print("No locked accounts found.")
        log_action("auto_unlock", "INFO", "N/A", "auto_unlock.py", "N/A", "No locked accounts found")
        return

    for username in locked:
        print(f"Found locked account: {username}")

        incident_number, sys_id = create_servicenow_incident(
            f"Account lockout detected: {username}",
            "Access",
            f"Auto-unlock script detected locked account {username} at {datetime.now()}"
        )

        success = unlock_account(session, username)

        if success:
            status = "Unlocked successfully"
            print(f"{username} — {status}")
        else:
            status = "Unlock failed"
            print(f"{username} — {status}")

        log_action("auto_unlock", "INFO", incident_number or "N/A", "auto_unlock.py", username, status)

        if incident_number:
            resolve_incident(sys_id, f"Account {username} {status} by auto_unlock.py")

if __name__ == "__main__":
    main()
