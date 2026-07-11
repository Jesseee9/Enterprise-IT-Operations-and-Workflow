import argparse
import csv
import os
import subprocess
from datetime import datetime
from servicenow_api import create_servicenow_incident, resolve_incident

HEALTH_LOG_PATH = "logs/health_checks.csv"
EVIDENCE_DIR = "logs/evidence"
HEADERS = ["timestamp", "target", "ping_result", "dns_result", "tracert_saved", "overall_status", "notes", "inc_number"]


def run_command(cmd):
    """Run a shell command and return (stdout, returncode)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout + result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "ERROR: Command timed out after 60 seconds", 1
    except Exception as e:
        return f"ERROR: {e}", 1


def save_evidence(target, tool, output):
    """Write raw command output to logs/evidence/ and return the saved file path."""
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_target = target.replace(".", "-").replace(":", "-")
    filename = f"{timestamp_str}_{safe_target}_{tool}.txt"
    filepath = os.path.join(EVIDENCE_DIR, filename)
    with open(filepath, "w") as f:
        f.write(output)
    print(f"[+] Evidence saved: {filepath}")
    return filepath


def log_health_check(timestamp, target, ping_result, dns_result, tracert_saved, overall_status, notes="", inc_number=""):
    """Append a summary row to logs/health_checks.csv."""
    os.makedirs("logs", exist_ok=True)
    file_exists = os.path.isfile(HEALTH_LOG_PATH)
    with open(HEALTH_LOG_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS, quoting=csv.QUOTE_ALL)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": timestamp,
            "target": target,
            "ping_result": ping_result,
            "dns_result": dns_result,
            "tracert_saved": tracert_saved,
            "overall_status": overall_status,
            "notes": notes,
            "inc_number": inc_number
        })
    print(f"[LOGGED] ConnectivityCheck | {overall_status} | {target}")


def connectivity_check(target):
    timestamp = datetime.now().isoformat(timespec="seconds")
    notes_parts = []

    # --- Ping ---
    print(f"[*] Running ping against {target}...")
    ping_output, ping_rc = run_command(["ping", "-n", "4", target])
    save_evidence(target, "ping", ping_output)
    if ping_rc == 0 and "TTL=" in ping_output:
        ping_result = "reachable"
        print(f"[+] Ping succeeded — {target} is reachable")
    else:
        ping_result = "unreachable"
        notes_parts.append("ping failed")
        print(f"[!] Ping failed — {target} did not respond")

    # --- NSLookup ---
    print(f"[*] Running nslookup against {target}...")
    nslookup_output, nslookup_rc = run_command(["nslookup", target])
    save_evidence(target, "nslookup", nslookup_output)
    if nslookup_rc == 0 and "NXDOMAIN" not in nslookup_output and "can't find" not in nslookup_output.lower():
        dns_result = "resolved"
        print(f"[+] NSLookup succeeded — {target} resolved")
    else:
        dns_result = "unresolved"
        notes_parts.append("dns unresolved")
        print(f"[!] NSLookup failed — {target} could not be resolved")

    # --- Tracert ---
    print(f"[*] Running tracert against {target}...")
    tracert_output, _ = run_command(["tracert", "-d", "-w", "1000", target])
    tracert_path = save_evidence(target, "tracert", tracert_output)
    tracert_saved = tracert_path

    # --- Overall status ---
    if ping_result == "reachable" and dns_result == "resolved":
        overall_status = "healthy"
    elif ping_result == "reachable" or dns_result == "resolved":
        overall_status = "degraded"
    else:
        overall_status = "unreachable"

    notes = "; ".join(notes_parts) if notes_parts else "all checks passed"

    inc_number, sys_id = create_servicenow_incident(
        short_description=f"Connectivity check — {target}",
        category="Network",
        details=f"Ping: {ping_result}, DNS: {dns_result}, Overall status: {overall_status}"
    )
    print(f"[+] ServiceNow incident raised: {inc_number}")

    resolve_incident(sys_id, resolution_notes=f"Connectivity check completed for {target}. Ping: {ping_result}. DNS: {dns_result}. Overall status: {overall_status}.")
    print(f"[+] Incident resolved: {inc_number}")

    log_health_check(
        timestamp=timestamp,
        target=target,
        ping_result=ping_result,
        dns_result=dns_result,
        tracert_saved=tracert_saved,
        overall_status=overall_status,
        notes=notes,
        inc_number=inc_number
    )

    print(f"[DONE] Connectivity check complete -- {target} | {overall_status}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ping, nslookup, and tracert against a target IP")
    parser.add_argument("--target", required=True, help="IP address or hostname to check")
    args = parser.parse_args()

    connectivity_check(args.target)

