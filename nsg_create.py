import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient

SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]
RESOURCE_GROUP_NAME = 'blast'
NSG_NAME = 'blast-nsg'
LOCATIONS = 'westeurope'

def create_nsg(subscription_id, resource_group_name, nsg_name, location):
    credential = DefaultAzureCredential()
    network_client = NetworkManagementClient(credential, subscription_id)

    # Define NSG parameters
    nsg_params = {
        'location': location,
        'security_rules': [
            {
                'name': 'AllowSSH',
                'protocol': 'Tcp',
                'source_port_range': '*',
                'destination_port_range': '22',
                'source_address_prefix': '*',
                'destination_address_prefix': '*',
                'access': 'Allow',
                'priority': 100,
                'direction': 'Inbound'
            }
        ]
    }

    # Create the NSG
    nsg = network_client.network_security_groups.begin_create_or_update(
        resource_group_name,
        nsg_name,
        parameters=nsg_params
    ).result()

    print(f"Network Security Group '{nsg.name}' created successfully.")


create_nsg(SUBSCRIPTION_ID, RESOURCE_GROUP_NAME, NSG_NAME, LOCATIONS)