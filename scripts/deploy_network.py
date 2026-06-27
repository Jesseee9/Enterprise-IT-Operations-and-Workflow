import os
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from logger import log_action

load_dotenv()

SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP")
LOCATION = os.getenv("AZURE_LOCATION")

credential = ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
resource_client = ResourceManagementClient(credential, SUBSCRIPTION_ID)
network_client = NetworkManagementClient(credential, SUBSCRIPTION_ID)

def deploy_network():
    try:
        print("[*] Creating resource group...")
        resource_client.resource_groups.create_or_update(RESOURCE_GROUP, {"location": LOCATION})
        print(f"[+] Resource group {RESOURCE_GROUP} created")

        print("[*] Creating VNet...")
        vnet_params = {
            "location": LOCATION,
            "address_space": {"address_prefixes": ["10.0.0.0/16"]}
        }
        network_client.virtual_networks.begin_create_or_update(RESOURCE_GROUP, "vnet-it-ops", vnet_params).result()
        print("[+] VNet created — 10.0.0.0/16")

        print("[*] Creating subnet...")
        subnet_params = {"address_prefix": "10.0.1.0/24"}
        network_client.subnets.begin_create_or_update(RESOURCE_GROUP, "vnet-it-ops", "subnet-public", subnet_params).result()
        print("[+] Subnet created — 10.0.1.0/24")

        print("[*] Creating NSG...")
        nsg_params = {
            "location": LOCATION,
            "security_rules": [
                {
                    "name": "Allow-SSH",
                    "properties": {
                        "priority": 100,
                        "protocol": "Tcp",
                        "access": "Allow",
                        "direction": "Inbound",
                        "source_address_prefix": "*",
                        "source_port_range": "*",
                        "destination_address_prefix": "*",
                        "destination_port_range": "22"
                    }
                },
                {
                    "name": "Deny-All-Inbound",
                    "properties": {
                        "priority": 200,
                        "protocol": "*",
                        "access": "Deny",
                        "direction": "Inbound",
                        "source_address_prefix": "*",
                        "source_port_range": "*",
                        "destination_address_prefix": "*",
                        "destination_port_range": "*"
                    }
                }
            ]
        }
        network_client.network_security_groups.begin_create_or_update(RESOURCE_GROUP, "nsg-it-ops", nsg_params).result()
        print("[+] NSG created — port 22 open, all other inbound denied")

        print("[*] Verifying NSG rules...")
        nsg = network_client.network_security_groups.get(RESOURCE_GROUP, "nsg-it-ops")
        for rule in nsg.security_rules:
            print(f"    Rule: {rule.name} — {rule.access} — port {rule.destination_port_range}")

        log_action("AzureNetworkProvision", "success", "PENDING", "deploy_network.py", "Azure-uksouth", "VNet 10.0.0.0/16, subnet 10.0.1.0/24, NSG with SSH allow and deny-all created and verified")

        print("[*] Tearing down resource group...")
        resource_client.resource_groups.begin_delete(RESOURCE_GROUP).result()
        print(f"[+] Resource group {RESOURCE_GROUP} deleted — zero ongoing cost")

    except Exception as e:
        log_action("AzureNetworkProvision", "failure", "N/A", "deploy_network.py", "Azure-uksouth", str(e))
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    deploy_network()
