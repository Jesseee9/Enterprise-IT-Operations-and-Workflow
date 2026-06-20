import argparse
import csv
import os
from collections import Counter
from datetime import datetime
from dotenv import load_dotenv
from logger import log_action
from servicenow_api import create_servicenow_incident, resolve_incident

load_dotenv()

def analyse_log(input_path):
    with open(input_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    total = len(rows)
    sources = Counter(r['Source'].strip() for r in rows)
    top_sources = sources.most_common(3)
    most_recent = rows[0] if rows else None

    print(f"[*] Total errors: {total}")
    print(f"[*] Top 3 sources:")
    for source, count in top_sources:
        print(f"    - {source}: {count}")
    if most_recent:
        print(f"[*] Most recent error: {most_recent['TimeGenerated']} | {most_recent['Source']} | {most_recent['Message']}")

    return total, top_sources, most_recent

def save_summary(total, top_sources, most_recent, incident_number):
    health_log_path = "logs/health_checks.csv"
    file_exists = os.path.isfile(health_log_path)

    with open(health_log_path, "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "CheckType", "Status", "TicketID", "Summary"])
        top_sources_str = "; ".join([f"{s}:{c}" for s, c in top_sources])
        summary = f"Total errors: {total}. Top sources: {top_sources_str}."
        writer.writerow([datetime.now().isoformat(), "LogAnalysis", "success", incident_number, summary])

def main():
    parser = argparse.ArgumentParser(description="Analyse exported Windows Event Log CSV")
    parser.add_argument("--input", required=True, help="Path to system_errors.csv")
    args = parser.parse_args()

    total, top_sources, most_recent = analyse_log(args.input)

    incident_number, sys_id = create_servicenow_incident(
        f"System log analysis — {total} errors found",
        "Network",
        f"PowerShell log analysis run at {datetime.now()}. Total errors: {total}. Top sources: {top_sources}."
    )
    print(f"[+] ServiceNow incident raised: {incident_number}")

    save_summary(total, top_sources, most_recent, incident_number)

    log_action("LogAnalysis", "success", incident_number, "log_analyser.py", "WindowsServer2022", f"Analysed {total} system errors")

    resolve_incident(sys_id, f"Log analysis complete. {total} errors reviewed. Top sources: {'; '.join([s for s, c in top_sources])}.")
    print(f"[+] Incident resolved: {incident_number}")

if __name__ == "__main__":
    main()
