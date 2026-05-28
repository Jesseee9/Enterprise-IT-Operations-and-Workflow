# IT Ops Training Lab

A 14-day repeatable workflow simulating a production MSP environment.  
Covers Active Directory, networking, Microsoft 365, Entra ID, Linux, PowerShell, and Python automation — all connected as real workflows, not isolated tasks.

-----

## Daily Structure

|Block                |Time     |What You Do                                                                                                                                                                |
|---------------------|---------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|**Warm-up**          |10 min   |Check VMware VMs are running. Verify Windows Server 2022 (192.168.128.130) and Windows 11 VM (192.168.10.60) are reachable. Open ServiceNow PDI and confirm you can log in.|
|**Main Task**        |60–90 min|Follow the day’s steps exactly. Every action must be deliberate — treat it as a real support ticket.                                                                       |
|**Python/Automation**|20–30 min|Run or write the corresponding script from `AUTOMATION.md`. Log results to `logs/IT_Audit_Log.csv` using the logger script.                                                |
|**Commit**           |10 min   |Stage and push changes to GitHub. Write a meaningful commit message describing what you did.                                                                               |

-----

## 14-Day Calendar

-----

### Week 1 — Core IT Support Workflows

-----

#### Day 1: New Starter Provisioning

**Scenario:** A new employee joins the company. You need to create their AD account, assign them to the correct group, create a ServiceNow ticket, and log the action.

**Steps:**

1. Open Active Directory Users and Computers on Windows Server 2022 VM
1. Create a new user in the `corp.local` domain — use a realistic name (e.g. Sarah.Blake)
1. Set a temporary password and tick “User must change password at next logon”
1. Add the user to the correct security group based on their department (e.g. `IT-Staff` or `Sales`)
1. Open ServiceNow PDI and create an Incident ticket: category = Access, short description = “New starter account created for [Name]”
1. Note the ticket ID
1. Run the Python provisioning logger script — pass in the username, department, ticket ID
1. Verify the log row has been added to `logs/IT_Audit_Log.csv`
1. Push to GitHub

**Skills touched:** Active Directory, ServiceNow, Python logging, GitHub

-----

#### Day 2: Connectivity Troubleshooting

**Scenario:** A user reports they cannot reach a network resource. You need to diagnose and document the issue.

**Steps:**

1. From your Windows 11 VM, open Command Prompt
1. Run `ping 192.168.128.130` — note the result
1. Run `nslookup corp.local` — confirm DNS is resolving
1. Run `tracert 192.168.128.130` — save the output
1. If ping fails, check VMware network adapter settings — confirm both VMs are on the same virtual network
1. Create a ServiceNow Incident: category = Network, short description = “Connectivity check — [date]”
1. Run the Python connectivity check script — pass in the target IP, save stdout to evidence
1. Log the result to `logs/IT_Audit_Log.csv`
1. Push to GitHub

**Skills touched:** Networking, DNS, VMware, Python automation, ServiceNow

-----

#### Day 3: Group Membership and Role-Based Access

**Scenario:** A user’s role has changed. You need to update their group membership and verify their access level is correct.

**Steps:**

1. Open Active Directory Users and Computers
1. Find the user created on Day 1
1. Remove them from their current group
1. Add them to a different group (e.g. move from `Sales` to `IT-Staff`)
1. Open PowerShell on the server and run: `Get-ADUser -Identity Sarah.Blake -Properties MemberOf | Select-Object MemberOf`
1. Confirm the output matches the intended group
1. Create a ServiceNow Incident: category = Access, short description = “Group membership updated for [Name]”
1. Run Python logger — log action = GroupUpdate, target = username, ticket ID
1. Push to GitHub

**Skills touched:** Active Directory, PowerShell, ServiceNow, Python logging

-----

#### Day 4: DNS and DHCP Verification

**Scenario:** A device is not getting an IP or resolving hostnames. You need to verify DNS and DHCP are functioning correctly.

**Steps:**

1. Open DNS Manager on Windows Server 2022
1. Confirm an A record exists for your Windows 11 VM hostname
1. If missing, create it manually — right click Forward Lookup Zone > New Host
1. Open DHCP Manager — check the scope leases, confirm Windows 11 VM has a lease
1. From Windows 11 VM, run `ipconfig /all` — confirm IP, subnet, gateway, and DNS server
1. Run `nslookup DESKTOP-QL161MH` from Windows 11 VM — should resolve
1. Create a ServiceNow Incident: category = Network, short description = “DNS/DHCP verified — [date]”
1. Run Python DNS/DHCP check script
1. Log to CSV and push to GitHub

**Skills touched:** DNS, DHCP, Windows Server, networking fundamentals, Python

-----

#### Day 5: Entra ID Licence Assignment

**Scenario:** A new user needs a Microsoft 365 licence assigned. You need to verify the account exists in Entra ID and assign the correct licence.

**Steps:**

1. Open Azure Portal — go to Entra ID > Users
1. Find or create a test user
1. Go to Licences > Assignments — assign Microsoft 365 Business Basic
1. Open PowerShell and run the `entra_id.py` script (already built): look up the user, check licence status
1. Confirm licence shows as assigned in the script output
1. Create a ServiceNow Incident: category = Access, short description = “Licence assigned for [Name]”
1. Run Python logger — log action = LicenceAssign, target = user email
1. Push to GitHub

**Skills touched:** Entra ID, Microsoft Graph API, Python, ServiceNow

-----

#### Day 6: Account Lockout Investigation

**Scenario:** A user is locked out of their account. You need to identify the cause, unlock the account, and document it.

**Steps:**

1. Open Event Viewer on Windows Server 2022
1. Go to Windows Logs > Security — filter by Event ID 4625 (failed logon)
1. Note the account name, failure reason, and source workstation
1. Open Active Directory Users and Computers — find the locked account
1. Right click > Properties > Account tab — tick “Unlock account”
1. Open PowerShell and run: `Search-ADAccount -LockedOut | Select-Object Name, LockedOut`
1. Confirm no remaining locked accounts
1. Create a ServiceNow Incident: category = Access, short description = “Account lockout resolved for [Name]”
1. Run Python logger — log action = AccountUnlock
1. Push to GitHub

**Skills touched:** Event Viewer, Active Directory, PowerShell, ServiceNow, Python

-----

#### Day 7: Bulk User Provisioning from CSV

**Scenario:** Five new starters join on the same day. You need to create all accounts from a CSV file using a Python script.

**Steps:**

1. Create a file called `new_starters.csv` with columns: FirstName, LastName, Department, Group
1. Add five realistic entries
1. Write or run a Python script that reads the CSV and creates each AD user via WinRM (same method as Ren’s AD manager)
1. For each user created, log a row to `IT_Audit_Log.csv`
1. Create one ServiceNow Incident summarising the bulk provisioning: “Bulk provisioning completed — 5 users — [date]”
1. Verify all five users appear in Active Directory Users and Computers
1. Push CSV, script, and log to GitHub

**Skills touched:** Python (CSV, WinRM), Active Directory, ServiceNow, bulk operations

-----

### Week 2 — Advanced Workflows

-----

#### Day 8: Firewall Rule Check and Remediation

**Scenario:** A service is unreachable. You suspect a firewall rule is blocking traffic. You need to identify, test, and fix it.

**Steps:**

1. Open Windows Firewall with Advanced Security on Windows Server 2022
1. Find an inbound rule for a relevant port (e.g. RDP port 3389 or WinRM port 5985)
1. Disable the rule deliberately
1. From Windows 11 VM, try to connect — confirm it fails
1. Re-enable the rule
1. Confirm the connection works again
1. Open PowerShell and run: `Get-NetFirewallRule | Where-Object { $_.Enabled -eq 'True' } | Select-Object DisplayName, Direction, Action | Format-Table`
1. Create a ServiceNow Incident: category = Network, short description = “Firewall rule verified and restored — [date]”
1. Run Python logger — log action = FirewallCheck
1. Push to GitHub

**Skills touched:** Windows Firewall, PowerShell, networking, Python logging, ServiceNow

-----

#### Day 9: Offboarding Workflow

**Scenario:** An employee is leaving. You need to disable their account, remove group memberships, and document the offboarding.

**Steps:**

1. Open Active Directory Users and Computers
1. Find the user to offboard
1. Disable the account — right click > Disable Account
1. Remove all group memberships — Properties > Member Of > Remove all
1. Move the account to a Disabled Users OU (create one if it does not exist)
1. Open Entra ID — confirm the account is also disabled or synced correctly
1. Open PowerShell and run: `Get-ADUser -Identity [username] -Properties Enabled, MemberOf`
1. Confirm Enabled = False and MemberOf is empty
1. Create a ServiceNow Incident: category = Access, short description = “Offboarding complete for [Name]”
1. Run Python offboard logger script
1. Push to GitHub

**Skills touched:** Active Directory, Entra ID, PowerShell, ServiceNow, Python

-----

#### Day 10: PowerShell Log Analysis

**Scenario:** You need to review system health by parsing Windows Event Logs using PowerShell and Python, then generate a summary.

**Steps:**

1. Open PowerShell on Windows Server 2022
1. Run: `Get-EventLog -LogName System -EntryType Error -Newest 20 | Select-Object TimeGenerated, Source, Message | Export-Csv -Path C:\logs\system_errors.csv -NoTypeInformation`
1. Open the CSV and review the errors
1. Write or run a Python script that reads `system_errors.csv` and prints a summary: total errors, top 3 sources, most recent error
1. Save the summary output to `logs/health_checks.csv`
1. Create a ServiceNow Incident: category = Infrastructure, short description = “System log review — [date]”
1. Push CSV, script output, and log to GitHub

**Skills touched:** PowerShell, Python (CSV parsing), Windows Event Logs, ServiceNow

-----

#### Day 11: Linux SSH and Service Check

**Scenario:** A Linux server needs checking. You need to SSH in, verify services are running, and review logs.

**Steps:**

1. Use KillerCoda (killercoda.com) to launch a free Ubuntu instance — no setup needed
1. SSH in or use the browser terminal
1. Run: `systemctl status ssh` — confirm the service is active
1. Run: `df -h` — check disk usage
1. Run: `top` — review CPU and memory, then press Q to exit
1. Run: `cat /var/log/syslog | tail -20` — review the last 20 log lines
1. Create a new user on the Linux machine: `sudo adduser testuser`
1. Confirm the user was created: `cat /etc/passwd | grep testuser`
1. Back in your lab, run Python logger — log action = LinuxHealthCheck, target = KillerCoda instance
1. Create a ServiceNow Incident: category = Infrastructure, short description = “Linux server health check — [date]”
1. Push notes and log to GitHub

**Skills touched:** Linux CLI, SSH, user management, system monitoring, Python logging, ServiceNow

-----

#### Day 12: Exchange Online Mail Flow Validation

**Scenario:** Emails from a domain are being rejected. You need to verify SPF, DKIM, and MX records are correctly configured.

**Steps:**

1. Go to MXToolbox (mxtoolbox.com) — no login needed
1. Enter your Microsoft 365 tenant domain (your M365 domain from GTS or your test tenant)
1. Run MX Lookup — confirm MX records point to Microsoft
1. Run SPF Lookup — confirm the SPF record includes `include:spf.protection.outlook.com`
1. Run DKIM Lookup — confirm DKIM selector records exist
1. In Microsoft 365 Admin Centre, go to Settings > Domains — verify the domain status shows as healthy
1. Create a ServiceNow Incident: category = Email, short description = “Mail flow DNS validation — [date]”
1. Run Python logger — log action = MailflowCheck, target = domain
1. Push notes and log to GitHub

**Skills touched:** DNS, Microsoft 365, email security, Python logging, ServiceNow

-----

#### Day 13: Python Script Hardening

**Scenario:** Your automation scripts work but are not production-ready. Today you harden them — add error handling, input validation, and move secrets to environment variables.

**Steps:**

1. Open one of your existing Python scripts (start with the provisioning logger)
1. Wrap the main logic in a `try/except` block — catch at minimum `Exception as e` and log the error to the CSV
1. Add input validation — if a required field is missing or empty, raise a `ValueError` with a clear message
1. Move any hardcoded credentials or IPs to a `.env` file
1. Install `python-dotenv` if not already installed: `pip install python-dotenv`
1. Load the `.env` file at the top of the script: `from dotenv import load_dotenv`
1. Add `.env` to `.gitignore` — confirm it is not being committed
1. Retest the script — confirm it still works and the `.env` values are loading correctly
1. Repeat for a second script
1. Push hardened scripts to GitHub

**Skills touched:** Python (error handling, dotenv, validation), security best practices, GitHub

-----

#### Day 14: Shift Simulation

**Scenario:** You are covering a full IT support shift. Work through the following five tickets in order. Each one must be resolved, documented, and logged before moving to the next.

**Ticket Queue:**

1. **Ticket 1 — New starter:** Create AD account for James.Okafor, department = Finance, assign to Finance group, assign M365 licence
1. **Ticket 2 — Locked account:** Sarah.Blake has been locked out — investigate Event Viewer, unlock the account, document cause
1. **Ticket 3 — Connectivity:** A user cannot reach the server — run ping, nslookup, tracert from Windows 11 VM, document results
1. **Ticket 4 — Offboarding:** A contractor’s account needs disabling — disable in AD and Entra ID, remove groups, move to Disabled OU
1. **Ticket 5 — Health check:** Run PowerShell event log export and Python summary script — confirm no critical errors

**Rules:**

- Create a real ServiceNow Incident for each ticket
- Log every action to `IT_Audit_Log.csv` using your Python logger
- Do not move to the next ticket until the current one is closed in ServiceNow
- Push everything to GitHub at the end

**Skills touched:** Active Directory, Entra ID, ServiceNow, PowerShell, Python logging, VMware, Windows Server, GitHub

-----

## Looping the Lab

After Day 14, restart at Day 1 with harder constraints:

- **Loop 2:** Introduce a deliberate error in each scenario (wrong group, incorrect IP, expired licence) — find and fix it
- **Loop 3:** Add a time limit — complete each task within 20 minutes
- **Loop 4:** Do Day 14 Shift Simulation only — four tickets, no notes, from memory

-----

## Skills Covered

---

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

---

### Windows Server 2022
- Event Viewer
- Event ID Analysis
- DNS Manager
- DHCP Manager
- Windows Firewall
- Inbound and Outbound Rules
- PowerShell — Get-ADUser, Search-ADAccount, Get-NetFirewallRule, Get-EventLog, Export-Csv

---

### Networking
- DNS Resolution
- DHCP Lease Verification
- Ping / Tracert / Nslookup
- IP Configuration
- Virtual Networking in VMware

---

### VMware Workstation
- VM Health Checks
- Network Adapter Configuration
- Remote Desktop Protocol
- WinRM

---

### Microsoft 365
- Entra ID
- Licence Assignment
- Account Management
- Microsoft Graph API
- Exchange Online
- SPF / DKIM / MX Records
- Mail Flow Validation
- Microsoft 365 Admin Centre

---

### ServiceNow
- Incident Creation
- Incident Updates
- Incident Closure
- ITSM Workflow

---

### Linux
- SSH
- Systemctl
- Disk Usage
- Process Monitoring
- User Management
- System Log Reading
- Bash Navigation

---

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

---

### GitHub
- Git Init / Add / Commit / Push
- Repository Structure
- gitignore Configuration
- Version Control Habits
-----

## Audit Trail

Every task must produce a log row in `logs/IT_Audit_Log.csv` using the Python logger script.  
See `LOGGING.md` for the full schema.
