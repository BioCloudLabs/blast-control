import os

from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from dotenv import load_dotenv
import random

load_dotenv()

def generate_random_vmname(length):
    characters = '0123456789abcdefghijklmnopqrstuvwxyz'
    return ''.join(random.choices(characters, k=length))

# Retrieve subscription ID from environment variable.
SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]

# Constants we need in multiple places: the resource group name and
# the region in which we provision resources. You can change these
# values however you want.
RESOURCE_GROUP_NAME = "blast"
LOCATION = "westeurope"

# Network and IP address names
VM_NAME = generate_random_vmname(10)

VNET_NAME = f"{VM_NAME}-vnet"
SUBNET_NAME = f"{VM_NAME}-subnet"
IP_NAME = f"{VM_NAME}-ip"
IP_CONFIG_NAME = f"{VM_NAME}-ip-config"
NIC_NAME = f"{VM_NAME}-nic"
NSG_NAME = 'blast-nsg'

USERNAME = "azureuser"
PASSWORD = "ChangePa$$w0rd24"

def get_nsg_id_by_name(subscription_id, resource_group_name, nsg_name):
    credential = DefaultAzureCredential()
    network_client = NetworkManagementClient(credential, subscription_id)
    network_client._config.enable_http_logger = True

    nsg = network_client.network_security_groups.get(
        resource_group_name,
        nsg_name
    )

    return nsg.id if nsg else None

def associate_vm_with_nsg(subscription_id, resource_group_name, vm_name, nsg_id):
    credential = DefaultAzureCredential()
    compute_client = ComputeManagementClient(credential, subscription_id)
    network_client = NetworkManagementClient(credential, subscription_id)
    network_client._config.enable_http_logger = True

    # Get the VM
    vm = compute_client.virtual_machines.get(resource_group_name, vm_name)

    # Get the NIC ID of the VM
    nic_id = vm.network_profile.network_interfaces[0].id

    try:
        # Attempt to get the NIC

        # Get the NIC name from the NIC ID
        nic_name = nic_id.split('/')[-1]

        # Get the NIC
        nic = network_client.network_interfaces.get(resource_group_name, nic_name)
        
        # Update the NIC with the NSG
        nic.network_security_group = {'id': nsg_id}
        nic = network_client.network_interfaces.begin_create_or_update(resource_group_name, nic_name, nic).result()
        print(f"VM '{vm_name}' associated with NSG '{nsg_id}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

print(
    "Provisioning a virtual machine... some operations might take a \
minute or two."
)

# Acquire a credential object.
credential = DefaultAzureCredential()

# Step 1: Provision a resource group

# Obtain the management object for resources.
resource_client = ResourceManagementClient(credential, SUBSCRIPTION_ID)

# Provision the resource group.
rg_result = resource_client.resource_groups.create_or_update(RESOURCE_GROUP_NAME, {"location": LOCATION})

print(f"Provisioned resource group {rg_result.name} in the {rg_result.location} region")

# For details on the previous code, see Example: Provision a resource
# group at https://learn.microsoft.com/azure/developer/python/
# azure-sdk-example-resource-group

# Step 2: provision a virtual network

# A virtual machine requires a network interface client (NIC). A NIC
# requires a virtual network and subnet along with an IP address.
# Therefore we must provision these downstream components first, then
# provision the NIC, after which we can provision the VM.

# Obtain the management object for networks
network_client = NetworkManagementClient(credential, SUBSCRIPTION_ID)

# Provision the virtual network and wait for completion
poller = network_client.virtual_networks.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    VNET_NAME,
    {
        "location": LOCATION,
        "address_space": {"address_prefixes": ["10.0.0.0/16"]},
    },
)

vnet_result = poller.result()

print(f"Provisioned virtual network {vnet_result.name} with address prefixes {vnet_result.address_space.address_prefixes}")

# Step 3: Provision the subnet and wait for completion
poller = network_client.subnets.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    VNET_NAME,
    SUBNET_NAME,
    {"address_prefix": "10.0.0.0/24"},
)
subnet_result = poller.result()

print(
    f"Provisioned virtual subnet {subnet_result.name} with address \
prefix {subnet_result.address_prefix}"
)

# Step 4: Provision an IP address and wait for completion
poller = network_client.public_ip_addresses.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    IP_NAME,
    {
        "location": LOCATION,
        "sku": {"name": "Standard"},
        "public_ip_allocation_method": "Static",
        "public_ip_address_version": "IPV4",
    },
)

ip_address_result = poller.result()

print(
    f"Provisioned public IP address {ip_address_result.name} \
with address {ip_address_result.ip_address}"
)

# Step 5: Provision the network interface client
poller = network_client.network_interfaces.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    NIC_NAME,
    {
        "location": LOCATION,
        "ip_configurations": [
            {
                "name": IP_CONFIG_NAME,
                "subnet": {"id": subnet_result.id},
                "public_ip_address": {"id": ip_address_result.id},
            }
        ],
    },
)

nic_result = poller.result()

print(f"Provisioned network interface client {nic_result.name}")

# Step 6: Provision the virtual machine

# Obtain the management object for virtual machines
compute_client = ComputeManagementClient(credential, SUBSCRIPTION_ID)

print(
    f"Provisioning virtual machine {VM_NAME}; this operation might \
take a few minutes."
)

# Provision the VM specifying only minimal arguments, which defaults
# to an Ubuntu 18.04 VM on a Standard DS1 v2 plan with a public IP address
# and a default virtual network/subnet.

poller = compute_client.virtual_machines.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    VM_NAME,
    {
        "location": LOCATION,
        "storage_profile": {
            "image_reference": {
                "publisher": "Canonical",
                "offer": "0001-com-ubuntu-server-jammy",
                "sku": "22_04-lts-gen2",
                "version": "latest",
            }
        },
        "hardware_profile": {"vm_size": "Standard_DS1_v2"},
        "os_profile": {
            "computer_name": VM_NAME,
            "admin_username": USERNAME,
            "admin_password": PASSWORD,
        },
        "network_profile": {
            "network_interfaces": [
                {
                    "id": nic_result.id,
                }
            ]
        },
    },
)

vm_result = poller.result()

print(f"Provisioned virtual machine {vm_result.name}")

# Associate with the NSG
nsg_id = get_nsg_id_by_name(SUBSCRIPTION_ID, RESOURCE_GROUP_NAME, NSG_NAME)
associate_vm_with_nsg(SUBSCRIPTION_ID, RESOURCE_GROUP_NAME, VM_NAME, nsg_id)

# Create cloudflare record
from dns_managment import create_record

CLOUDFLARE_TOKEN = os.environ["CLOUDFLARE_TOKEN"]
create_record(CLOUDFLARE_TOKEN, vm_result.name, ip_address_result.ip_address)

# Install docker on the machine
from dockerize import setup_and_run
setup_and_run(ip_address_result.ip_address, USERNAME, PASSWORD)

