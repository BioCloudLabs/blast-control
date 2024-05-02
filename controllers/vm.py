from flask_smorest import Blueprint, abort
from flask.views import MethodView
from azure.mgmt.compute import ComputeManagementClient
from dns_managment import create_record
from dockerize import setup_and_run
from azure.mgmt.network import NetworkManagementClient
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode
import os
import random

blp = Blueprint("vm", __name__, description="VMs endpoint", url_prefix="/vm")

def generate_random_vmname(length):
    characters = '0123456789abcdefghijklmnopqrstuvwxyz'
    return ''.join(random.choices(characters, k=length))

TEMPLATE_BODY = {
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "metadata": {
    "_generator": {
      "name": "bicep",
      "version": "0.26.170.59819",
      "templateHash": "951129947329205422"
    }
  },
  "parameters": {
    "location": {
      "type": "string",
      "defaultValue": "westeurope"
    },
    "vmName": {
      "type": "string",
      "defaultValue": "blast-1",
      "metadata": {
        "description": "The name of your virtual machine."
      }
    },
    "username": {
      "type": "string",
      "defaultValue": "azure"
    },
    "publicKey": {
      "type": "string"
    }
  },
  "resources": [
    {
      "type": "Microsoft.Network/publicIPAddresses",
      "apiVersion": "2022-11-01",
      "name": "[format('{0}-ip', parameters('vmName'))]",
      "location": "[parameters('location')]",
      "sku": {
        "name": "Basic"
      },
      "properties": {
        "publicIPAllocationMethod": "Dynamic",
        "publicIPAddressVersion": "IPv4"
      }
    },
    {
      "type": "Microsoft.Compute/virtualMachines",
      "apiVersion": "2023-03-01",
      "name": "[format('{0}-vm', parameters('vmName'))]",
      "location": "[parameters('location')]",
      "properties": {
        "hardwareProfile": {
          "vmSize": "Standard_B1s"
        },
        "storageProfile": {
          "osDisk": {
            "createOption": "FromImage",
            "managedDisk": {
              "storageAccountType": "Premium_LRS"
            }
          },
          "imageReference": {
            "publisher": "Canonical",
            "offer": "0001-com-ubuntu-server-jammy",
            "sku": "22_04-lts-gen2",
            "version": "latest"
          }
        },
        "networkProfile": {
          "networkInterfaces": [
            {
              "id": "[resourceId('Microsoft.Network/networkInterfaces', format('{0}-nic', parameters('vmName')))]"
            }
          ]
        },
        "osProfile": {
          "computerName": "[parameters('vmName')]",
          "adminUsername": "[parameters('username')]",
          "linuxConfiguration": {
            "ssh": {
              "publicKeys": [
                {
                  "keyData": "[parameters('publicKey')]",
                  "path": "[format('/home/{0}/.ssh/authorized_keys', parameters('username'))]"
                }
              ]
            }
          }
        }
      },
      "dependsOn": [
        "[resourceId('Microsoft.Network/networkInterfaces', format('{0}-nic', parameters('vmName')))]"
      ]
    },
    {
      "type": "Microsoft.Network/networkInterfaces",
      "apiVersion": "2022-11-01",
      "name": "[format('{0}-nic', parameters('vmName'))]",
      "location": "[parameters('location')]",
      "properties": {
        "ipConfigurations": [
          {
            "name": "ipconfig1",
            "properties": {
              "subnet": {
                "id": "/subscriptions/f9853267-3520-442b-9bf6-18c8c9f17b5b/resourceGroups/blast/providers/Microsoft.Network/virtualNetworks/blast-vnet/subnets/default"
              },
              "privateIPAllocationMethod": "Dynamic",
              "publicIPAddress": {
                "id": "[resourceId('Microsoft.Network/publicIPAddresses', format('{0}-ip', parameters('vmName')))]"
              }
            }
          }
        ]
      },
      "dependsOn": [
        "[resourceId('Microsoft.Network/publicIPAddresses', format('{0}-ip', parameters('vmName')))]"
      ]
    }
  ]
}

PUB_SSH_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDWWyknEkUUNpKWH3LkmEi1x0s0x08wJHswnUxB4GuhT4jG6ZoePiZxPgGD14cahYp/dRgRgCFIvyYwCSj6vpo9yiQtbaUdu38X/xmHv9A1ssYA6mJceXoXmVHGhrhY9HT4Y7a6KKqAWzMxU69TQI90hcfl8OAxy3A1woIt2Pa6B4OvZAUN1/+YH873UOMoGaUlhYqbr12qU6UrTlxIOfSDTzejamkNCLNaokraOoM3Cx9YB6Lw4oOTk7MnWwNeT/pr4OftOdCRpaHO7mhWJoNmohWgmLA1Dnbv/MHRGsy/2KH0aRNfkPNzzc7UwxHId7IO76CbC9xF6u2wbz8qwBRrDWNKm6lp5iBs5nVbs2FxyAgeYKAcQQV4s9CN7kyiRmFy7XeDN5taAYLyXQZBEu9VqYdwkm9MQJ0S34ZYETjwS6ztP4bMOiOcCqtUKzzyGY16jSdZqj3Weg6pcMTcsOAO7XLcrE0KIVCK3xsafJ8vjTpRNnlM7wmE4iBZNuHmL1U= christiangoac@DESKTOP-VFSDTV4"

credential = AzureCliCredential()
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

resource_client = ResourceManagementClient(credential, subscription_id)

CLOUDFLARE_TOKEN = os.getenv("CLOUDFLARE_TOKEN")

@blp.route("/setup")
class SetupVm(MethodView):
    def get(self):
        """
        API Endpoint to create a vm.

        :return: HTTP response with the login result.
        """

        # vm_name = generate_random_vmname(10)
        vm_name = "blast-4"

        try:
            rg_deployment_result = resource_client.deployments.begin_create_or_update(
                "blast",
                "blast-deployment",
                {
                    "properties": {
                        "template": TEMPLATE_BODY,
                        "parameters": {
                            "vmName": {
                                "value": vm_name
                            },
                            "username": {
                                "value": "azure"
                            },
                            "location": {
                                "value": "westeurope"
                            },
                            "publicKey": {
                                "value": PUB_SSH_KEY
                            }
                        },
                        "mode": DeploymentMode.incremental
                    }
                }
            )

            rg_deployment_result.wait()

            network_client = NetworkManagementClient(credential, subscription_id)
            public_ip_address = network_client.public_ip_addresses.get('blast', vm_name + '-ip')

        except Exception as e:
            abort(500, message=f"An error ocurred while creating a vm: {str(e)}")

        try:
            dns = create_record(CLOUDFLARE_TOKEN, vm_name, public_ip_address.ip_address)
            print(dns)
        except Exception as e:
            abort(500, message=f"An error ocurred while creating vm dns records: {str(e)}")

        # setup_and_run(public_ip_address.ip_address)

        return {"ip": public_ip_address.ip_address, "dns": dns}, 200
