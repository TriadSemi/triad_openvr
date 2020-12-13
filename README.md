# Vive tracker UDP Server

UDP server for Vive Tracker.
Based on [this repository](https://github.com/TriadSemi/triad_openvr).

## Prerequisites 
Follow [this](https://www.acer.com/ac/en/US/content/windows-mixed-reality-setup-steamvr) to install SteamVR

Follow [this](http://help.triadsemi.com/en/articles/836917-steamvr-tracking-without-an-hmd) to configure SteamVR

Follow [this](https://github.com/cmbruns/pyopenvr) for Python prerequisites

## Setup 
1. Setup at least two Vive lighthouses
2. Connect lighthouse dongle to the local machine
3. Pair the Vive tracker to steamVR [link](https://www.vive.com/us/support/wireless-tracker/category_howto/pairing-vive-tracker.html).


## Run 
```bash
python udp_emitter.py [-h] [--ip IP] [--port PORT] [--mode {quaternion,euler}]
```

* IP should be the IP of the target device, and it defaults to loopback (`127.0.0.1`)
* Port defaults to `8051`
* Mode defaults to `quaternion`

## Test

Run the following on the target device to verify the incoming UDP:

```python
import socket

UDP_IP = "0.0.0.0"
UDP_PORT = 8051

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print("received message: %s" % data)
```


## Unity
To enable data aquisition in a unity editor:
1. Disable all Firewalls, or allow Unity editor in private and public network
2. Make sure `block incomming connections` tickbox is disabled in Windows Firewall settings