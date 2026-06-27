import os
import requests
from dotenv import load_dotenv
from logger import log_action
from servicenow_api import create_servicenow_incident, resolve_incident
from datetime import datetime

load_dotenv()

TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")

def get_access_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default"
    }
    response = requests.post(url, data=data)
    return response.json().get("access_token")

def run_mfa_audit():
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        evidence_path = f"logs/evidence/mfa_audit_{timestamp}.txt"

        print("[*] Authenticating to Microsoft Graph API...")
        token = get_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        print("[*] Pulling user list from Entra ID...")
        users_response = requests.get(
            "https://graph.microsoft.com/v1.0/users",
            headers=headers
        )
        users = users_response.json().get("value", [])
        print(f"[+] {len(users)} users found")

        print("[*] Checking MFA registration status...")
        compliant = []
        non_compliant = []

        for user in users:
            upn = user.get("userPrincipalName", "")
            auth_response = requests.get(
                f"https://graph.microsoft.com/v1.0/users/{user['id']}/authentication/methods",
                headers=headers
            )
            methods = auth_response.json().get("value", [])
            method_types = [m.get("@odata.type", "") for m in methods]
            has_mfa = any("phone" in t or "microsoftAuthenticator" in t or "fido2" in t for t in method_types)

            if has_mfa:
                compliant.append(upn)
            else:
                non_compliant.append(upn)

        print(f"\n[+] MFA Compliance Summary:")
        print(f"    Compliant: {len(compliant)}")
        print(f"    Non-compliant: {len(non_compliant)}")
        if non_compliant:
            print(f"\n[!] Users without MFA:")
            for u in non_compliant:
                print(f"    - {u}")

        os.makedirs("logs/evidence", exist_ok=True)
        with open(evidence_path, "w") as f:
            f.write(f"MFA Compliance Audit — {timestamp}\n")
            f.write(f"Total users: {len(users)}\n")
            f.write(f"Compliant: {len(compliant)}\n")
            f.write(f"Non-compliant: {len(non_compliant)}\n\n")
            f.write("Non-compliant users:\n")
            for u in non_compliant:
                f.write(f"  - {u}\n")
        print(f"\n[+] Audit saved to {evidence_path}")

        incident_number, sys_id = create_servicenow_incident(
            "MFA compliance audit completed",
            "Security",
            f"Audit found {len(non_compliant)} users without MFA out of {len(users)} total users"
        )
        print(f"[+] ServiceNow incident raised: {incident_number}")

        log_action("MFAAudit", "success", incident_number, "mfa_audit.py", "Entra ID", f"{len(non_compliant)} non-compliant users identified")

        resolve_incident(sys_id, f"MFA audit complete. {len(non_compliant)} users flagged as non-compliant. Evidence saved to {evidence_path}")
        print(f"[+] ServiceNow incident resolved: {incident_number}")

    except Exception as e:
        log_action("MFAAudit", "failure", "N/A", "mfa_audit.py", "Entra ID", str(e))
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    run_mfa_audit()
