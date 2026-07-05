import os
import csv
import argparse
from google import genai
from dotenv import load_dotenv
from logger import log_action
from datetime import datetime

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def run_triage(input_file):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        evidence_path = f"logs/evidence/triage_{timestamp}.txt"

        print(f"[*] Reading last 10 entries from {input_file}...")
        with open(input_file, "r") as f:
            rows = list(csv.DictReader(f))
        recent = rows[-10:] if len(rows) >= 10 else rows

        entries_text = "\n".join([
            f"Action: {r.get('Action','')}, Status: {r.get('Status','')}, Ticket: {r.get('TicketID','')}, Target: {r.get('Target','')}, Notes: {r.get('Notes','')}"
            for r in recent
        ])

        prompt = f"""You are an IT support triage assistant. Review these recent audit log entries from an MSP environment and for each one provide:
1. Priority level: Critical, High, Medium, or Low
2. Recommended next action in one sentence

Entries:
{entries_text}

Format your response clearly with one entry per line."""

        print("[*] Sending to Gemini for triage analysis...")
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt,
        )
        result = response.text

        print("\n[+] Triage Results:")
        print(result)

        os.makedirs("logs/evidence", exist_ok=True)
        with open(evidence_path, "w") as f:
            f.write(f"AI Triage Report — {timestamp}\n\n")
            f.write(result)
        print(f"\n[+] Triage report saved to {evidence_path}")

        log_action("AITriage", "success", "PENDING", "ai_triage.py", input_file, "Gemini triage analysis completed successfully")

    except Exception as e:
        log_action("AITriage", "failure", "N/A", "ai_triage.py", input_file, str(e))
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    run_triage(args.input)
