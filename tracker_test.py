print("0");
import triad_openvr
import time
import sys
import smooth_movement

v = triad_openvr.triad_openvr()
v.print_discovered_objects()

trackers = {}
for key, device in v.devices.items():
    if (device.device_class == 'Tracker'):
        trackers[key] = (device.get_serial(), smooth_movement.Smoother())

if len(sys.argv) == 1:
    interval = 1/250
elif len(sys.argv) == 2:
    interval = 1/float(sys.argv[1])
else:
    print("Invalid number of arguments")
    interval = False

smoother = smooth_movement.Smoother()
if interval:
    while(True):
        start = time.time()
        for tracker_id, (tracker_serial, smoother) in trackers.items():
            pos = v.devices[tracker_id].get_pose_euler()
            if pos is not None:
                txt = tracker_serial + " "
                #pos = smoother.smooth(pos)
                for each in pos:
                    txt += "%.4f" % each
                    txt += " "
                print("\r" + txt)
            sleep_time = interval-(time.time()-start)
            if sleep_time>0:
                time.sleep(sleep_time)
