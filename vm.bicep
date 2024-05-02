param location string = 'westeurope'

@description('The name of your virtual machine.')
param vmName string = 'blast-1'

param username string = 'azure'

// TODO use File
param publicKey string

resource ip 'Microsoft.Network/publicIPAddresses@2022-11-01' = {
  name: '${vmName}-ip'
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    publicIPAllocationMethod: 'Dynamic'
    publicIPAddressVersion: 'IPv4'
  }
}

resource vm 'Microsoft.Compute/virtualMachines@2023-03-01' = {
  name: '${vmName}-vm'
  location: location
  properties: {
    hardwareProfile: {
      vmSize: 'Standard_B1s' 
    }
    storageProfile: {
      osDisk: {
        createOption: 'FromImage'
        managedDisk: {
          storageAccountType: 'Premium_LRS'
        }
      }
      imageReference: {
        publisher: 'Canonical'
        offer: '0001-com-ubuntu-server-jammy'
        sku: '22_04-lts-gen2'
        version: 'latest'
      }
    }
    networkProfile: {
      networkInterfaces: [
        {
          id: nic.id
        }
      ]
    }
    osProfile: {
      computerName: vmName
      adminUsername: username
      linuxConfiguration: {
        ssh: {
          publicKeys: [
            {
              keyData: publicKey
              path: '/home/${username}/.ssh/authorized_keys'
            }
          ]
        }
      }
    }
  }
}

resource nic 'Microsoft.Network/networkInterfaces@2022-11-01' = {
  name: '${vmName}-nic'
  location: location
  properties: {
    ipConfigurations: [
      {
        name: 'ipconfig1'
        properties: {
          subnet: {
            id: '/subscriptions/f9853267-3520-442b-9bf6-18c8c9f17b5b/resourceGroups/blast/providers/Microsoft.Network/virtualNetworks/blast-vnet/subnets/default'
          }
          privateIPAllocationMethod: 'Dynamic'
          publicIPAddress:  {
            id: ip.id
          }
        }
      }
    ]
  }
}
