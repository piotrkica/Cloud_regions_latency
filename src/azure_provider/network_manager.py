from azure.identity import AzureCliCredential
from azure.mgmt.network import NetworkManagementClient
from azure_provider.resource_cleaner import cleanup_resource_sequential
from azure_provider.resource_cleaner import cleanup_resource


class ResourceLocation:
    def __init__(self, region: str, rg: str):
        self.region = region
        self.rg = rg


class NicDetails:
    def __init__(self, id: str, ip: str):
        self.id = id
        self.ip = ip


class NetworkManager:
    VNET_PREFIX = "tipy-vnet"
    NSG_PREFIX = "tipy-nsg"
    SUBNET_PREFIX = "tipy-subnet"
    IP_PREFIX = "tipy-ip"
    IP_CONFIG_PREFIX = "tipy-ip-config"
    NIC_PREFIX = "tipy-nic"

    _nsgs = []
    _vnets = []
    _subnets = []
    _ips = []
    _nics = []

    def __init__(self, credential: AzureCliCredential, subscription_id: str):
        self._network_client = NetworkManagementClient(
            credential, subscription_id)

    def create_nics(self, locations: "list[ResourceLocation]") -> "list[NicDetails]":
        self._create_security_groups(locations)
        self._create_vnets(locations)
        self._create_subnets(locations)
        self._create_ips(locations)
        self._create_nics(locations)
        return [NicDetails(nic.id, ip.ip_address) for (nic, ip) in zip(self._nics, self._ips)]

    def _create_security_groups(self, locations: "list[ResourceLocation]") -> "list[NicDetails]":
        nsg_pollers = []
        for location in locations:
            nsg_pollers.append(self._network_client.network_security_groups.begin_create_or_update(
                location.rg,
                self._nsg_name(location),
                {
                    "location": location.region,
                    "security_rules": [
                        {
                            "priority": 100,
                            "name": "AllowSSH",
                            "protocol": "Tcp",
                            "source_address_prefix": "*",
                            "source_port_range": "*",
                            "destination_address_prefix": "*",
                            "destination_port_range": 22,
                            "direction": "Inbound",
                            "access": "Allow"
                        },
                        {
                            "priority": 110,
                            "name": "AllowICMPInbound",
                            "protocol": "ICMP",
                            "source_address_prefix": "*",
                            "source_port_range": "*",
                            "destination_address_prefix": "*",
                            "destination_port_range": "*",
                            "direction": "Inbound",
                            "access": "Allow"
                        },
                                                {
                            "priority": 120,
                            "name": "AllowICMPOutbound",
                            "protocol": "ICMP",
                            "source_address_prefix": "*",
                            "source_port_range": "*",
                            "destination_address_prefix": "*",
                            "destination_port_range": 8080,
                            "direction": "Outbound",
                            "access": "Allow"
                        },
                    ]
                }
            ))

        for poller in nsg_pollers:
            nsg_result = poller.result()
            print(
                f"Provisioned network security group {nsg_result.name} to allow SSH access."
            )
            self._nsgs.append(nsg_result)

    def _nsg_name(self, location: ResourceLocation):
        return f"{self.NSG_PREFIX}-{location.region}"

    def _create_vnets(self, locations: "list[ResourceLocation]"):
        vnet_pollers = []
        for location in locations:
            vnet_pollers.append(self._network_client.virtual_networks.begin_create_or_update(
                location.rg,
                self._vnet_name(location),
                {
                    "location": location.region,
                    "address_space": {"address_prefixes": ["10.0.0.0/16"]},
                },
            ))

        for poller in vnet_pollers:
            vnet_result = poller.result()
            print(
                f"Provisioned virtual network {vnet_result.name} with address prefixes {vnet_result.address_space.address_prefixes}"
            )
            self._vnets.append(vnet_result)

    def _vnet_name(self, location: ResourceLocation):
        return f"{self.VNET_PREFIX}-{location.region}"

    def _create_subnets(self, locations: "list[ResourceLocation]"):
        subnet_pollers = []
        for (vnet, location) in zip(self._vnets, locations):
            subnet_pollers.append(self._network_client.subnets.begin_create_or_update(
                location.rg,
                vnet.name,
                self._subnet_name(location),
                {"address_prefix": "10.0.0.0/24"},
            ))

        for poller in subnet_pollers:
            subnet_result = poller.result()
            print(
                f"Provisioned virtual subnet {subnet_result.name} with address prefix {subnet_result.address_prefix}"
            )
            self._subnets.append(subnet_result)

    def _subnet_name(self, location: ResourceLocation):
        return f"{self.SUBNET_PREFIX}-{location.region}"

    def _create_ips(self, locations: "list[ResourceLocation]"):
        ip_pollers = []
        for location in locations:
            ip_pollers.append(self._network_client.public_ip_addresses.begin_create_or_update(
                location.rg,
                self._ip_name(location),
                {
                    "location": location.region,
                    "sku": {"name": "Standard"},
                    "public_ip_allocation_method": "Static",
                    "public_ip_address_version": "IPV4",
                },
            ))

        for poller in ip_pollers:
            ip_result = poller.result()
            print(
                f"Provisioned public IP address {ip_result.name} with address {ip_result.ip_address}"
            )
            self._ips.append(ip_result)

    def _ip_name(self, location: ResourceLocation):
        return f"{self.IP_PREFIX}-{location.region}"

    def _create_nics(self, locations: "list[ResourceLocation]"):
        nic_pollers = []
        for (location, subnet, ip, nsg) in zip(locations, self._subnets, self._ips, self._nsgs):
            nic_pollers.append(self._network_client.network_interfaces.begin_create_or_update(
                location.rg,
                self._nic_name(location),
                {
                    "location": location.region,
                    "ip_configurations": [
                        {
                            "name": self._ip_config_name(location),
                            "subnet": {"id": subnet.id},
                            "public_ip_address": {"id": ip.id},
                        }
                    ],
                    "network_security_group": {
                        "id": nsg.id
                    }
                },
            ))

        for poller in nic_pollers:
            nic_result = poller.result()
            print(f"Provisioned network interface client {nic_result.name}")
            self._nics.append(nic_result)

    def _nic_name(self, location: ResourceLocation):
        return f"{self.NIC_PREFIX}-{location.region}"

    def _ip_config_name(self, location: ResourceLocation):
        return f"{self.IP_CONFIG_PREFIX}-{location.region}"

    def cleanup(self, locations: "list[ResourceLocation]"):
        cleanup_resource([self._nic_name(location) for location in locations], [
            (lambda: self._network_client.network_interfaces.begin_delete(location.rg, self._nic_name(location))) for location in locations
        ])
        cleanup_resource_sequential([self._ip_name(location) for location in locations], [
            (lambda: self._network_client.public_ip_addresses.begin_delete(location.rg, self._ip_name(location))) for location in locations
        ])
        cleanup_resource([self._subnet_name(location) for location in locations], [
            (lambda: self._network_client.subnets.begin_delete(location.rg, self._vnet_name(location), self._subnet_name(location))) for location in locations
        ])
        cleanup_resource([self._vnet_name(location) for location in locations], [
            (lambda: self._network_client.virtual_networks.begin_delete(location.rg, self._vnet_name(location))) for location in locations
        ])
        cleanup_resource([self._nsg_name(location) for location in locations], [
            (lambda: self._network_client.network_security_groups.begin_delete(location.rg, self._nsg_name(location))) for location in locations
        ])
