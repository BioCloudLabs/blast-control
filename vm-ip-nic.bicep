resource ip 'Microsoft.Network/publicIPAddresses@2022-11-01' = {
  name: 'test-ip'
  location: 'westeurope'
  sku: {
    name: 'Basic'
  }
  properties: {
    publicIPAllocationMethod: 'Dynamic'
    publicIPAddressVersion: 'IPv4'
  }
}

resource nic 'Microsoft.Network/networkInterfaces@2022-11-01' = {
  name: 'test-nic'
  location: 'westeurope'
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

