# Automation Opportunities

Use these specifications to write or generate scripts in Python.  
Every script must log its output to `logs/IT_Audit_Log.csv` using the shared logger module.  
All credentials, IPs, and secrets must be stored in `.env` — never hardcoded.

-----

## Shared Logger Module

All scripts import this. Create it once at `scripts/logger.py`.

**What it does:** Appends a row to `logs/IT_Audit_Log.csv`  
**Inputs:** action, status, ticket_id, actor, target, notes  
**Output:** New row written to CSV  
**Success criteria:** CSV row exists with correct timestamp and all fields populated

-----

## Script Specifications

|Script                |File                           |Inputs                               |Output                                       |Success Criteria                       |
|----------------------|-------------------------------|-------------------------------------|---------------------------------------------|---------------------------------------|
|**Provision User**    |`scripts/provision_user.py`    |First, Last, Dept, Group, Password   |AD object created, ServiceNow ticket, log row|AD user exists, CSV row added          |
|**Connectivity Check**|`scripts/connectivity_check.py`|Target IP or FQDN                    |Ping/nslookup results, health log row        |Reachable = True, evidence saved       |
|**Auto Unlock**       |`scripts/auto_unlock.py`       |None — queries AD for locked accounts|List of unlocked accounts, log rows          |Locked list empty after run            |
|**Bulk Provision**    |`scripts/bulk_provision.py`    |CSV file path                        |Per-user status printed, log rows            |All valid rows processed, errors caught|
|**DNS/DHCP Check**    |`scripts/dns_dhcp_check.py`    |Hostname                             |A record status, DHCP lease info, log row    |DNS resolves, lease confirmed          |
|**Licence Assign**    |`scripts/licence_assign.py`    |User email, SKU ID                   |Licence status, log row                      |User has licence, log updated          |
|**Firewall Verifier** |`scripts/firewall_check.py`    |Rule name or port                    |Rule status, log row                         |Rule state confirmed and logged        |
|**Log Analyser**      |`scripts/log_analyser.py`      |Path to exported Event Log CSV       |Summary printed, health_checks.csv row       |Summary generated, errors counted      |
|**Mailflow Validator**|`scripts/mailflow_check.py`    |Domain name                          |MX/SPF/DKIM status printed, log row          |All records valid or issues flagged    |
|**Health Check**      |`scripts/health_check.py`      |List of server IPs                   |Health CSV rows, printed summary             |All checks run, no unlogged failures   |
|**Offboard User**     |`scripts/offboard_user.py`     |Username                             |Account disabled, groups removed, log row    |Enabled = False, MemberOf empty        |

-----

## Implementation Notes

- Use `pywinrm` for all AD operations (same approach as Ren’s AD manager)
- Use `requests` for ServiceNow REST API calls
- Use `python-dotenv` for all secrets and IPs
- Use `subprocess` for running PowerShell commands where needed
- Wrap all external calls in `try/except` — catch failures and log them with status = `failure`
- Print a confirmation message to stdout on success so you can see it worked

-----

## Where Python Adds the Most Value in This Lab

These are the tasks where writing Python is worth your time:

1. **Logging** — every task. One shared logger means you never manually edit a CSV
1. **Bulk operations** — Day 7 bulk provisioning is the clearest example. Manual AD creation for 5 users takes 20 minutes. The script takes 10 seconds
1. **Querying state** — checking if a user exists, if a licence is assigned, if an account is locked. Python hits the API and gives you a clean answer
1. **Log analysis** — parsing Event Log exports and producing a summary. PowerShell exports it, Python reads and summarises it
1. **Connectivity checks** — running ping/nslookup programmatically and saving the result means you have evidence without manually copying terminal output