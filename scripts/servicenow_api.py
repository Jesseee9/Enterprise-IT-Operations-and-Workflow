import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def create_servicenow_incident(short_description, category, details):
    instance = os.getenv("SN_INSTANCE", "dev268884")
    url = f"https://{instance}.service-now.com/api/now/table/incident"
    user = os.getenv("SN_USER", "admin")
    password = os.getenv("SN_PASSWORD")

    if not password:
        print("[!] ERROR: SN_PASSWORD not set in .env")
        return "INC_API_ERR"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "short_description": short_description,
        "category": category,
        "description": details,
        "urgency": "3",
        "impact": "3"
    }

    try:
        response = requests.post(
            url,
            auth=(user, password),
            headers=headers,
            data=json.dumps(payload),
            timeout=10
        )

        if response.status_code == 201:
            data = response.json()
            inc_number = data["result"]["number"]
            sys_id = data["result"]["sys_id"]
            print(f"[+] ServiceNow incident raised: {inc_number} (SysID: {sys_id})")
            return inc_number
        else:
            print(f"[!] ServiceNow API failed — status {response.status_code}")
            print(response.text)
            return "INC_API_ERR"

    except requests.exceptions.RequestException as e:
        print(f"[!] Connection error reaching ServiceNow: {e}")
        return "INC_CONN_ERR"
