# Python Command Reference

All Python commands used in the Enterprise IT Operations and Workflow environment. Run every command from the project root: `C:\My Projects\IT Practice Lab`

---

## User Provisioning

**Provision a single new AD user:**
```bash
python scripts/provision_user.py --first [FirstName] --last [LastName] --dept [Department] --group [GroupName] --password [Password]
```
Example:
python scripts/provision_user.py --first Sarah --last Blake --dept Sales --group Sales-Staff --password Welcome@2026!

Bulk Provisioning
Provision multiple users from a CSV file:
python scripts/bulk_provision.py --csv csv-inputs/new_starters.csv
CSV format required:
FirstName,LastName,Department,Group,Password

Account Lockout
Query all locked AD accounts, unlock each one, raise and resolve a ServiceNow incident:
python scripts/auto_unlock.py

Offboarding
Disable account, remove all group memberships, move to Disabled Users OU:
python scripts/offboard_user.py --username [SamAccountName]
Example:
python scripts/offboard_user.py --username sarah.blake

Entra ID
Create a new Entra ID user via Microsoft Graph API:
python scripts/entra_provision.py --display "[Display Name]" --upn [UPN] --password [Password]
Example:
python scripts/entra_provision.py --display "Test Contractor" --upn testcontractor@yourdomain.onmicrosoft.com --password TempPass1!
Look up an existing Entra ID user:
python scripts/entra_lookup.py --upn [UPN]
Example:
python scripts/entra_lookup.py --upn testcontractor@yourdomain.onmicrosoft.com

Connectivity Check
Run ping, nslookup, and tracert against a target — saves evidence and raises a ServiceNow incident:
python scripts/connectivity_check.py --target [IP or hostname]
Example:
python scripts/connectivity_check.py --target 192.168.10.50

Log Analysis
Analyse an exported Windows Event Log CSV and produce a health summary:
python scripts/log_analyser.py --input logs/system_errors.csv

Manual Logging
Log a manual action to IT_Audit_Log.csv:
python scripts/logger.py --action [ActionName] --status [success|failure] --ticket [INC number] --actor [Manual] --target [target]
Examples:
python scripts/logger.py --action GroupUpdate --status success --ticket INC0010003 --actor Manual --target sarah.blake

python scripts/logger.py --action FirewallCheck --status success --ticket INC0010014 --actor Manual --target WindowsServer2022

python scripts/logger.py --action DNSDHCPCheck --status success --ticket INC0010004 --actor Manual --target 192.168.10.60

python scripts/logger.py --action LinuxHealthCheck --status success --ticket INC0010017 --actor Manual --target 192.168.10.70

GitHub
Standard push after every completed workflow:
git add .
git commit -m "Day X — [task name] — [INC number]"
git push origin main
If push is rejected due to remote changes:
git pull origin main --rebase
git push origin main
