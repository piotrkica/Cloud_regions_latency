from azure_provider.regions import all_regions
from azure_provider.provisioner import AzureProvisioner
from pinger import pinger

# can be passed all regions at once, then creating vms should be faster
azure_provisioner = AzureProvisioner(all_regions[:2])
# azure_provisioner.emergency_cleanup()
azure_provisioner.init_region_resources()
vms = azure_provisioner.create_vms(all_regions[:2])

# returns grid with ping statistics grouped by vm ids
print(pinger.ping(vms))

input("Press enter to cleanup")
# clean only some vms, might be useful if we hit some resource limit
azure_provisioner.cleanup_vms(all_regions[:1])
azure_provisioner.cleanup()
