from __future__ import print_function
import triad_openvr
import time
import sys

v = triad_openvr.triad_openvr()
v.print_discovered_objects()
interval = 1/250


while(True):
    start = time.time()
    txt = ""
    for each in v.devices["controller_1"].get_pose_euler():
        txt += "%.0f" % each
        txt += " "
    print("\r" + txt, end="")
    sleep_time = interval-(time.time()-start)
    if sleep_time>0:
        time.sleep(sleep_time)