
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


