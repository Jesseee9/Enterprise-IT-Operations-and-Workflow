import argparse
import os
from dotenv import load_dotenv
import winrm
from servicenow_api import create_servicenow_incident
from logger import log_action

load_dotenv()

def provision_user(first, last, dept, group, password):
    server_ip = os.getenv("SERVER_IP", "192.168.10.10")
    domain = os.getenv("DOMAIN", "corp.local")
    admin_user = os.getenv("ADMIN_USER", "Administrator")
    admin_pass = os.getenv("ADMIN_PASS")

    if not admin_pass:
        print("[!] ERROR: ADMIN_PASS not set in .env")
        return

    username = f"{first}.{last}"
    upn = f"{username}@{domain}"

    print(f"[*] Connecting to {server_ip} via WinRM...")

    try:
        session = winrm.Session(
            f"http://{server_ip}:5985/wsman",
            auth=(f"{admin_user}", admin_pass),
            transport="basic"
        )

        create_cmd = f"""
        New-ADUser `
            -Name "{first} {last}" `
            -GivenName "{first}" `
            -Surname "{last}" `
            -SamAccountName "{username}" `
            -UserPrincipalName "{upn}" `
            -Department "{dept}" `
            -AccountPassword (ConvertTo-SecureString "{password}" -AsPlainText -Force) `
            -Enabled $true
        """
        print(f"[*] Creating AD user {username}...")
        result = session.run_ps(create_cmd)

        if result.status_code != 0:
            error = result.std_err.decode()
            print(f"[!] AD user creation failed: {error}")
            log_action("ProvisionUser", "failure", "N/A", "provision_user.py", username, error)
            return

        print(f"[+] AD user {username} created successfully")

        group_cmd = f'Add-ADGroupMember -Identity "{group}" -Members "{username}"'
        print(f"[*] Adding {username} to group {group}...")
        result = session.run_ps(group_cmd)

        if result.status_code != 0:
            error = result.std_err.decode()
            print(f"[!] Group assignment failed: {error}")
            log_action("ProvisionUser", "failure", "N/A", "provision_user.py", username, error)
            return

        print(f"[+] {username} added to {group}")

        short_desc = f"New starter account created for {first} {last}"
        details = f"User {username} provisioned in corp.local. Department: {dept}. Group: {group}."
        print("[*] Raising ServiceNow incident...")
        inc_number, sys_id = create_servicenow_incident(short_desc, "Access", details)

        log_action(
            action="ProvisionUser",
            status="success",
            ticket_id=inc_number,
            actor="provision_user.py",
            target=username,
            notes=f"AD user created. Group: {group}. Dept: {dept}."
        )

        print(f"[✓] Day 1 complete — {username} provisioned, {inc_number} raised, audit log updated")

    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        log_action("ProvisionUser", "failure", "N/A", "provision_user.py", f"{first}.{last}", str(e))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Provision a new AD user")
    parser.add_argument("--first", required=True)
    parser.add_argument("--last", required=True)
    parser.add_argument("--dept", required=True)
    parser.add_argument("--group", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    provision_user(args.first, args.last, args.dept, args.group, args.password)
