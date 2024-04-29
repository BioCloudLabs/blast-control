import os
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode
from flask import Flask
from flask_smorest import Api
import os
from controllers.vm import blp as VmController
from dotenv import load_dotenv

app: Flask = Flask(__name__, static_folder="dist", static_url_path="/")

load_dotenv()

app.config["API_TITLE"] = os.getenv("API_TITLE")
app.config["API_VERSION"] = os.getenv("API_VERSION")
app.config["OPENAPI_VERSION"] = os.getenv("OPENAPI_VERSION")

api: Api = Api(app)

api.register_blueprint(VmController)

credential = AzureCliCredential()
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

resource_client = ResourceManagementClient(credential, subscription_id)

PUB_SSH_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDWWyknEkUUNpKWH3LkmEi1x0s0x08wJHswnUxB4GuhT4jG6ZoePiZxPgGD14cahYp/dRgRgCFIvyYwCSj6vpo9yiQtbaUdu38X/xmHv9A1ssYA6mJceXoXmVHGhrhY9HT4Y7a6KKqAWzMxU69TQI90hcfl8OAxy3A1woIt2Pa6B4OvZAUN1/+YH873UOMoGaUlhYqbr12qU6UrTlxIOfSDTzejamkNCLNaokraOoM3Cx9YB6Lw4oOTk7MnWwNeT/pr4OftOdCRpaHO7mhWJoNmohWgmLA1Dnbv/MHRGsy/2KH0aRNfkPNzzc7UwxHId7IO76CbC9xF6u2wbz8qwBRrDWNKm6lp5iBs5nVbs2FxyAgeYKAcQQV4s9CN7kyiRmFy7XeDN5taAYLyXQZBEu9VqYdwkm9MQJ0S34ZYETjwS6ztP4bMOiOcCqtUKzzyGY16jSdZqj3Weg6pcMTcsOAO7XLcrE0KIVCK3xsafJ8vjTpRNnlM7wmE4iBZNuHmL1U= christiangoac@DESKTOP-VFSDTV4"

template_body = {
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "metadata": {
    "_generator": {
      "name": "bicep",
      "version": "0.26.170.59819",
      "templateHash": "17707196249449278594"
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
      "defaultValue": "blast"
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
              "storageAccountType": "Standard_LRS"
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

rg_deployment_result = resource_client.deployments.begin_create_or_update(
    "blast",
    "blast-deployment",
    {
        "properties": {
            "template": template_body,
            "parameters": {
                "vmName": {
                    "value": "test-1"
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

print(rg_deployment_result.result())