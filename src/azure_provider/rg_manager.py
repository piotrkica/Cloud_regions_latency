from azure_provider.resource_cleaner import cleanup_resource
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient


class RgManager:
    RESOURCE_GROUP_PREFIX = "tipy-rg"
    _rg_results: list = []

    def __init__(self, credential: AzureCliCredential, subscription_id: str):
        self._resource_client = ResourceManagementClient(
            credential, subscription_id)

    def create_rgs(self, locations: list) -> "list[str]":
        for location in locations:
            self._rg_results.append(self._resource_client.resource_groups.create_or_update(
                f"{self.RESOURCE_GROUP_PREFIX}-{location}", {"location": location}
            ))

        for rg_result in self._rg_results:
            print(
                f"Provisioned resource group {rg_result.name} in the {rg_result.location} region"
            )

        return [x.name for x in self._rg_results]

    def cleanup(self):
        cleanup_resource([rg.name for rg in self._rg_results], [
            lambda: self._resource_client.resource_groups.begin_delete(rg.name) for rg in self._rg_results
        ])
