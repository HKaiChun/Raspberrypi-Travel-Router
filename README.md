# Raspberrypi-Travel-Router

<big>***STUDY PROJECT***</big>

<big>***NOT FOR PRODUCTION***</big>

A small project try to build a router with Raspberry Pi, without RaspAP.

It kind of success?
## Motivation
-  The RaspberryPi Travel Router becomes the perfect companion for travelers, especially those who carry multiple devices. When traveling abroad, we often bring along smartphones, tablets, laptops, and various other devices, all of which require a stable and secure internet connection. Due to varying network environments in different regions, relying solely on Wi-Fi provided by hotels or public places may not always meet our needs.
  With the RaspberryPi Travel Router, you can effortlessly establish your own mobile network wherever you go, ensuring that all your devices have access to a reliable internet connection.

## Implementation Resources

### Hardware
- Raspberry Pi 3 Model B
- USB WiFi Adapter (rtl8192eu chip)
- 16 GB SD card

### Software
- Raspberry Pi OS Lite(64-bit)
- Python 3.12.1

## Implementation Process

### A. Set Up WiFi Access Point

1. Install Packages

    To create an access point, we need hostapd and dnsmasq.

    -> `sudo apt-get -y install hostapd dnsmasq`

    hostapd: enabling a network interface card to act as an access point and authentication server.
    dnsmasq: a lightweight combination of DHCP and DNS

2. Set Static IP Address

    In recent versions of Raspbian, network configuration is managed by the dhcpcd program.
    Tell it to ingnore the wireless interface, wlan0, and set a static IP address elsewhere.

    Edit the dhcpcd file:

    -> `sudo vim /etc/dhcpcd.conf`

    At the bottom of the file, add:

    -> `denyinterfaces wlan0`

    Next, tell the Raspberry Pi to set a static IP address for the WiFi interface.
    Open the interfaces file with the following command.

    -> `sudo vim /etc/network/interfaces`

    At the bottom of that file, add:

    -> 
    ```
    auto eth0
    iface eth0 inet dhcp

    allow-hotplug wlan0
    iface wlan0 inet static
        address 192.168.5.1
        netmask 255.255.255.0
        network 192.168.5.0
        broadcast 192.168.5.255
    ```

3. Configure Hostapd

    Set up hostapd to tell it to broadcast a particular SSID and allow WiFi connections on a certain channel.
    Edit the hostapd.conf file:

    -> `sudo vim /etc/hostapd/hostapd.conf`

    Enter the following into that file:
    ssid: WiFi network name
    wpa_passphrase: password to join the network

    ->
    ```
    interface=wlan0
    driver=nl80211
    ssid=MyPiAP
    hw_mode=g
    channel=6
    ieee80211n=1
    wmm_enabled=1
    ht_capab=[HT40][SHORT-GI-20][DSSS_CCK-40]
    macaddr_acl=0
    auth_algs=1
    ignore_broadcast_ssid=0
    wpa=2
    wpa_key_mgmt=WPA-PSK
    wpa_passphrase=raspberry
    rsn_pairwise=CCMP
    ```

    Next, we need to provide its location to the hostapd startup script
    since hostapd does not know where to find this configuration file.

    -> `sudo vim /etc/default/hostapd`

    Find the line #DAEMON_CONF="" and replace it with:

    -> `DAEMON_CONF="/etc/hostapd/hostapd.conf"`

4. Configure Dnsmasq

    The .conf file that comes with Dnsmasq has a lot of good information in it, so it might be worthwhile to save it (as a backup).

    -> `sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.bak`

    Open a new one to Edit it:

    -> `sudo vim /etc/dnsmasq.conf`

    In the blank file, paste in the text below.
    Note that we set up DHCP to assign addresses to devices between 192.168.5.100 and 192.168.5.200.
    Remember that 192.168.5.1 is reserved for the Pi.
    So, anything between 192.168.5.2 - 192.168.5.9 and between 192.168.5.201 - 192.168.5.254 can be used for devices with static IP addresses.

    ->
    ```
    interface=wlan0
    listen-address=192.168.5.1
    bind-interfaces
    server=8.8.8.8
    domain-needed
    bogus-priv
    dhcp-range=192.168.5.100,192.168.5.200,24h
    ```


5. Test WiFi connection

    Restart the Raspberry Pi

    -> `sudo reboot`

6. hostapd does not automatically start by default,
    so you need to execute a command to start hostapd and set it to run automatically at boot.

    -> `sudo systemctl start hostapd`
    -> `sudo systemctl enable hostapd`

7. If you encounter the following error message:

    Failed to enable unit: Unit file /etc/systemd/system/hostapd.service is masked.

8.  hostapd unmak, and execute again

    -> `sudo systemctl unmask hostapd`
    -> `sudo systemctl enable hostapd`
    -> `sudo systemctl start hostapd`

### B. Install USB WiFi Adapter (rtl8192eu) Driver

Depend to your USB WiFi Adapter, Raspberry Pi might come with build in driver. But is this case, we have to get the driver by ourself. The Following section we will be introduce how to build a driver source code and install into Raspberry Pi kernel. The following will be hardware depended and each driver will have different build step. Please visit your driver install instruction manuel for more information.

1. Get driver source code.

- visit [rtl8192eu-linux-driver](https://github.com/Mange/rtl8192eu-linux-driver) github page.

- install necessary tooling 
  
    `sudo apt install git raspberrypi-kernel-headers build-essential dkms`
    (In Raspberry pi **DO NOT** install `linux-headers-generic`)

- clone the repo

    `git clone https://github.com/Mange/rtl8192eu-linux-driver`
    `cd rtl8192eu-linux-driver`

- modify Makefile build platform to Raspberry Pi

  ```
  ...
  CONFIG_PLATFORM_ARM_RPI = y
  ...
  CONFIG_PLATFORM_I386_PC = n
  ```

- ***If dkms work on your machine***

    `sudo dkms add .`

    `sudo dkms install rtl8192eu/1.0`

- ***If not, you can build it yourself and install it manually***

    `make ARCH="arm64" -j4`

    when the build finish, copy the `8192eu.ko` into kernel.

    `sudo cp 8192eu.ko /lib/modules/$(uname -r)/kernel/driver/net/wireless`

    `sudo depmod`

- After the installation, reboot Raspberry Pi. When you plug the USB WiFi Adapter, it should recognize the adapter.

### C. Install Python 3.12.1

This section will briefly introduce how to build and install newer version of python on Raspberry Pi. Our target version is 3.12.1.

- download the source code from python official website or via this link [Gzipped source tarball](https://www.python.org/ftp/python/3.12.1/Python-3.12.1.tgz)

- unzip the source code

    `sudo tar zxf Python-3.12.1.tgz`

    `cd Python-3.12.1`

- generate Makefile

    `sudo ./configure --enable-optimization`

- build Python
    
    It will take some times, in Pi 3 with ancient will take hours long.
    If your Pi freeze have to restart, just keep run the same command to resume the build.

    `sudo make -j4`

    After that, your can check the python version by typing `python3.12 -v`.

    If you like to have alias, you can append it into `.bashrc`

### D. Launch Control Interface

The following section will guild you how to start the control website when the Raspberry Pi startup.

- Clone This Repo

    `git clone https://github.com/HKaiChun/Raspberrypi-Travel-Router.git`

    `cd Raspberrypi-Travel-Router`

- create a virtual environment

    `python3.12 -m venv venv`

- add execute permission to both shell script

    ```
    sudo chmod +x launch.sh
    sudo chmod +x update_wpa.sh
    ```

- use crontab schedule startup job

  ```
  crontab -e # If this is your first time enter. Pick your favorite number and enter.
  
  #add this line at the end of file

  @reboot sudo /home/pi/router_app/launch.sh
  ```

- add routeing rule into iptables

    `sudo iptables -t nat -A POSTROUTING -o wlan1 -j MASQUERADE`

    - you can preserve the rule by using "iptables-persistent"
        ```
        sudo apt install iptables-persistent
        iptables-persistent save
        ```

- when you restart, access `http://192.168.5.1:9999` should be able visit the tab.
## Knowledge from Lecture

- DHCP
- SSH
- Iptables
- Kernel module
- crontab

## Usage

The control panel will be hosted at `http://192.165.5.1:9999`. 
And it require to enter account and password to login.
The default account and password will be hard code as `adminpi` and `raspberry`.

<big>*** ONCE AGAIN! THIS PROJECT IS NOT AIM FOR PRODUCTION! ***</big>

The Application UI have basic authentication base on LAN IP.
In theory you will able to access the control panel once you login into any browser on your device.

After login, you will expect to see following layout.

```
+-----------------------------+-------------------------+
|       Network Status                                  |
+-----------------------------+-------------------------+
| Available Network                                     |
| update wifi status (button) | clean (button)          |
+-----------------------------+-------------------------+
| Config Network                                        |
| Network id (input)          | Select Network (button) |
|                                                       |
| reset (button)                                        |
| wpa-cli network                                       |
| (text area)                                           |
+-----------------------------+-------------------------+
```

- Network Status

    This section will display the current connection status.

    If router current does not connect to any wifi, the following text will be display:

    ```
    Router does not connect to any WiFi.
    ```
    Otherwise, it will display the current connected wifi SSID and ip address:
    
    ```
    +---------+-------------+
    |  ssid   | ip address  |
    +---------+-------------+
    | example | 192.168.0.1 |
    +---------+-------------+
    ```

    You can get the latest state by refreshing the control panel webpage.

- Available Network

    This section will display the nearby wifi info.
    Assumed your USB wifi adapter work as intended, you can get the nearby wifi by clicking `update wifi status` button. Which will generate following result.

    ```
    +------------+-------------+-------------------+----------+--------+-----------+---------+------------+----------------+
    | cellnumber |    ssid     |    mac address    | protocal |  mode  | frequency | channel | encryption | signal quality |
    +------------+-------------+-------------------+----------+--------+-----------+---------+------------+----------------+
    |         01 | exampleWifi | 11:22:33:44:55:66 | WPA2     | Master | 2.462 GHz |      11 | on         |             80 |
    +------------+-------------+-------------------+----------+--------+-----------+---------+------------+----------------+
    ```

    update the table by clicking the `update wifi status` button again.

    if you want to clean the session table, click `clean` button.

- Config Network
    
    - Overview

      The router will connect the network according value of the `Network id` value.

      `Network id` will be the the `index` of the setting json.

      All the network configuration will be written into `wpa_supplicant-wlan1.conf` (USB wifi adapter config file).

      The `Network id` option will try to access the network.
      If the connection fail then will fallback to any network available in network config.

      ```
             +---------+
             |select id|
             +----+----+
                  |
                  v
        +---------------------+
        |apply network setting|
        +---------+-----------+
                  |
                  v
      +-------------------------+
      | select hotspot by index |
      +-----------+-------------+
                  |
                  v
         +-----------------+
         | connect network |
         +-----------------+
       ```
    - Network ID
        
        The value will be the index position of the `wpa-cli network` config json array.
        Submit `Network ID` by clicking `Select network` button.
        Which will select the correspond network in your `wpa-cli network` config json array.

    - wpa-cli network

        This is where you configure the wifi of your device.

        <big>CURRENTLY ONLY SUPPORT PSK WIFI</big>

        Each json object shall follow this schema:
        
        ```json
        {
            "ssid": "ssid",
            "psk": "password"
        }
        ```

        And must wrap by an array:

        ```json
        [
            {
                "ssid": "wifi01",
                "psk": "foo"
            },
            {
                "ssid": "exampleWifiABC",
                "psk": "aabbccddeeffgg"
            }
        ]
        ```
        Perviously motioned `Network ID` will control which wifi shall be connected if available.
        For example: to connect "wifi01", Network ID shall be 0, to connect "exampleWifiABC", Network ID shall be 1.

        To update the network setting, click the `Select Network` button.

        If you want to rollback the current setting, click `reset` button.
        This will rollback the last time when `Select Network` clicked.

## Job Assignment

- Implementation (Hot spot)
    - 110213011 黃楷俊
    - 110213012 陳維德

- Implementation (Control UI)
    - 110213041 陳家輝
    - 110213077 陳慧珍

- Concept
    - 110213041 陳家輝
    - 110213044 陳俊傑

## References
- [Setting up a Raspberry Pi 3 as an Access Point](https://learn.sparkfun.com/tutorials/setting-up-a-raspberry-pi-3-as-an-access-point/all)
- [[Raspberry]Raspberry Pi 3 model B 變身為WiFi AP (Bridge mode)](https://tkunlin.medium.com/raspberry-raspberry-pi-3-model-b-%E8%AE%8A%E8%BA%AB%E7%82%BAwifi-ap-bridge-mode-8790884fe17)
- [YouTube - Raspberry Pi Travel Router - RaspAP - Everyday Tech](https://www.youtube.com/watch?v=m2JvWFr8bX4)
- [YouTube - Update Python on Raspberry Pi / Change Python Version | Simple Guide | Complete - TroubleChute](https://www.youtube.com/watch?v=Cj7NhuLkvdQ)
