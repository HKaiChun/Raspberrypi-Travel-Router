import json

from . import session
from module import network, iwlist

INTERFACE = "wlan1"


def currentStatusHandler() -> dict[str, str | None]:
    responsePayload: dict[str, str | None] = {
        "ssid": None,
        "ip_address": None,
    }

    ssid = network.getCurrentSSID(INTERFACE)
    ip = network.getLocalIPAddress(INTERFACE)

    if ssid != "":
        responsePayload["ssid"] = ssid
    if ip != "":
        responsePayload["ip_address"] = ip

    return responsePayload


def scanNetworkHandler() -> list[iwlist.IwlistResult]:
    return iwlist.parse(iwlist.scan(INTERFACE))


def applyWpaSettingHandler() -> bool:
    return network.updateWpaSupplicant(INTERFACE)


def selectNetworkHandler(netId: int) -> bool:
    return network.selectWpaNetworkID(INTERFACE, netId)


def loginHandler(ip: str, payload: str) -> bool:
    data: dict[str, str] = json.loads(payload)

    name = data.get("name")
    password = data.get("password")

    if name is None or password is None:
        return False

    LOGIN_NAME = "adminpi"
    LOGIN_PASSWORD = "raspberry"

    if name != LOGIN_NAME or password != LOGIN_PASSWORD:
        return False

    session.LOGIN_SESSION.updateSession(ip)
    return True
