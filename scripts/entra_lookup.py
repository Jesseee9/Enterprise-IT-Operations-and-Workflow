import argparse
import os
import requests
from dotenv import load_dotenv

# 1. Load credentials from .env using dotenv
load_dotenv()

AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")

def main():
    # 2. Accept one command line argument using argparse: --upn
    parser = argparse.ArgumentParser(description="Lookup a user in Entra ID by UPN.")
    parser.add_argument("--upn", required=True, help="User Principal Name (UPN) of the user to look up")
    args = parser.parse_args()

    # 6. Wrap all logic in try/except
    try:
        # Validate that configurations are present
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
        print("[+] Authenticated successfully.")

        # 4. Query the user from Entra ID via GET to https://graph.microsoft.com/v1.0/users/{upn}
        # request displayName, accountEnabled, and assignedLicenses fields
        print(f"[*] Querying Entra ID for user: {args.upn}...")
        user_url = f"https://graph.microsoft.com/v1.0/users/{args.upn}"
        params = {
            "$select": "displayName,accountEnabled,assignedLicenses"
        }
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        user_res = requests.get(user_url, params=params, headers=headers, timeout=10)
        
        if user_res.status_code == 404:
            raise ValueError(f"User '{args.upn}' not found in Entra ID.")
        
        user_res.raise_for_status()
        user_data = user_res.json()

        # 5. Print the display name, account status (enabled or disabled), and assigned licenses
        display_name = user_data.get("displayName", "N/A")
        account_enabled = user_data.get("accountEnabled")
        
        if account_enabled is True:
            status = "Enabled"
        elif account_enabled is False:
            status = "Disabled"
        else:
            status = "Unknown"
            
        licenses = user_data.get("assignedLicenses", [])
        license_ids = [lic.get("skuId", "N/A") for lic in licenses]

        print("\n=== Entra ID User Details ===")
        print(f"Display Name   : {display_name}")
        print(f"Account Status : {status}")
        if license_ids:
            print("Assigned Licenses:")
            for sku_id in license_ids:
                print(f" - SkuID: {sku_id}")
        else:
            print("Assigned Licenses: None")
        print("=============================\n")

    except Exception as e:
        # Prints a clear error message if the user is not found or the request fails
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    main()
