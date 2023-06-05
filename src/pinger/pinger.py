from paramiko import SSHClient, AutoAddPolicy
from azure_provider.vm_manager import VmDetails
from re import findall


class PingStatistics:
    def __init__(self, mini, avg, maxi, mdev):
        self.mini = mini
        self.avg = avg
        self.maxi = maxi
        self.mdev = mdev

    def __repr__(self):
       return f'PingStatistics({self.mini}, {self.avg}, {self.maxi}, {self.mdev})' 

    @staticmethod
    def from_ping_output(output: str):
        mini, avg, maxi, mdev = findall("\d*\.\d*", output)
        return PingStatistics(float(mini), float(avg), float(maxi), float(mdev))

VmId = str
PingStatisticsGrid = dict[VmId, dict[VmId, PingStatistics]] 

def ping(vms: list[VmDetails], ping_count=10) -> PingStatisticsGrid:
    result = {vm.id: {} for vm in vms}

    for src_vm in vms:
        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(src_vm.ip, username=src_vm.login, password=src_vm.password)

        for dest_vm in vms:
            if src_vm.ip != dest_vm.ip:
                ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command(f"ping -qc {ping_count} {dest_vm.ip}")
                rtt_stats = ssh_stdout.readlines()[-1]
                stats = PingStatistics.from_ping_output(rtt_stats)
                result[src_vm.id][dest_vm.id] = stats

        client.close()
    
    return result