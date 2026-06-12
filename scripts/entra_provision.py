import argparse
import os
import requests
from dotenv import load_dotenv
from servicenow_api import create_incident, resolve_incident
from logger import log_action

# 1. Load credentials from .env using dotenv
load_dotenv()

AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
SN_INSTANCE = os.getenv("SN_INSTANCE")
SN_USER = os.getenv("SN_USER")
SN_PASSWORD = os.getenv("SN_PASSWORD")

def main():
    # 2. Accept command line arguments using argparse
    parser = argparse.ArgumentParser(description="Provision a user in Entra ID and log the action.")
    parser.add_argument("--display", required=True, help="Display Name of the user")
    parser.add_argument("--upn", required=True, help="User Principal Name (UPN) of the user")
    parser.add_argument("--password", required=True, help="Password for the user")
    args = parser.parse_args()

    # Define mailNickname from UPN
    mail_nickname = args.upn.split("@")[0] if "@" in args.upn else args.upn

    ticket_id = "N/A"
    sys_id = None

    try:
        # Validate that required configurations are present
        if not all([AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET]):
            raise ValueError("Azure/Entra ID credentials (AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET) are missing in the environment.")

        # 3. Authenticate to Microsoft Graph API using client credentials flow
        print("[*] Authenticating to Microsoft Graph API...")
        token_url = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/token"
        token_data = {
            "grant_type": "client_credentials",
            "client_id": AZURE_CLIENT_ID,
            "client_secret": AZURE_CLIENT_SECRET,
            "scope": "https://graph.microsoft.com/.default"
        }
        
        token_res = requests.post(token_url, data=token_data, timeout=10)
        token_res.raise_for_status()
        access_token = token_res.json().get("access_token")
        if not access_token:
            raise ValueError("Access token not found in authentication response.")
        print("[+] Authenticated to Microsoft Graph API successfully.")

        # 4. Create user in Entra ID via POST to https://graph.microsoft.com/v1.0/users
        print("[*] Creating user in Entra ID...")
        create_user_url = "https://graph.microsoft.com/v1.0/users"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        user_payload = {
            "accountEnabled": True,
            "displayName": args.display,
            "mailNickname": mail_nickname,
            "userPrincipalName": args.upn,
            "passwordProfile": {
                "forceChangePasswordNextSignIn": False,
                "password": args.password
            }
        }
        
        create_res = requests.post(create_user_url, json=user_payload, headers=headers, timeout=10)
        create_res.raise_for_status()
        print(f"[+] Entra ID user '{args.display}' ({args.upn}) created successfully.")

        # 5. Raise a ServiceNow incident using create_incident
        print("[*] Raising ServiceNow incident...")
        short_desc = f"Entra ID user created — {args.display}"
        details = f"Successfully provisioned user account in Entra ID.\nDisplay Name: {args.display}\nUPN: {args.upn}"
        inc_number, sys_id = create_incident(short_desc, "Software", details)
        
        if inc_number in ("INC_API_ERR", "INC_CONN_ERR") or not sys_id:
            raise RuntimeError(f"ServiceNow incident creation failed: {inc_number}")
        
        ticket_id = inc_number
        print(f"[+] ServiceNow incident raised: {ticket_id} (SysID: {sys_id})")

        # 6. Log the action to IT_Audit_Log.csv
        print("[*] Logging action to IT_Audit_Log.csv...")
        log_action(
            action="EntraProvision",
            status="success",
            ticket_id=ticket_id,
            actor="entra_provision.py",
            target=args.upn,
            notes=f"Entra ID user created. ServiceNow incident raised."
        )
        print("[+] Logged action successfully.")

        # 7. Resolve the ServiceNow incident using the sys_id
        print("[*] Resolving ServiceNow incident...")
        resolution_notes = f"ServiceNow incident {ticket_id} resolved. Entra ID user creation workflow complete."
        resolve_incident(sys_id, resolution_notes)
        print("[+] Resolved ServiceNow incident.")
        
        print("[✓] Process complete — Entra ID user created, incident raised and resolved, log updated.")

    except Exception as e:
        error_msg = str(e)
        print(f"[!] Error occurred: {error_msg}")
        print("[*] Logging failure to IT_Audit_Log.csv...")
        try:
            log_action(
                action="EntraProvision",
                status="failure",
                ticket_id=ticket_id,
                actor="entra_provision.py",
                target=args.upn,
                notes=error_msg
            )
            print("[+] Logged failure successfully.")
        except Exception as log_err:
            print(f"[!] Critical: Failed to log failure to CSV: {log_err}")

if __name__ == "__main__":
    main()
