import os
import json

from azure_provider.regions import all_regions
from azure_provider.provisioner import AzureProvisioner
from pinger import pinger
from common.vm_details import VmDetails

# can be passed all regions at once, then creating vms should be faster
azure_provisioner = AzureProvisioner(all_regions[:2])
azure_provisioner.emergency_cleanup()
azure_provisioner.init_region_resources()
vms = azure_provisioner.create_vms(all_regions[:2])

# returns grid with ping statistics grouped by vm ids
for vm in vms:
    print(vm)

pingresults = pinger.ping(vms)

print(pingresults)

with open("pingresults.json", "w+") as f:
    json.dump(pingresults, f, indent=4)

input("Press enter to cleanup")
# clean only some vms, might be useful if we hit some resource limit
# azure_provisioner.cleanup_vms(all_regions)
azure_provisioner.cleanup()

# pinger.ping([VmDetails("tipy-vm-eastus0", "4.227.254.131", "azureuser", "ChangePa$$w0rd24"), VmDetails("tipy-vm-eastus2", "20.7.1.187", "azureuser", "ChangePa$$w0rd24")])
