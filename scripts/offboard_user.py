import argparse
import os
from dotenv import load_dotenv
import winrm
from logger import log_action
from servicenow_api import create_servicenow_incident, resolve_incident

load_dotenv()

def offboard_user(username):
    print(f"[*] Starting offboarding for {username}")

    server_ip = os.getenv("SERVER_IP", "192.168.10.10")
    admin_user = os.getenv("ADMIN_USER", "Administrator")
    admin_pass = os.getenv("ADMIN_PASS")

    if not admin_pass:
        print("[!] ERROR: ADMIN_PASS not set in .env")
        return

    session = winrm.Session(
        f"http://{server_ip}:5985/wsman",
        auth=(admin_user, admin_pass),
        transport='basic'
    )

    # Disable account
    disable_cmd = f"Disable-ADAccount -Identity {username}"
    session.run_ps(disable_cmd)
    print(f"[+] Account disabled")

    # Remove all group memberships
    remove_groups = f"""
    $groups = Get-ADUser -Identity {username} -Properties MemberOf | Select-Object -ExpandProperty MemberOf
    foreach ($group in $groups) {{
        Remove-ADGroupMember -Identity $group -Members {username} -Confirm:$false
    }}
    """
    session.run_ps(remove_groups)
    print(f"[+] Groups removed")

    # Move to Disabled Users OU
    move_cmd = f"""
    $dn = (Get-ADUser -Identity {username}).DistinguishedName
    Move-ADObject -Identity $dn -TargetPath 'OU=Disabled Users,DC=corp,DC=local'
    """
    session.run_ps(move_cmd)
    print(f"[+] Moved to Disabled Users OU")

    # Raise ServiceNow incident
    incident_number, sys_id = create_servicenow_incident(
        f"Offboarding: {username}",
        "Access",
        f"Employee offboarding for {username}. Account disabled, groups cleared, moved to Disabled Users OU."
    )
    print(f"[+] Incident raised: {incident_number}")

    # Log the action
    log_action("OffboardUser", "success", incident_number, "offboard_user.py", username, "Account disabled, groups removed, moved to Disabled Users OU")

    # Resolve the incident
    resolve_incident(sys_id, f"Offboarding complete for {username}")
    print(f"[+] Incident resolved: {incident_number}")

    print(f"[✓] Offboarding complete for {username}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    args = parser.parse_args()
    offboard_user(args.username)
