# Workflows

Step-by-step runbooks for every workflow in the Enterprise IT Operations and Workflow lab. Each workflow documents the exact commands, what Python automates, what remains manual, and the skills demonstrated.

---

## Script Inventory

| File | Purpose |
|---|---|
| .github/workflows/audit_summary.yml | CI — Audit log summary posted on every push to main |
| .gitignore | Excludes .env and credentials from version control |
| csv-inputs/new_starters.csv | Sample bulk provisioning input file |
| Dockerfile | Packages mfa_audit.py into a portable container |
| LOGGING.md | Full schema and rules for IT_Audit_Log.csv and health_checks.csv |
| logs/evidence/ | Stores raw output from connectivity and health checks |
| scripts/ai_triage.py | Reads audit log entries, sends to Gemini API for priority classification and recommended actions |
| scripts/auto_unlock.py | AD lockout detection and unlock via WinRM |
| scripts/bulk_provision.py | Bulk AD user provisioning from CSV |
| scripts/connectivity_check.py | Ping, nslookup, tracert, evidence saving, health log |
| scripts/deploy_network.py | Provisions Azure VNet, subnet, and NSG via Azure SDK, then tears down the VNet and NSG — the resource group remains |
| scripts/dns_audit.py | Automates external DNS record lookup (A, MX, PTR) and captures evidence |
| scripts/entra_lookup.py | Queries Entra ID via Graph API to verify live user statuses and assigned licensing |
| scripts/entra_provision.py | Provisions contractor identities directly into cloud-native Entra ID using Graph API |
| scripts/log_analyser.py | Parses exported Windows Server event log CSVs via Python to isolate system errors |
| scripts/logger.py | Shared audit logging module — used by every script |
| scripts/mfa_audit.py | Queries Graph API for Entra ID users without MFA enabled, logs compliance findings |
| scripts/offboard_user.py | Disables AD account, strips group memberships, moves to Disabled Users OU, and updates cloud identity |
| scripts/provision_user.py | AD user provisioning via WinRM |
| scripts/servicenow_api.py | Raises and resolves ServiceNow incidents via Table REST API |
| scripts/vm_health_check.py | Spins up a B1s Ubuntu VM in Azure, runs bash health check via custom data, retrieves report, tears down |

---

## Identity Management

### New Starter Provisioning
Scenario: A new employee joins. Their AD account needs creating, assigned to the correct group, and a ServiceNow incident raised and resolved — all from a single command.

Workflow:
1. Open terminal in the project folder
2. Run the provisioning script:
```
py scripts/provision_user.py --first Sarah --last Blake --dept Sales --group Sales --password Welcome1!
```
3. The script connects to Windows Server via WinRM, creates the user in corp.local, adds them to the Sales group, raises a ServiceNow incident, captures the INC number, logs the full action to IT_Audit_Log.csv, and resolves the incident
4. Open Active Directory Users and Computers — confirm Sarah.Blake exists in the Users container
5. Check her Member Of tab — confirm she is in the Sales group
6. Open ServiceNow PDI — confirm the incident shows as Resolved with the correct INC number
7. Open logs/IT_Audit_Log.csv — confirm the row is there with the INC number populated
8. Push to GitHub

**What Python automates:** AD user creation via WinRM, group assignment, ServiceNow incident open and resolve, INC capture, audit logging

**Skills:** Active Directory, WinRM, Python, ServiceNow REST API, GitHub

---

### Bulk User Provisioning from CSV
Scenario: Five new starters join on the same day. A Python script reads a CSV and creates all accounts automatically.

Workflow:
1. Create csv-inputs/new_starters.csv with columns: FirstName, LastName, Department, Group, Password
2. Add five realistic entries
3. Run the bulk provisioning script:
```
py scripts/bulk_provision.py --csv csv-inputs/new_starters.csv
```
4. The script reads each row, creates the AD user via WinRM, logs a row per user, raises one ServiceNow incident covering the batch, and resolves it
5. Open Active Directory Users and Computers — confirm all five users exist
6. Open ServiceNow PDI — confirm the incident shows as Resolved
7. Open logs/IT_Audit_Log.csv — confirm five rows were logged
8. Push the CSV, script, and updated log to GitHub

**What Python automates:** CSV parsing, AD user creation for all rows, per-user logging, ServiceNow incident open and resolve, error handling for invalid rows

**Skills:** Python, Active Directory, WinRM, CSV handling, ServiceNow, GitHub

---

### Group Membership and Role-Based Access
Scenario: A user's role has changed. Update their group membership in Active Directory, verify the change with PowerShell, and log it.

Workflow:
1. Open Active Directory Users and Computers on Windows Server 2022
2. Find Sarah.Blake — right click > Properties > Member Of
3. Remove her from the Sales group
4. Click Add — type IT-Staff, click Check Names, click OK. Click Apply and OK
5. Open PowerShell on the server and verify:
```
Get-ADUser -Identity sarah.blade -Properties MemberOf | Select-Object MemberOf
```
6. Confirm IT-Staff appears in the output and Sales is removed
7. Open ServiceNow PDI — raise an Incident manually:
   - Category: Access
   - Short description: Group membership updated — Sarah Blake
   - Note the INC number
8. Run the logger with the INC number from step 7:
```
py scripts/logger.py --action GroupUpdate --status success --ticket [INC number] --actor Manual --target sarah.blade
```
9. Resolve the incident in ServiceNow PDI — set state to Resolved, add resolution note
10. Push to GitHub

**What Python does:** Logs the manual action

**Skills:** Active Directory, PowerShell, ServiceNow, Python logging, GitHub

---

### Account Lockout Investigation
Scenario: A user is locked out. Investigate the cause in Event Viewer, unlock the account via Python, and document it.

Workflow:
1. Open Event Viewer on Windows Server 2022 — Windows Logs > Security
2. Filter by Event ID 4625 — note the account name, failure reason, and source workstation
3. Run the auto unlock script:
```
py scripts/auto_unlock.py
```
4. The script queries AD for all locked accounts, unlocks each one, raises a ServiceNow incident, logs every action, and resolves the incident
5. Open PowerShell and verify:
```
Search-ADAccount -LockedOut | Select-Object Name, LockedOut
```
6. Confirm the output is empty
7. Open ServiceNow PDI — confirm the incident shows as Resolved
8. Open logs/IT_Audit_Log.csv — confirm the row is there
9. Push to GitHub

**What Python automates:** AD lockout query, account unlock, ServiceNow incident open and resolve, logging

**Skills:** Event Viewer, Active Directory, PowerShell, Python, ServiceNow, GitHub

---

### Offboarding Workflow
Scenario: An employee is leaving. Account disabled, groups cleared, account moved to Disabled Users OU — Python handles the full AD workflow.

Workflow:
1. Run the offboarding script:
```
py scripts/offboard_user.py --username sarah.blade
```
2. The script disables the account, removes all group memberships, moves it to the Disabled Users OU, raises a ServiceNow incident, logs the action, and resolves the incident
3. Open Active Directory Users and Computers and verify:
   - Account is disabled — icon shows a downward arrow
   - Member Of tab is empty
   - Account is in the Disabled Users OU
4. Open PowerShell and verify:
```
Get-ADUser -Identity sarah.blade -Properties Enabled, MemberOf
```
5. Confirm Enabled = False and MemberOf is empty
6. Open Entra ID > Users — confirm the account shows as blocked from sign-in
7. Open ServiceNow PDI — confirm the incident shows as Resolved
8. Push to GitHub

**What Python automates:** Account disable, group removal, OU move, ServiceNow incident open and resolve, logging

**Skills:** Active Directory, Entra ID, PowerShell, Python, ServiceNow, GitHub

---

### Entra ID User Lifecycle via Graph API
Scenario: A new contractor needs a cloud identity created and verified. Python handles the full workflow via Microsoft Graph API — no portal required.

Workflow:
1. Run the Entra ID provisioning script:
```
py scripts/entra_provision.py --display "Test Contractor" --upn testcontractor@yourdomain.onmicrosoft.com --password TempPass1!
```
2. The script authenticates to Graph API, creates the user in Entra ID, raises a ServiceNow incident, logs the action to IT_Audit_Log.csv, and resolves the incident
3. Open Entra ID > Users — confirm the account exists and shows as active
4. Run the lookup script to verify:
```
py scripts/entra_lookup.py --upn testcontractor@yourdomain.onmicrosoft.com
```
5. The script returns the user's display name, account status, and assigned licences
6. Open ServiceNow PDI — confirm the incident shows as Resolved with the correct INC number
7. Push to GitHub

**What Python automates:** Graph API authentication, user creation, account verification, ServiceNow incident open and resolve, audit logging

**Skills:** Microsoft Entra ID, Microsoft Graph API, Python, REST APIs, ServiceNow, GitHub

---

## Security Operations

### Python Script Hardening
Scenario: The scripts built across the lab work but need production‑grade error handling, input validation, and secrets management.

Workflow:
1. Open scripts/provision_user.py
2. Wrap the main logic in a try/except block:
```python
try:
    # existing logic here
except Exception as e:
    log_action("ProvisionUser", "failure", "N/A", "provision_user.py", target, str(e))
    print(f"[ERROR] {e}")
```
3. Add input validation — if any required field is empty, raise a ValueError with a clear message
4. Confirm .env exists in the project root with all credentials. Confirm .env is in .gitignore
5. Confirm every script loads credentials via dotenv:
```python
from dotenv import load_dotenv
import os
load_dotenv()
server_ip = os.getenv("SERVER_IP")
```
6. Retest each hardened script — confirm it still works with values loading from .env
7. Run a deliberate failure — pass an empty field — confirm the script catches it and logs a failure row rather than crashing
8. Push hardened scripts to GitHub — confirm .env does not appear in the commit

**What Python does:** This entire workflow is Python focused

**Skills:** Python, Error Handling, Input Validation, Security Best Practices, dotenv, GitHub

---

## Network Operations

### Connectivity Troubleshooting
Scenario: A user reports they cannot reach a network resource. Run diagnostics, save evidence, document the outcome, and close the ticket.

Workflow:
1. Run the connectivity check script:
```
py scripts/connectivity_check.py --target 192.168.10.50
```
2. The script runs ping, nslookup, and tracert — saves raw output to logs/evidence/
3. Review the saved output — note whether the target was reachable and what DNS returned
4. If ping failed, open VMware Workstation and confirm both VMs are on Host‑only adapter (VMnet2). Re‑run the script after fixing
5. The script raises a ServiceNow incident automatically, logs a row to logs/health_checks.csv with the INC number, and resolves the incident with a summary
6. Open ServiceNow PDI — confirm the incident shows as Resolved
7. Open logs/health_checks.csv — confirm the row is there with the correct status and INC number
8. Push to GitHub

**What Python automates:** Ping, nslookup, tracert, evidence saving, ServiceNow incident open and resolve, health check logging

**Skills:** Networking, DNS, VMware, Python, ServiceNow, GitHub

---

### DNS Health Check and Public Record Audit
Scenario: A client reports intermittent connectivity issues. Run a full external DNS audit to rule out misconfiguration — Python automates the checks and saves all evidence.

Workflow:
1. Run the DNS audit script against a target domain:
```
py scripts/dns_audit.py --domain yourdomain.com
```
2. The script runs nslookup for A, MX, and PTR records, checks whether the domain resolves correctly, saves all output to logs/evidence/, raises a ServiceNow incident, logs the result to logs/health_checks.csv, and resolves the incident
3. Review the saved evidence — note any missing or misconfigured records
4. Cross‑reference against expected values — confirm MX records point to the correct mail server and A record resolves to the correct IP
5. Open ServiceNow PDI — confirm the incident shows as Resolved with findings in the resolution notes
6. Push evidence file, script, and log to GitHub

**What Python automates:** nslookup execution, record capture, evidence saving, health check logging, ServiceNow incident open and resolve

**Skills:** DNS, Networking, Python, Evidence Collection, ServiceNow, GitHub

---

## Cloud Infrastructure

### Azure Network Provisioning and Security
Scenario: A new client environment needs a secure network provisioned. Python uses the Azure SDK to build a VNet with a locked‑down NSG, runs a verification check, and tears everything down — zero ongoing cost.

Workflow:
1. Ensure your .env file contains:
```
AZURE_SUBSCRIPTION_ID=your_subscription_id
AZURE_TENANT_ID=your_tenant_id
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_client_secret
AZURE_RESOURCE_GROUP=rg-Enterprise-IT-Lab
AZURE_LOCATION=uksouth
```
Note: rg-Enterprise-IT-Lab must be pre‑created in Azure and empty before running this script.
2. Open ServiceNow PDI — raise an Incident manually:
   - Category: Network
   - Short description: Azure network provisioning and security check — [date]
   - Note the INC number
3. Run the network provisioning script:
```
py scripts/deploy_network.py
```
4. The script authenticates to Azure via SDK, provisions a VNet (10.0.0.0/16), creates a subnet (10.0.1.0/24), attaches a NSG blocking all inbound traffic except port 22, verifies the NSG rules, logs the result, and tears down the VNet and NSG — the resource group remains
5. Confirm the output shows: VNet created, NSG applied, rules verified, VNet and NSG deleted
6. Run the logger:
```
py scripts/logger.py --action AzureNetworkProvision --status success --ticket [INC number] --actor deploy_network.py --target Azure-uksouth
```
7. Resolve the incident in ServiceNow PDI
8. Push to GitHub

**What Python automates:** Azure authentication, VNet and subnet creation, NSG rule configuration, verification, teardown, audit logging

**Skills:** Azure SDK, IP Subnetting, Network Security Groups, Cloud Networking, Python, ServiceNow, GitHub

---

### Linux VM Bootstrap and Health Check
Scenario: A Linux server needs provisioning and an immediate health check. Python spins up a B1s Ubuntu VM in Azure, runs a bash health check automatically on boot, pulls the report back locally, and destroys the infrastructure.

Workflow:
1. Run the VM bootstrap script:
```
py scripts/vm_health_check.py
```
2. The script provisions a B1s Ubuntu VM inside a secured subnet within rg-Enterprise-IT-Lab, passes a bash script via custom data that runs on boot — checking disk usage, active ports, and system uptime — waits for the report, downloads it to logs/evidence/vm_health_[timestamp].txt, and deletes the VM and all associated network resources
3. Open logs/evidence/ — confirm the health report file is there
4. Review the report — note disk usage, active ports, and uptime
5. Open ServiceNow PDI — raise an Incident manually:
   - Category: Infrastructure
   - Short description: Azure Linux VM health check — [date]
   - Note the INC number
6. Run the logger:
```
py scripts/logger.py --action AzureVMHealthCheck --status success --ticket [INC number] --actor vm_health_check.py --target Azure-UbuntuVM
```
7. Resolve the incident in ServiceNow PDI
8. Push to GitHub

**What Python automates:** Azure VM provisioning, bash script injection via custom data, report retrieval, infrastructure teardown, audit logging

**Skills:** Azure SDK, Linux Administration, Infrastructure as Code, Cloud Lifecycle Management, Python, ServiceNow, GitHub

---

### MFA Compliance Audit with Docker
Scenario: A security audit is required. Python queries Microsoft Graph API to identify all Entra ID users without MFA enabled, logs the findings, and the script is packaged into a Docker container so it can run on any machine.

Workflow:
1. Run the MFA audit script:
```
py scripts/mfa_audit.py
```
2. The script authenticates to Graph API, pulls all users from your Entra ID tenant, checks MFA registration status for each, prints a compliance summary to the terminal, saves findings to logs/evidence/mfa_audit_[timestamp].txt, raises a ServiceNow incident, logs the action, and resolves the incident automatically
3. Review the output — note any users flagged as non‑compliant
4. Confirm logs/evidence/ contains the audit file
5. Build the Docker image:
```
docker build -t mfa-auditor .
```
6. Run the container:
```
docker run --env-file .env mfa-auditor
```
7. Confirm the container produces the same output as the direct script run
8. Push to GitHub — Dockerfile and script included, .env excluded

**What Python automates:** Graph API authentication, MFA status check per user, findings logging, ServiceNow incident open and resolve

**What Docker does:** Packages the auditor into a portable container that runs identically on any machine

**Skills:** Microsoft Graph API, Entra ID Security, MFA Compliance, Docker, Python, ServiceNow, GitHub

---

## System Administration

### PowerShell Log Analysis
Scenario: Review system health by exporting Windows Event Logs with PowerShell and analysing them with Python to produce a summary.

Workflow:
1. Open PowerShell on Windows Server 2022 and create the logs folder if it does not exist:
```
New-Item -ItemType Directory -Force -Path C:\logs
```
2. Export the last 20 system errors:
```
Get-EventLog -LogName System -EntryType Error -Newest 20 | Select-Object TimeGenerated, Source, Message | Export-Csv -Path C:\logs\system_errors.csv -NoTypeInformation
```
3. Copy system_errors.csv to your local project folder under logs/
4. Run the log analyser:
```
py scripts/log_analyser.py --input logs/system_errors.csv
```
5. The script counts total errors, identifies the top 3 sources, prints the most recent error, saves a summary to logs/health_checks.csv, raises a ServiceNow incident, and resolves it
6. Review the output — note any recurring sources worth investigating
7. Open ServiceNow PDI — confirm the incident shows as Resolved
8. Push everything to GitHub

**What Python automates:** CSV parsing, error counting, source analysis, summary output, ServiceNow incident open and resolve, logging

**Skills:** PowerShell, Python, Windows Event Logs, ServiceNow, GitHub

---

### AI-Assisted Incident Triage
Scenario: Before starting a shift, Python reads the recent audit log, sends the entries to Gemini, and gets back a priority ranking and recommended action for each — helping the engineer know what to tackle first.

Workflow:
1. Ensure your .env file contains:
```
GEMINI_API_KEY=your_gemini_api_key
```

Uses the google-genai SDK (migrated from the deprecated google-generativeai package) calling model gemini-3.1-flash-lite.

2. Run the triage script:
```
py scripts/ai_triage.py --input logs/IT_Audit_Log.csv
```
3. The script reads the last 10 log entries, sends them to Gemini with a structured prompt requesting priority classification and recommended next action per entry, prints the response to terminal, and saves output to logs/evidence/triage_[timestamp].txt
4. Review the output — note which incidents Gemini flagged as highest priority
5. Open ServiceNow PDI — raise an Incident manually:
   - Category: Service Desk
   - Short description: AI‑assisted triage completed — [date]
   - Note the INC number
6. Run the logger:
```
py scripts/logger.py --action AITriage --status success --ticket [INC number] --actor ai_triage.py --target IT_Audit_Log.csv
```
7. Resolve the incident in ServiceNow PDI
8. Push to GitHub

**What Python automates:** Log parsing, Gemini API call, structured prompt engineering, evidence saving, audit logging

**Skills:** Python, Gemini API, Prompt Engineering, Log Analysis, ServiceNow, GitHub

---
## Shift Simulation
Scenario: You are covering a support shift. Work through five tickets in order. Each must be fully resolved and closed in ServiceNow before moving to the next. Log everything.

Ticket Queue:

| # | Type | Task |
|---|------|------|
| 1 | New starter | Create AD account for James.Okafor, department = Finance, assign to Finance group |
| 2 | Locked account | Sarah.Blake is locked out — simulate via PowerShell (`Set-ADUser -Replace @{lockoutTime=1}`), run auto_unlock.py, verify with PowerShell |
| 3 | Connectivity | A user cannot reach the server — run connectivity_check.py against 192.168.10.10 (server's current Host-only adapter IP; may drift due to DHCP — verify via ipconfig if needed), review the evidence file, document findings. Note: ServiceNow incident raise/resolve was added to connectivity_check.py during this session — the script now automatically raises and resolves an incident, in line with the other workflow scripts. |
| 4 | Offboarding | A contractor's account needs disabling — run offboard_user.py, verify in AD and Entra ID, confirm groups are cleared |
| 5 | Health check | Export system errors with PowerShell, run log_analyser.py, confirm no critical unresolved errors |

Rules:
- Raise a real ServiceNow Incident for each ticket
- Log every action to IT_Audit_Log.csv
- Resolve the ServiceNow ticket before moving to the next one
- Push everything to GitHub at the end with a single commit

