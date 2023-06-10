from paramiko import SSHClient, AutoAddPolicy
from pssh.clients import ParallelSSHClient
from azure_provider.vm_manager import VmDetails
from re import findall
from tqdm import tqdm

VmId = str
PingStatisticsGrid: "dict[VmId, dict[VmId, PingStatistics]]" = dict()


class PingStatistics:
    def __init__(self, p95, p99):
        self.p95 = p95
        self.p99 = p99

    def __repr__(self):
        return {"p95": self.p95, "p99": self.p99}  # in ms

    def __str__(self):
        return str({"p95": self.p95, "p99": self.p99})

    @staticmethod
    def from_ping_output(output: str):
        mini, avg = findall("\d*\.\d*", output)
        return {"p95": float(mini), "p99": float(avg)}


def ping(vms: "list[VmDetails]", ping_count=1000) -> PingStatisticsGrid:
    result = {vm.id: {} for vm in vms}
    ips = list(map(lambda x: x.ip, vms))
    client = ParallelSSHClient(ips, user=vms[0].login, password=vms[0].password)
    install_datamash(client)

    for dst_vm in tqdm(vms):
        print(dst_vm.ip)
        fill_result(client, vms, ping_count, dst_vm, result)
    return result

def install_datamash(client):
    try:
        for x in client.run_command("apt update -y && apt install -y datamash", sudo=True):
            stderr = list(x.stderr)
            if len(stderr) > 0: print(stderr)
    except Exception as e:
        print(e)
        install_datamash(client)

def fill_result(client, vms, ping_count, dst_vm, result):
    try:
        output = client.run_command(f"ping -c {ping_count} {dst_vm.ip} | tail -n+2 | head -n-1 | sed -rn 's|.*=([0-9]+\.?[0-9]+?) ms|\\1|p' | LC_ALL=C datamash perc:95 1 perc:99 1")

        for (src_vm, host_output) in zip(vms, output):
            stdout = list(host_output.stdout)
            stderr = list(host_output.stderr)
            if (len(stderr) > 0):
                print(stderr)
            result[src_vm.id][dst_vm.id] = PingStatistics.from_ping_output(stdout[-1])
            print(f"Pinged: {src_vm} to {dst_vm}. Result {result[src_vm.id][dst_vm.id]}")
    except Exception as e:
        print(f"Retrying {dst_vm.ip}. Exc: {e}")
        fill_result(client, vms, ping_count, dst_vm, result)