from azure_provider.rg_manager import RgManager
from azure_provider.network_manager import NetworkManager
from azure_provider.network_manager import NicDetails
from azure_provider.network_manager import ResourceLocation
from azure_provider.vm_manager import VmManager
from azure_provider.vm_manager import VmDetails
from azure_provider.regions import all_regions
import os

from azure.identity import AzureCliCredential


class AzureProvisioner:
    regions_to_resources: "dict[str, tuple[ResourceLocation, NicDetails]]" = {}

    def __init__(self, regions=all_regions):
        credential = AzureCliCredential()
        subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
        self.regions = regions
        self.rg_manager = RgManager(credential, subscription_id)
        self.network_manager = NetworkManager(credential, subscription_id)
        self.vm_manager = VmManager(credential, subscription_id)

    def init_region_resources(self):
        rgs = self.rg_manager.create_rgs(self.regions)
        self.resource_locations = [ResourceLocation(region, rg)
                              for (region, rg) in zip(self.regions, rgs)]
        # network_manager.cleanup(nic_locations)
        self.nics = self.network_manager.create_nics(self.resource_locations)

        for (region, location, nic) in zip(self.regions, self.resource_locations, self.nics):
            self.regions_to_resources[region] = (location, nic)

    def create_vms(self) -> "list[VmDetails]":
        return self.create_vms(self.regions)

    def create_vms(self, regions) -> "list[VmDetails]":
        locations = []
        nics = []

        for region in regions:
            (location, nic) = self.regions_to_resources[region]
            locations.append(location)
            nics.append(nic)

        return self.vm_manager.create_vms(locations, nics)

    def cleanup_vms(self, regions: "list[str]"):
        locations = []

        for region in regions:
            (location, _) = self.regions_to_resources[region]
            locations.append(location)

        self.vm_manager.cleanup(locations)

    def cleanup(self):
        self.vm_manager.cleanup(self.resource_locations)
        self.network_manager.cleanup(self.resource_locations)
        self.rg_manager.cleanup()

    def emergency_cleanup(self):
        rgs = self.rg_manager.create_rgs(self.regions)
        self.resource_locations = [ResourceLocation(region, rg)
                              for (region, rg) in zip(self.regions, rgs)]
        self.cleanup()
        