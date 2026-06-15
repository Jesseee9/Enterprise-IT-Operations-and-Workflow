import argparse
import csv
import os
from datetime import datetime
from dotenv import load_dotenv
import winrm
from servicenow_api import create_servicenow_incident, resolve_incident
from logger import log_action

load_dotenv()

def get_winrm_session():
    server_ip = os.getenv("SERVER_IP", "192.168.169.10")
    admin_user = os.getenv("ADMIN_USER", "Administrator")
    admin_pass = os.getenv("ADMIN_PASS")
    session = winrm.Session(
        f"http://{server_ip}:5985/wsman",
        auth=(admin_user, admin_pass),
        transport="basic"
    )
    return session

def create_ad_user(session, first, last, dept, group, password):
    domain = os.getenv("DOMAIN", "corp.local")
    username = f"{first}.{last}"
    upn = f"{username}@{domain}"

    create_cmd = f'''
    New-ADUser `
        -Name "{first} {last}" `
        -GivenName "{first}" `
        -Surname "{last}" `
        -SamAccountName "{username}" `
        -UserPrincipalName "{upn}" `
        -Department "{dept}" `
        -AccountPassword (ConvertTo-SecureString "{password}" -AsPlainText -Force) `
        -Enabled $true
    '''
    result = session.run_ps(create_cmd)
    if result.status_code != 0:
        error = result.std_err.decode()
        return False, error

    group_cmd = f'Add-ADGroupMember -Identity "{group}" -Members "{username}"'
    result = session.run_ps(group_cmd)
    if result.status_code != 0:
        error = result.std_err.decode()
        return False, f"User created but group assignment failed: {error}"

    return True, "User created and group assigned"

def main():
    parser = argparse.ArgumentParser(description="Bulk provision AD users from CSV")
    parser.add_argument("--csv", required=True, help="Path to CSV file")
    args = parser.parse_args()

    session = get_winrm_session()

    results = []
    errors = []

    with open(args.csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"[*] Found {len(rows)} users to provision")

    incident_number, sys_id = create_servicenow_incident(
        f"Bulk new starter provisioning — {len(rows)} accounts",
        "Access",
        f"Bulk provisioning job started at {datetime.now()} for {len(rows)} users from {args.csv}"
    )
    print(f"[+] ServiceNow incident raised: {incident_number}")

    for row in rows:
        first = row['FirstName'].strip()
        last = row['LastName'].strip()
        dept = row['Department'].strip()
        group = row['Group'].strip()
        password = row['Password'].strip()
        username = f"{first}.{last}"

        if not all([first, last, dept, group, password]):
            print(f"[!] Skipping invalid row: {row}")
            errors.append(username)
            log_action("BulkProvision", "failure", incident_number, "bulk_provision.py", username, "Invalid or incomplete row in CSV")
            continue

        print(f"[*] Provisioning {username}...")
        success, message = create_ad_user(session, first, last, dept, group, password)

        if success:
            print(f"[+] {username} — {message}")
            log_action("BulkProvision", "success", incident_number, "bulk_provision.py", username, message)
            results.append(username)
        else:
            print(f"[!] {username} — failed: {message}")
            log_action("BulkProvision", "failure", incident_number, "bulk_provision.py", username, message)
            errors.append(username)

    summary = f"Bulk provisioning complete. Success: {len(results)}, Failed: {len(errors)}. Users: {', '.join(results)}"
    resolve_incident(sys_id, summary)
    print(f"[+] Incident resolved: {incident_number}")
    print(f"\n--- Summary ---")
    print(f"Provisioned: {len(results)}")
    print(f"Failed: {len(errors)}")
    if errors:
        print(f"Errors: {', '.join(errors)}")

if __name__ == "__main__":
    main()
