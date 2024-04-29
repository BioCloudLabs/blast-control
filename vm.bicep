param location string = 'westeurope'

@description('The name of your virtual machine.')
param vmName string = 'blast-1'

param username string = 'blast'

// TODO use File
param publicKey string

// // https://docs.microsoft.com/en-us/azure/templates/microsoft.network/virtualnetworks?tabs=bicep
// resource vnet 'Microsoft.Network/virtualNetworks@2022-11-01' = {
//   name: '${location}-vnet'
//   location: location
//   properties: {
//     addressSpace: {
//       addressPrefixes: [
//         '10.1.0.0/16'
//       ]
//     }
//     subnets: [
//       {
//         name: '${location}-vnet-1'
//         properties: {
//           addressPrefix: '10.1.1.0/24'
//         }
//       }
//     ]
//   }
// }

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

//https://learn.microsoft.com/en-us/azure/virtual-machines/linux/quick-create-bicep?tabs=CLI

// https://learn.microsoft.com/en-us/azure/templates/microsoft.compute/virtualmachines?pivots=deployment-language-bicep

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
          storageAccountType: 'Standard_LRS'
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
            id: 'blast-vnet'
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

