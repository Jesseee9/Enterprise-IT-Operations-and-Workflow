# IT Ops Training Lab

A 14-day repeatable lab built to simulate working in an MSP environment. Every task follows a real workflow — not isolated exercises. Where Python can genuinely automate something, it does. Where it can’t, the task is done manually and logged.

Built and maintained by Jesse Adejoh as part of ongoing IT support skill development.

-----

## Environment

|Component          |Details                            |
|-------------------|-----------------------------------|
|Windows Server 2022|192.168.128.130 — corp.local domain|
|Windows 11 VM      |192.168.10.60 — DESKTOP-QL161MH    |
|Linux VM           |IP confirmed at task time          |
|ServiceNow PDI     |dev268884                          |
|Microsoft 365      |Business Basic tenant              |
|Hypervisor         |VMware Workstation                 |

-----

## Daily Structure

|Block    |Time     |What Happens                                                                                           |
|---------|---------|-------------------------------------------------------------------------------------------------------|
|Warm-up  |10 min   |Check VMs are running. Confirm Windows Server and Windows 11 VM are reachable. Log into ServiceNow PDI.|
|Main Task|60–90 min|Follow the day’s steps. Every action is deliberate — treat it as a real support ticket.                |
|Logging  |5–10 min |Run the Python logger script. Confirm the row appears in logs/IT_Audit_Log.csv.                        |
|Push     |5 min    |Push everything to GitHub via Git Bash or IDE.                                                         |

-----

## How Logging Works

Every task gets logged to `logs/IT_Audit_Log.csv` using `scripts/logger.py`.

For automated tasks — the script logs the action itself at the end of the run.
For manual tasks — after finishing, run the logger from terminal and pass in the details.

See `LOGGING.md` for the full schema and setup.

-----

## 14-Day Calendar

-----

### Week 1 — Core IT Support Workflows

-----

#### Day 1: New Starter Provisioning

**Scenario:** A new employee joins. Their account needs creating in Active Directory, assigned to the right group, and a ticket raised in ServiceNow. This task is automated — a Python script handles the AD creation and logs everything.

**Steps:**

1. Open terminal in the project folder
1. Run the provisioning script — pass in first name, last name, department, group, and password:

```bash
python scripts/provision_user.py --first Sarah --last Blake --dept Sales --group Sales --password Welcome1!
```

1. The script connects to Windows Server via WinRM, creates the user in corp.local, adds them to the group, and logs the action
1. Open Active Directory Users and Computers and verify Sarah.Blake exists in the Users container
1. Check her Member Of tab — confirm she is in the Sales group
1. Open ServiceNow PDI and raise an Incident:
- Category: Access
- Short description: New starter account created for Sarah Blake
- Note the INC number
1. Update the log row with the ticket ID:

```bash
python scripts/logger.py --action ProvisionUser --status success --ticket INC0010001 --actor provision_user.py --target sarah.blake
```

1. Open `logs/IT_Audit_Log.csv` and confirm the row is there
1. Push to GitHub

**What Python automates:** AD user creation, group assignment, audit logging

**Skills touched:** Active Directory, WinRM, Python, ServiceNow, GitHub

-----

#### Day 2: Connectivity Troubleshooting

**Scenario:** A user reports they cannot reach a network resource. Run diagnostics, save the evidence, and document the outcome. Python automates the checks and saves the output.

**Steps:**

1. Run the connectivity check script — pass in the target IP:

```bash
python scripts/connectivity_check.py --target 192.168.128.130
```

1. The script runs ping, nslookup, and tracert — saves the output to `logs/evidence/`
1. Review the saved output — note whether the target was reachable and what DNS returned
1. If ping failed, open VMware Workstation and check both VMs are on the same virtual network adapter
1. Re-run the script after fixing — confirm it passes
1. Open ServiceNow PDI and raise an Incident:
- Category: Network
- Short description: Connectivity check — [date]
- Note the INC number
1. The script logs automatically — verify the row in `logs/health_checks.csv`
1. Push to GitHub

**What Python automates:** Ping, nslookup, tracert, evidence saving, logging

**Skills touched:** Networking, DNS, VMware, Python, ServiceNow, GitHub

-----

#### Day 3: Group Membership and Role-Based Access

**Scenario:** A user’s role has changed and their group membership needs updating. This is done manually in Active Directory — Python logs the change.

**Steps:**

1. Open Active Directory Users and Computers on Windows Server 2022
1. Find Sarah.Blake — right click > Properties > Member Of
1. Remove her from the Sales group — select it and click Remove
1. Click Add — type IT-Staff, click Check Names, click OK
1. Click Apply and OK
1. Open PowerShell on the server and verify the change:

```powershell
Get-ADUser -Identity sarah.blake -Properties MemberOf | Select-Object MemberOf
```

1. Confirm IT-Staff appears in the output
1. Open ServiceNow PDI and raise an Incident:
- Category: Access
- Short description: Group membership updated for Sarah Blake
- Note the INC number
1. Run the logger:

```bash
python scripts/logger.py --action GroupUpdate --status success --ticket INC0010002 --actor Manual --target sarah.blake
```

1. Push to GitHub

**What Python does:** Logs the manual action

**Skills touched:** Active Directory, PowerShell, ServiceNow, Python logging, GitHub

-----

#### Day 4: DNS and DHCP Verification

**Scenario:** A device is not resolving hostnames or getting an IP. Verify DNS and DHCP are working correctly. Manual verification — Python logs the outcome.

**Steps:**

1. Open DNS Manager on Windows Server 2022 — Server Manager > Tools > DNS
1. Expand the server > Forward Lookup Zones > corp.local
1. Check that an A record exists for DESKTOP-QL161MH pointing to 192.168.10.60
1. If missing — right click the zone > New Host (A) — enter the name and IP
1. Open DHCP Manager — Server Manager > Tools > DHCP
1. Expand the server > IPv4 > Scope > Address Leases
1. Confirm the Windows 11 VM has an active lease
1. On the Windows 11 VM, open Command Prompt and run:

```cmd
ipconfig /all
nslookup DESKTOP-QL161MH
```

1. Confirm the IP, subnet, gateway, and DNS server match the expected values
1. Open ServiceNow PDI and raise an Incident:
- Category: Network
- Short description: DNS and DHCP verified — [date]
- Note the INC number
1. Run the logger:

```bash
python scripts/logger.py --action DNSDHCPCheck --status success --ticket INC0010003 --actor Manual --target 192.168.10.60
```

1. Push to GitHub

**What Python does:** Logs the manual action

**Skills touched:** DNS, DHCP, Windows Server, Networking, Python logging, GitHub

-----

#### Day 5: Entra ID Licence Assignment

**Scenario:** A user needs a Microsoft 365 licence assigned. Python hits the Graph API to check and assign it.

**Steps:**

1. Open Azure Portal and go to Entra ID > Users
1. Find or create a test user — note their email address
1. Run the licence assignment script:

```bash
python scripts/licence_assign.py --email testuser@yourdomain.com --sku BUSINESS_BASIC
```

1. The script uses Microsoft Graph API to check the current licence status and assign if missing
1. Go back to Entra ID > Users > find the user > Licences
1. Confirm Microsoft 365 Business Basic is listed as assigned
1. Open ServiceNow PDI and raise an Incident:
- Category: Access
- Short description: M365 licence assigned for [Name]
- Note the INC number
1. The script logs automatically — verify the row in `logs/IT_Audit_Log.csv`
1. Push to GitHub

**What Python automates:** Graph API licence check and assignment, logging

**Skills touched:** Entra ID, Microsoft Graph API, Python, ServiceNow, GitHub

-----

#### Day 6: Account Lockout Investigation

**Scenario:** A user is locked out. Investigate the cause in Event Viewer, unlock the account using a Python script, and document it.

**Steps:**

1. Open Event Viewer on Windows Server 2022
1. Go to Windows Logs > Security
1. Filter by Event ID 4625 — note the account name, failure reason, and source workstation
1. Run the auto unlock script:

```bash
python scripts/auto_unlock.py
```

1. The script queries AD for all locked accounts, unlocks each one, and logs every action
1. Open PowerShell and verify no accounts remain locked:

```powershell
Search-ADAccount -LockedOut | Select-Object Name, LockedOut
```

1. Confirm the output is empty
1. Open ServiceNow PDI and raise an Incident:
- Category: Access
- Short description: Account lockout resolved — [Name]
- Note the INC number
1. Update the log with the ticket ID if the script did not capture it:

```bash
python scripts/logger.py --action AccountUnlock --status success --ticket INC0010004 --actor auto_unlock.py --target sarah.blake
```

1. Push to GitHub

**What Python automates:** AD lockout query, account unlock, logging

**Skills touched:** Event Viewer, Active Directory, PowerShell, Python, ServiceNow, GitHub

-----

#### Day 7: Bulk User Provisioning from CSV

**Scenario:** Five new starters join on the same day. A Python script reads a CSV file and creates all accounts automatically.

**Steps:**

1. Create `csv-inputs/new_starters.csv` with these columns:
- FirstName, LastName, Department, Group, Password
1. Add five realistic entries
1. Run the bulk provisioning script:

```bash
python scripts/bulk_provision.py --csv csv-inputs/new_starters.csv
```

1. The script reads each row, creates the AD user via WinRM, and logs a row for each one
1. Open Active Directory Users and Computers — confirm all five users exist
1. Open ServiceNow PDI and raise one Incident covering the whole batch:
- Category: Access
- Short description: Bulk provisioning — 5 new starters — [date]
- Note the INC number
1. Open `logs/IT_Audit_Log.csv` — confirm five rows were logged
1. Push the CSV, script, and updated log to GitHub

**What Python automates:** CSV parsing, AD user creation for all rows, per-user logging, error handling for invalid rows

**Skills touched:** Python, Active Directory, WinRM, CSV handling, ServiceNow, GitHub

-----

### Week 2 — Advanced Workflows

-----

#### Day 8: Firewall Rule Check and Remediation

**Scenario:** A service becomes unreachable. A firewall rule is suspected. Manually test, fix, and verify — Python logs the outcome.

**Steps:**

1. Open Windows Firewall with Advanced Security on Windows Server 2022
1. Go to Inbound Rules — find the rule for RDP (port 3389) or WinRM (port 5985)
1. Disable the rule deliberately — right click > Disable Rule
1. From the Windows 11 VM, try to RDP or connect via WinRM — confirm it fails
1. Go back to Windows Server — re-enable the rule
1. Retry the connection from Windows 11 VM — confirm it works
1. Open PowerShell and run:

```powershell
Get-NetFirewallRule | Where-Object { $_.Enabled -eq 'True' } | Select-Object DisplayName, Direction, Action | Format-Table
```

1. Confirm the rule is showing as enabled in the output
1. Open ServiceNow PDI and raise an Incident:
- Category: Network
- Short description: Firewall rule verified and restored — [date]
- Note the INC number
1. Run the logger:

```bash
python scripts/logger.py --action FirewallCheck --status success --ticket INC0010005 --actor Manual --target WindowsServer2022
```

1. Push to GitHub

**What Python does:** Logs the manual action

**Skills touched:** Windows Firewall, PowerShell, Networking, Python logging, ServiceNow, GitHub

-----

#### Day 9: Offboarding Workflow

**Scenario:** An employee is leaving. Their account needs disabling, groups removing, and the account moving to a Disabled Users OU. Python handles the AD changes automatically.

**Steps:**

1. Run the offboarding script — pass in the username:

```bash
python scripts/offboard_user.py --username sarah.blake
```

1. The script disables the account, removes all group memberships, and moves it to the Disabled Users OU
1. Open Active Directory Users and Computers and verify:
- Account is disabled — icon shows a downward arrow
- Member Of tab is empty
- Account is in the Disabled Users OU
1. Open Entra ID and confirm the account is also disabled or synced correctly
1. Open PowerShell and verify:

```powershell
Get-ADUser -Identity sarah.blake -Properties Enabled, MemberOf
```

1. Confirm Enabled = False and MemberOf is empty
1. Open ServiceNow PDI and raise an Incident:
- Category: Access
- Short description: Offboarding complete for Sarah Blake
- Note the INC number
1. The script logs automatically — verify the row in `logs/IT_Audit_Log.csv`
1. Push to GitHub

**What Python automates:** Account disable, group removal, OU move, logging

**Skills touched:** Active Directory, Entra ID, PowerShell, Python, ServiceNow, GitHub

-----

#### Day 10: PowerShell Log Analysis

**Scenario:** Review system health by exporting Windows Event Logs with PowerShell and analysing them with Python to produce a summary.

**Steps:**

1. Open PowerShell on Windows Server 2022 and export the last 20 system errors:

```powershell
Get-EventLog -LogName System -EntryType Error -Newest 20 | Select-Object TimeGenerated, Source, Message | Export-Csv -Path C:\logs\system_errors.csv -NoTypeInformation
```

1. Copy `system_errors.csv` to your local project folder under `logs/`
1. Run the log analyser script:

```bash
python scripts/log_analyser.py --input logs/system_errors.csv
```

1. The script reads the CSV, counts total errors, identifies the top 3 sources, and prints the most recent error
1. The summary is saved to `logs/health_checks.csv`
1. Review the output — note any recurring sources worth investigating
1. Open ServiceNow PDI and raise an Incident:
- Category: Infrastructure
- Short description: System log review — [date]
- Note the INC number
1. Run the logger:

```bash
python scripts/logger.py --action LogAnalysis --status success --ticket INC0010006 --actor log_analyser.py --target WindowsServer2022
```

1. Push everything to GitHub

**What Python automates:** CSV parsing, error counting, source analysis, summary output, logging

**Skills touched:** PowerShell, Python, Windows Event Logs, ServiceNow, GitHub

-----

#### Day 11: Linux SSH and System Check

**Scenario:** A Linux server needs a routine health check. SSH in from the Windows 11 VM, check services, review disk and logs, and create a test user. Python logs the outcome.

**Steps:**

1. Boot your Linux VM in VMware Workstation
1. Note the IP — run `ip a` in the Linux VM terminal and find the inet address
1. From the Windows 11 VM, open Command Prompt and SSH in:

```cmd
ssh username@[Linux VM IP]
```

1. Once in, check the SSH service is running:

```bash
systemctl status ssh
```

1. Check disk usage:

```bash
df -h
```

1. Check running processes and resource usage — press Q to exit:

```bash
top
```

1. Review the last 20 lines of the system log:

```bash
cat /var/log/syslog | tail -20
```

1. Create a test user:

```bash
sudo adduser testuser
```

1. Confirm the user was created:

```bash
cat /etc/passwd | grep testuser
```

1. Back on your Windows machine, run the logger:

```bash
python scripts/logger.py --action LinuxHealthCheck --status success --ticket INC0010007 --actor Manual --target [Linux VM IP]
```

1. Open ServiceNow PDI and raise an Incident:
- Category: Infrastructure
- Short description: Linux server health check — [date]
1. Push notes and log to GitHub

**What Python does:** Logs the manual action

**Skills touched:** Linux CLI, SSH, User Management, System Monitoring, VMware, Python logging, ServiceNow, GitHub

-----

#### Day 12: Exchange Online Mail Flow Validation

**Scenario:** Emails from a domain are being flagged or rejected. Verify SPF, DKIM, and MX records are correctly configured. Manual DNS checks — Python logs the outcome.

**Steps:**

1. Go to mxtoolbox.com — no login needed
1. Run MX Lookup for your Microsoft 365 domain — confirm records point to Microsoft
1. Run SPF Lookup — confirm the record includes `include:spf.protection.outlook.com`
1. Run DKIM Lookup — confirm selector records exist
1. Open Microsoft 365 Admin Centre > Settings > Domains
1. Confirm the domain status shows as healthy with no warnings
1. Open ServiceNow PDI and raise an Incident:
- Category: Email
- Short description: Mail flow DNS validation — [date]
- Note the INC number
1. Run the logger:

```bash
python scripts/logger.py --action MailflowCheck --status success --ticket INC0010008 --actor Manual --target yourdomain.com
```

1. Push to GitHub

**What Python does:** Logs the manual action

**Skills touched:** DNS, Microsoft 365, Email Security, Python logging, ServiceNow, GitHub

-----

#### Day 13: Python Script Hardening

**Scenario:** The scripts built across the lab work but are not production ready. Today you harden them — proper error handling, input validation, and secrets management.

**Steps:**

1. Open `scripts/provision_user.py`
1. Wrap the main logic in a try/except block:

```python
try:
    # existing logic here
except Exception as e:
    log_action("ProvisionUser", "failure", "N/A", "provision_user.py", target, str(e))
    print(f"[ERROR] {e}")
```

1. Add input validation — if any required field is empty, raise a ValueError with a clear message
1. Create a `.env` file in the root of the project:

```
SERVER_IP=192.168.128.130
DOMAIN=corp.local
ADMIN_USER=Administrator
ADMIN_PASS=yourpassword
```

1. Install python-dotenv if not already installed:

```bash
pip install python-dotenv
```

1. Add this to the top of the script:

```python
from dotenv import load_dotenv
import os
load_dotenv()
server_ip = os.getenv("SERVER_IP")
```

1. Confirm `.env` is listed in `.gitignore` — open the file and check
1. Retest the script — confirm it still works with the values loading from `.env`
1. Repeat for a second script
1. Push hardened scripts to GitHub — confirm `.env` does not appear in the commit

**What Python does:** This entire day is Python focused

**Skills touched:** Python, Error Handling, Security Best Practices, dotenv, GitHub

-----

#### Day 14: Shift Simulation

**Scenario:** You are covering a support shift. Work through five tickets in order. Each one must be fully resolved and closed in ServiceNow before moving to the next. Log everything.

**Ticket Queue:**

**Ticket 1 — New starter**
Create AD account for James.Okafor, department = Finance, assign to Finance group, assign M365 licence via Python script

**Ticket 2 — Locked account**
Sarah.Blake is locked out — check Event Viewer for Event ID 4625, run auto_unlock.py, verify with PowerShell

**Ticket 3 — Connectivity**
A user cannot reach the server — run connectivity_check.py against 192.168.128.130, review the evidence file, document findings

**Ticket 4 — Offboarding**
A contractor’s account needs disabling — run offboard_user.py, verify in AD and Entra ID, confirm groups are cleared

**Ticket 5 — Health check**
Export system errors with PowerShell, run log_analyser.py, confirm no critical unresolved errors

**Rules:**

- Raise a real ServiceNow Incident for each ticket
- Log every action to `IT_Audit_Log.csv`
- Close the ServiceNow ticket before moving to the next one
- Push everything to GitHub at the end with a single commit

**Skills touched:** Active Directory, Entra ID, PowerShell, Python, ServiceNow, Networking, Windows Server, GitHub

-----

## Looping the Lab

After Day 14, restart at Day 1 with harder constraints:

- **Loop 2:** Introduce a deliberate error in each scenario — wrong group, incorrect IP, missing licence. Find and fix it before logging
- **Loop 3:** Add a 20-minute time limit per task
- **Loop 4:** Day 14 Shift Simulation only — five tickets, no notes, from memory

-----

## Skills Covered

-----

### Active Directory

- User Provisioning
- Account Management
- Group Membership
- Role-Based Access Control
- Organisational Units
- Security Groups
- Account Lockout Investigation
- Bulk User Provisioning
- Offboarding

-----

### Windows Server 2022

- Event Viewer
- Event ID Analysis
- DNS Manager
- DHCP Manager
- Windows Firewall
- Inbound and Outbound Rules
- PowerShell — Get-ADUser, Search-ADAccount, Get-NetFirewallRule, Get-EventLog, Export-Csv

-----

### Networking

- DNS Resolution
- DHCP Lease Verification
- Ping / Tracert / Nslookup
- IP Configuration
- Virtual Networking in VMware

-----

### VMware Workstation

- VM Health Checks
- Network Adapter Configuration
- Remote Desktop Protocol
- WinRM

-----

### Microsoft 365

- Entra ID
- Licence Assignment
- Account Management
- Microsoft Graph API
- Exchange Online
- SPF / DKIM / MX Records
- Mail Flow Validation
- Microsoft 365 Admin Centre

-----

### ServiceNow

- Incident Creation
- Incident Updates
- Incident Closure
- ITSM Workflow

-----

### Linux

- SSH
- Systemctl
- Disk Usage
- Process Monitoring
- User Management
- System Log Reading
- Bash Navigation

-----

### Python

- CSV Reading and Writing
- WinRM Integration
- REST API Calls
- Error Handling
- Input Validation
- Environment Variables with dotenv
- Subprocess
- Modular Scripting
- Audit Logging Automation

-----

### GitHub

- Git Init / Add / Commit / Push
- Repository Structure
- gitignore Configuration
- Version Control Habits

-----

## Audit Trail

Every task must produce a log row in `logs/IT_Audit_Log.csv` using the Python logger script.
See `LOGGING.md` for the full schema and setup.
