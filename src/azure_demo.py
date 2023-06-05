import os
import json

from azure_provider.regions import all_regions
from azure_provider.provisioner import AzureProvisioner
from pinger import pinger

# can be passed all regions at once, then creating vms should be faster
azure_provisioner = AzureProvisioner(all_regions)
# azure_provisioner.emergency_cleanup()
azure_provisioner.init_region_resources()
vms = azure_provisioner.create_vms(all_regions)

# ping_results = pinger.ping(vms)

cdn_results = pinger.download(vms)
with open("data/cdn_results.json", "w+") as f:
    json.dump(cdn_results, f, indent=4)

input("Press enter to cleanup")
azure_provisioner.cleanup_vms(all_regions)
azure_provisioner.cleanup()
