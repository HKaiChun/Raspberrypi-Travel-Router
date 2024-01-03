import module.iwlist as iwlist

# import module.network as network
import module.network as network


import server.entry as server


def main():
    server.launch_server()


if __name__ == "__main__":
    main()

    # print(iwlist.parse(iwlist.scan("wlan1")))
    # print(network.getCurrentSSID("wlan1"))
    # print(network.getLocalIPAddress("wlan1"))

    # network.updateWpaSupplicant("wlan1")
    # network.selectWpaNetworkID("wlan1", 0)
