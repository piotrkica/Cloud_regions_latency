from azure_provider.regions import all_regions
from azure_provider.provisioner import AzureProvisioner

# can be passed all regions at once, then creating vms should be faster
azure_provisioner = AzureProvisioner(all_regions[:2])
# azure_provisioner.emergency_cleanup()
azure_provisioner.init_region_resources()
print(list(map(lambda x: str(x), azure_provisioner.create_vms(all_regions[:2]))))
input("Press enter to cleanup")
# clean only some vms, might be useful if we hit some resource limit
azure_provisioner.cleanup_vms(all_regions[:1])
azure_provisioner.cleanup()
