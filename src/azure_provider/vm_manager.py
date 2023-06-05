from azure_provider.network_manager import ResourceLocation
from azure_provider.network_manager import NicDetails
from azure_provider.resource_cleaner import cleanup_resource
from common.vm_details import VmDetails
from azure.identity import AzureCliCredential
from azure.mgmt.compute import ComputeManagementClient
from functools import partial


class VmManager:
    VM_PREFIX = "tipy-vm"
    USERNAME = "azureuser"
    PASSWORD = "ChangePa$$w0rd24"

    _vms = []

    def __init__(self, credential: AzureCliCredential, subscription_id: str):
        self._compute_client = ComputeManagementClient(
            credential, subscription_id)

    def create_vms(self, locations: "list[ResourceLocation]", nics: "list[NicDetails]") -> "list[VmDetails]":
        vm_pollers = []
        for (location, nic) in zip(locations, nics):
            print(
                f"Provisioning virtual machine {self._vm_name(location)}; this operation might take a few minutes."
            )
            vm_pollers.append(self._compute_client.virtual_machines.begin_create_or_update(
                location.rg,
                self._vm_name(location),
                {
                    "location": location.region,
                    "storage_profile": {
                        "image_reference": {
                            "publisher": "Canonical",
                            "offer": "UbuntuServer",
                            "sku": "16.04.0-LTS",
                            "version": "latest",
                        }
                    },
                    "hardware_profile": {"vm_size": "Standard_B1s"},
                    "os_profile": {
                        "computer_name": self._vm_name(location),
                        "admin_username": self.USERNAME,
                        "admin_password": self.PASSWORD,
                    },
                    "network_profile": {
                        "network_interfaces": [
                            {
                                "id": nic.id,
                            }
                        ]
                    },
                },
            ))

        for poller in vm_pollers:
            vm_result = poller.result()
            print(f"Provisioned virtual machine {vm_result.name}")
            self._vms.append(vm_result)

        return [VmDetails(vm.name, nic.ip, self.USERNAME, self.PASSWORD) for (vm, nic) in zip(self._vms, nics)]

    def _vm_name(self, location: ResourceLocation):
        return f"{self.VM_PREFIX}-{location.region}"

    def cleanup(self, locations: "list[ResourceLocation]"):
        cleanup_resource([self._vm_name(location) for location in locations], [
            partial(lambda x: self._compute_client.virtual_machines.begin_delete(x.rg, self._vm_name(x)), location)
            for location in locations
        ])
