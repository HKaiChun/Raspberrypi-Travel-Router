"""python-iwlist

Original from https://github.com/iancoleman/python-iwlist/tree/master
"""

import re
import subprocess

from typing import TypedDict, cast


class IwlistResult(TypedDict, total=False):
    cellnumber: str
    essid: str
    protocol: str
    mode: str
    frequency: str
    frequency_units: str
    channel: str
    signal_quality: str
    signal_quality: str
    signal_level_dBm: str


cellNumberRe = re.compile(r"^Cell\s+(?P<cellnumber>.+)\s+-\s+Address:\s(?P<mac>.+)$")
regexps = [
    re.compile(r"^ESSID:\"(?P<essid>.*)\"$"),
    re.compile(r"^Protocol:(?P<protocol>.+)$"),
    re.compile(r"^Mode:(?P<mode>.+)$"),
    re.compile(r"^Frequency:(?P<frequency>[\d.]+) (?P<frequency_units>.+) \(Channel (?P<channel>\d+)\)$"),
    re.compile(r"^Encryption key:(?P<encryption>.+)$"),
    re.compile(
        # r"^Quality=(?P<signal_quality>\d+)/(?P<signal_total>\d+)\s+Signal level=(?P<signal_level_dBm>.+) d.+$"
        r"^Quality=(?P<signal_quality>\d+)/(?P<signal_total>\d+)\s+Signal level=(?P<signal_level_dBm>.+)/\d.+$"
    ),
    re.compile(r"^Signal level=(?P<signal_quality>\d+)/(?P<signal_total>\d+).*$"),
]

# Detect encryption type
wpaRe = re.compile(r"IE:\ WPA\ Version\ 1$")
wpa2Re = re.compile(r"IE:\ IEEE\ 802\.11i/WPA2\ Version\ 1$")


# Runs the comnmand to scan the list of networks.
# Must run as super user.
# Does not specify a particular device, so will scan all network devices.
def scan(interface: str):
    cmd = ["iwlist", interface, "scan"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    points = ""
    if proc.stdout is not None:
        points = proc.stdout.read().decode("utf-8")

    return points


# Parses the response from the command "iwlist scan"
def parse(content: str) -> list[IwlistResult]:
    cells: list[dict[str, str]] = []
    lines = content.split("\n")
    for line in lines:
        line = line.strip()
        cellNumber = cellNumberRe.search(line)
        if cellNumber is not None:
            cells.append(cellNumber.groupdict())
            continue
        wpa = wpaRe.search(line)
        if wpa is not None:
            cells[-1].update({"encryption": "wpa"})
        wpa2 = wpa2Re.search(line)
        if wpa2 is not None:
            cells[-1].update({"encryption": "wpa2"})
        for expression in regexps:
            result = expression.search(line)
            if result is not None:
                if "encryption" in result.groupdict():
                    if result.groupdict()["encryption"] == "on":
                        cells[-1].update({"encryption": "wep"})
                    else:
                        cells[-1].update({"encryption": "off"})
                else:
                    cells[-1].update(result.groupdict())
                continue

    # return cells
    temp: list[IwlistResult] = [cast(IwlistResult, i) for i in cells]
    return temp
