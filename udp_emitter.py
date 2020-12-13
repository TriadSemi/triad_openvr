import triad_openvr
import time
import sys
import smooth_movement
import struct
import socket
import ipaddress
import argparse
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


parser = argparse.ArgumentParser(description='Vive Tracker UDP')
parser.add_argument('--ip', type=str, required=False, default='127.0.0.1', help='IP address of the target machine')
parser.add_argument('--port', type=int, required=False, default=8051, help='IP address of the target machine')
parser.add_argument('--mode', type=str, required=False, default="quaternion", choices=['quaternion', 'euler'],
                    help='Rotation representation mode [quaternion, euler]')
parser.add_argument('--fps', type=int, required=False, default=250, help='Sample rate')
args = parser.parse_args()


if ipaddress.ip_address(args.ip).is_multicast:
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

MODE_EULER = 0
MODE_QUATERNION = 1

mode = MODE_QUATERNION if args.mode == 'quaternion' else MODE_EULER

print(f"Sending UDP to {args.ip}:{args.port}")
sock.connect((args.ip, args.port))

v = triad_openvr.triad_openvr()
v.print_discovered_objects()

trackers = {}
for key, device in v.devices.items():
    if (device.device_class == 'Tracker'):
        trackers[key] = (device.get_serial(), (bytes(device.get_serial(), 'utf-8') + bytes(31))[:31], smooth_movement.Smoother())

interval = 1 / args.fps

smoother = smooth_movement.Smoother()
while True:
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
        if sleep_time > 0:
            time.sleep(sleep_time)
