import triad_openvr
import time
import sys
import smooth_movement
import struct
import socket
import ipaddress

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('127.0.0.1' if len(sys.argv)<2 else sys.argv[1], 8051 if len(sys.argv)<3 else int(sys.argv[2]))
if ipaddress.ip_address(server_address[0]).is_multicast:
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

MODE_EULER = 0
MODE_QUATERNION = 1

mode = MODE_QUATERNION # todo: read from argv

print("Sending UDP to", server_address)
sock.connect(server_address)

v = triad_openvr.triad_openvr()
v.print_discovered_objects()

trackers = {}
for key, device in v.devices.items():
    if (device.device_class == 'Tracker'):
        trackers[key] = (device.get_serial(), (bytes(device.get_serial(), 'utf-8') + bytes(31))[:31], smooth_movement.Smoother())
if len(sys.argv) == 3:
    interval = 1/float(sys.argv[2])
else:
    interval = 1/250

smoother = smooth_movement.Smoother()
while(True):
    start = time.time()
    for tracker_id, (tracker_serial, packet_header, smoother) in trackers.items():
        try:
            pos = v.devices[tracker_id].get_pose_euler() if mode == MODE_EULER else v.devices[tracker_id].get_pose_quaternion()
            if pos is not None:
                txt = tracker_serial
                #pos = smoother.smooth(pos)
                if mode == MODE_EULER:
                    txt += " Euler      "
                    packet = struct.pack('31sBdddddd', packet_header, mode, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5])
                else:
                    txt += " Quaternion "
                    packet = struct.pack('31sBddddddd', packet_header, mode, pos[0], pos[1], pos[2], pos[3], pos[4], pos[5], pos[6])
                sent = sock.send(packet)
                for each in pos:
                    txt += "%9.4f" % each
                    txt += " "
                print("\r" + txt)
        except:
            pass
        sleep_time = interval-(time.time()-start)
        if sleep_time>0:
            time.sleep(sleep_time)
