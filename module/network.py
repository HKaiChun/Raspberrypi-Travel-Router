import json
import re
import subprocess


def getCurrentSSID(interface: str) -> str:
    cmd = ("iwgetid", "-r", interface)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ssid = ""

    if proc.stdout is not None:
        ssid = proc.stdout.read().decode("utf-8")

    return ssid.strip()


def getLocalIPAddress(interface: str) -> str:
    cmd = ("ip", "addr", "show", interface)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    ip = ""
    if proc.stdout is not None:
        temp = proc.stdout.read().decode("utf-8")

        matchResult = re.search(r"inet\s+(\d+\.\d+\.\d+\.\d+)", temp)

        if matchResult:
            ip = matchResult.group(1)

    return ip.strip()


def updateWpaSupplicant(interface: str) -> bool:
    with open("database/db.json") as f:
        rememberNetwork: list[dict[str, str]] = json.loads(f.read())

    template = "\n".join(("ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev", "update_config=1", "\n"))

    for i in rememberNetwork:
        template += "network={\n"

        for k, v in i.items():
            if k == "priority":
                template += f"    {k}={v}\n"
            else:
                template += f'    {k}="{v}"\n'

        template += "}\n\n"

    configPath = {
        "wlan0": "/etc/wpa_supplicant/wpa_supplicant.conf",
        "wlan1": "/etc/wpa_supplicant/wpa_supplicant-wlan1.conf",
    }

    cmd = ("sudo", "bash", "update_wpa.sh", template, configPath.get(interface, "test.conf"))
    subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    cmd = ("wpa_cli", "-i", interface, "reconfigure")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if proc.stdout is None:
        return False

    # if proc.stdout.read().decode("utf-8") == "OK":
    #     return True
    # else:
    #     return False

    return True


def selectWpaNetworkID(interface: str, netId: int) -> bool:
    cmd = ("wpa_cli", "-i", interface, "list_networks")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if proc.stdout is None:
        return False

    networkList = proc.stdout.read().decode("utf-8").split("\n")[1:-1]

    if netId not in range(len(networkList)):
        return False

    cmd = ("wpa_cli", "-i", interface, "select_network", str(netId))
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if proc.stdout is None:
        return False

    # if proc.stdout.read().decode("utf-8") == "OK":
    #     return True

    # return False

    return True
