from paramiko import SSHClient, AutoAddPolicy
from azure_provider.vm_manager import VmDetails
from re import findall
from tqdm import tqdm

VmId = str
PingStatisticsGrid = dict[VmId, dict[VmId, dict]]


class PingStatistics:
    def __init__(self, mini, avg, maxi, mdev):
        self.mini = mini
        self.avg = avg
        self.maxi = maxi
        self.mdev = mdev

    def __repr__(self):
        return {"min": self.mini, "avg": self.avg, "max": self.maxi, "mdev": self.mdev}  # in ms

    def __str__(self):
        return str({"min": self.mini, "avg": self.avg, "max": self.maxi, "mdev": self.mdev})

    @staticmethod
    def from_ping_output(output: str):
        mini, avg, maxi, mdev = findall("\d*\.\d*", output)
        return {"min": float(mini), "avg": float(avg), "max": float(maxi), "mdev": float(mdev)}


def ping(vms: list[VmDetails], ping_count=5) -> PingStatisticsGrid:
    result = {vm.id: {} for vm in vms}

    for src_vm in tqdm(vms):
        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(src_vm.ip, username=src_vm.login, password=src_vm.password)

        for i, dest_vm in enumerate(vms):
            if src_vm.ip != dest_vm.ip:
                ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command(f"ping -qc {ping_count} {dest_vm.ip}")
                rtt_stats = ssh_stdout.readlines()[-1]
                stats = PingStatistics.from_ping_output(rtt_stats)
                result[src_vm.id][dest_vm.id] = stats
                print(f"Pinged: {src_vm} to {dest_vm}. Completed {i}/{len(vms) - 1}")
        client.close()

    return result
