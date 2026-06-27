import os
import subprocess
import argparse
from dotenv import load_dotenv
from logger import log_action
from servicenow_api import create_servicenow_incident, resolve_incident
from datetime import datetime

load_dotenv()

def run_dns_audit(domain):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        evidence_path = f"logs/evidence/dns_audit_{timestamp}.txt"

        print(f"[*] Running DNS audit for {domain}...")

        results = []

        for record_type in ["A", "MX", "PTR"]:
            print(f"[*] Checking {record_type} record...")
            try:
                output = subprocess.check_output(
                    ["nslookup", "-type=" + record_type, domain],
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=10
                )
                results.append(f"=== {record_type} RECORD ===\n{output}\n")
                print(f"[+] {record_type} record retrieved")
            except subprocess.CalledProcessError as e:
                results.append(f"=== {record_type} RECORD ===\nError: {e.output}\n")
                print(f"[!] {record_type} record lookup failed")

        os.makedirs("logs/evidence", exist_ok=True)
        with open(evidence_path, "w") as f:
            f.write(f"DNS Audit Report — {domain} — {timestamp}\n\n")
            f.writelines(results)
        print(f"[+] Evidence saved to {evidence_path}")

        incident_number, sys_id = create_servicenow_incident(
            f"DNS health check completed — {domain}",
            "Network",
            f"DNS audit for {domain} completed. A, MX, and PTR records checked. Evidence saved to {evidence_path}"
        )
        print(f"[+] ServiceNow incident raised: {incident_number}")

        log_action("DNSAudit", "success", incident_number, "dns_audit.py", domain, f"A, MX, PTR records checked — evidence at {evidence_path}")

        resolve_incident(sys_id, f"DNS audit complete for {domain}. All records checked and evidence saved. Solution provided.")
        print(f"[+] ServiceNow incident resolved: {incident_number}")

    except Exception as e:
        log_action("DNSAudit", "failure", "N/A", "dns_audit.py", domain, str(e))
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", required=True, help="Domain to audit")
    args = parser.parse_args()
    run_dns_audit(args.domain)
