# Production Configuration Guide

This document covers how to deploy the Enterprise IT Operations and Workflow environment from scratch. Follow each section in order before running any scripts.

---

## Prerequisites

- Windows Server 2022 VM with Active Directory Domain Services installed and configured
- Windows 11 VM on the same VMware network (VMnet2)
- VMware Workstation installed on the host machine
- Python 3.10 or later installed on the host machine
- Git installed on the host machine
- A ServiceNow Personal Developer Instance (PDI) — register free at developer.servicenow.com
- A Microsoft Entra ID tenant — free tier is sufficient

---

## 1. VMware Network Configuration

Both VMs must be on the same host-only network to communicate.

- Open VMware Workstation
- Go to Edit > Virtual Network Editor
- Confirm VMnet2 exists as a Host-only network
- Assign Windows Server 2022 adapter to VMnet2
- Assign Windows 11 VM adapter to VMnet2
- Windows Server static IP: 192.168.10.50
- Windows 11 VM IP: assigned via DHCP from the server (expected: 192.168.10.60)

---

## 2. WinRM Configuration on Windows Server

WinRM allows Python scripts on the host machine to execute PowerShell commands remotely on the server.

Run the following on Windows Server 2022 PowerShell as Administrator:

```powershell
# Enable WinRM
Enable-PSRemoting -Force

# Set authentication to Basic
winrm set winrm/config/service/auth '@{Basic="true"}'

# Allow unencrypted traffic (required for HTTP on internal lab network)
winrm set winrm/config/service '@{AllowUnencrypted="true"}'

# Confirm WinRM is listening
winrm enumerate winrm/config/listener
```
Verify from the host machine:
Test-WSMan -ComputerName 192.168.10.50
A successful response confirms WinRM is reachable.

3. Active Directory Requirements
The execution account used by the scripts requires the following AD permissions:
	•	Member of the Domain Admins group, or delegated permissions to:
	◦	Create and disable user accounts
	◦	Modify group membership
	◦	Move objects between OUs
	◦	Read all user properties
The following Organisational Units must exist in corp.local:
OU
Purpose
Users (default)
Active user accounts
Disabled Users
Offboarded accounts moved here by offboard_user.py
To create the Disabled Users OU if missing:
New-ADOrganizationalUnit -Name "Disabled Users" -Path "DC=corp,DC=local"
The following Security Groups must exist:
Group
Used by
IT-Staff
provision_user.py, bulk_provision.py
Sales-Staff
bulk_provision.py
HR-Staff
bulk_provision.py
Finance-Staff
bulk_provision.py
To create missing groups:
New-ADGroup -Name "IT-Staff" -GroupScope Global -GroupCategory Security
New-ADGroup -Name "Sales-Staff" -GroupScope Global -GroupCategory Security
New-ADGroup -Name "HR-Staff" -GroupScope Global -GroupCategory Security
New-ADGroup -Name "Finance-Staff" -GroupScope Global -GroupCategory Security

4. ServiceNow PDI Configuration
	•	Register at developer.servicenow.com and request a Personal Developer Instance
	•	Note your instance ID (e.g. dev268884)
	•	Log in and confirm the instance is active — PDIs hibernate after inactivity, wake them from the developer portal
	•	The scripts use the Table REST API — no additional plugins required on a standard PDI
	•	Valid close_code for incident resolution on this PDI: Solution provided

5. Microsoft Entra ID Configuration
	•	Log in to entra.microsoft.com
	•	Register a new App Registration — name it anything (e.g. IT Lab Script)
	•	Under API Permissions, add Microsoft Graph application permissions:
	◦	User.ReadWrite.All
	◦	Directory.ReadWrite.All
	•	Grant admin consent
	•	Under Certificates and Secrets, create a new Client Secret — copy the value immediately
	•	Note the Application (Client) ID and Directory (Tenant) ID from the Overview page

6. Environment Variables
Create a .env file in the project root. This file is excluded from GitHub via .gitignore — never commit it.
SN_INSTANCE=your_servicenow_instance_id
SN_USER=admin
SN_PASSWORD=your_pdi_password
SERVER_IP=192.168.10.50
DOMAIN=corp.local
ADMIN_USER=Administrator
ADMIN_PASS=your_server_admin_password
AZURE_TENANT_ID=your_entra_tenant_id
AZURE_CLIENT_ID=your_app_registration_client_id
AZURE_CLIENT_SECRET=your_client_secret_value

7. Python Dependencies
Install required packages from the project root:
pip install pywinrm python-dotenv requests msal

8. Verify the Setup
Run this check from the project root to confirm everything is connected:
python scripts/connectivity_check.py --target 192.168.10.50
A successful run confirms WinRM connectivity, ServiceNow API access, and audit logging are all working.

Security Notes
	•	Never hardcode credentials in any script — always use .env and os.getenv()
	•	Never commit .env to GitHub — confirm .gitignore excludes it before every push
	•	WinRM is configured for HTTP on an isolated internal lab network — in a production environment use HTTPS with a valid certificate
	•	Client secrets in Entra ID expire — check expiry dates and rotate before they lapse

## Workflows

For full step-by-step runbooks for every workflow in this lab, see the Workflow.md workflow sections. Each workflow documents the exact commands, what Python automates, manual steps required, and skills demonstrated.
