import time
import sys
import openvr
import math

# Function to print out text but instead of starting a new line it will overwrite the existing line
def update_text(txt):
    sys.stdout.write('\r'+txt)
    sys.stdout.flush()

def get_threesixtyatan(num):
    ret = math.degrees(num)
    
    ret = (ret + 360)%360

    return math.radians(ret)

#Convert the standard 3x4 position/rotation matrix to a x,y,z location and the appropriate Euler angles (in degrees)
def convert_to_euler(pose_mat):
    rad_list = convert_to_radians(pose_mat)
    return [rad_list[0],rad_list[1],rad_list[2],math.degrees(rad_list[3]),math.degrees(rad_list[4]),math.degrees(rad_list[5])]

#Convert the 3x4 position/rotation matrix to a x,y,z location and the appropriate Euler angles (in radians)
def convert_to_radians(pose_mat):
    quat_pose_list = convert_to_quaternion(pose_mat)
    x = quat_pose_list[0]
    y = quat_pose_list[1]
    z = quat_pose_list[2]
    
    q0 = quat_pose_list[3]
    q1 = quat_pose_list[4]
    q2 = quat_pose_list[5]
    q3 = quat_pose_list[6]

    sinr_cosp = 2*(q0*q1+q2*q3)
    cosr_cosp = 1-2*(q1**2 + q2**2)
    sinp = 2*(q0*q2-q3*q1)
    siny_cosp = 2*(q0*q3+q1*q2)
    cosy_cosp = 1-2*(q2**2+q3**2)
    
    phi = math.atan2(sinr_cosp, cosr_cosp)
    phi = get_threesixtyatan(phi)
    
    theta = math.asin(sinp)

    psi = math.atan2(siny_cosp, cosy_cosp)
    psi = get_threesixtyatan(psi)
    
    return [x, y, z, phi, theta, psi]

#Convert the standard 3x4 position/rotation matrix to a x,y,z location and the appropriate Quaternion
def convert_to_quaternion(pose_mat):
    r_w = math.sqrt( max( 0, 1 + pose_mat[0][0] + pose_mat[1][1]+ pose_mat[2][2] ) ) / 2
    r_x = math.sqrt( max( 0, 1 + pose_mat[0][0] - pose_mat[1][1] - pose_mat[2][2] ) ) / 2
    r_y = math.sqrt( max( 0, 1 - pose_mat[0][0] + pose_mat[1][1] - pose_mat[2][2] ) ) / 2
    r_z = math.sqrt( max( 0, 1 - pose_mat[0][0] - pose_mat[1][1] + pose_mat[2][2] ) ) / 2
    r_x *= math.copysign(1, r_x * ( -pose_mat[2][1] + pose_mat[1][2] ) )
    r_y *= math.copysign(1,r_y * ( -pose_mat[0][2] + pose_mat[2][0] ) )
    r_z *= math.copysign(1,r_z * ( pose_mat[1][0] - pose_mat[0][1] ) )

    x = pose_mat[0][3]
    y = pose_mat[1][3]
    z = pose_mat[2][3]
    return [x,y,z,r_w,r_x,r_y,r_z]

#Define a class to make it easy to append pose matricies and convert to both Euler and Quaternion for plotting
class pose_sample_buffer():
    def __init__(self):
        self.i = 0
        self.index = []
        self.time = []
        self.x = []
        self.y = []
        self.z = []
        self.yaw = []
        self.pitch = []
        self.roll = []
        self.r_w = []
        self.r_x = []
        self.r_y = []
        self.r_z = []
    
    def append(self,pose_mat,t):
        self.time.append(t)
        self.x.append(pose_mat[0][3])
        self.y.append(pose_mat[1][3])
        self.z.append(pose_mat[2][3])
        self.yaw.append(180 / math.pi * math.atan(pose_mat[1][0] /pose_mat[0][0]))
        self.pitch.append(180 / math.pi * math.atan(-1 * pose_mat[2][0] / math.sqrt(pow(pose_mat[2][1], 2) + math.pow(pose_mat[2][2], 2))))
        self.roll.append(180 / math.pi * math.atan(pose_mat[2][1] /pose_mat[2][2]))
        r_w = math.sqrt(abs(1+pose_mat[0][0]+pose_mat[1][1]+pose_mat[2][2]))/2
        self.r_w.append(r_w)
        self.r_x.append((pose_mat[2][1]-pose_mat[1][2])/(4*r_w))
        self.r_y.append((pose_mat[0][2]-pose_mat[2][0])/(4*r_w))
        self.r_z.append((pose_mat[1][0]-pose_mat[0][1])/(4*r_w))

class vr_tracked_device():
    def __init__(self,vr_obj,index,device_class):
        self.device_class = device_class
        self.index = index
        self.vr = vr_obj
        
    def get_serial(self):
        return self.vr.getStringTrackedDeviceProperty(self.index,openvr.Prop_SerialNumber_String).decode('utf-8')
    
    def get_model(self):
        return self.vr.getStringTrackedDeviceProperty(self.index,openvr.Prop_ModelNumber_String).decode('utf-8')
        
    def sample(self,num_samples,sample_rate):
        interval = 1/sample_rate
        rtn = pose_sample_buffer()
        sample_start = time.time()
        for i in range(num_samples):
            start = time.time()
            pose = self.vr.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseStanding, 0,openvr.k_unMaxTrackedDeviceCount)
            rtn.append(pose[self.index].mDeviceToAbsoluteTracking,time.time()-sample_start)
            sleep_time = interval- (time.time()-start)
            if sleep_time>0:
                time.sleep(sleep_time)
        return rtn
        
    def get_pose_euler(self):
        pose = self.vr.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseSeated, 0,openvr.k_unMaxTrackedDeviceCount)
        return convert_to_euler(pose[self.index].mDeviceToAbsoluteTracking)
    
    def get_pose_radians(self):
        pose = self.vr.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseStanding, 0,openvr.k_unMaxTrackedDeviceCount)
        return convert_to_radians(pose[self.index].mDeviceToAbsoluteTracking)
    
    def get_pose_quaternion(self):
        pose = self.vr.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseStanding, 0,openvr.k_unMaxTrackedDeviceCount)
        return convert_to_quaternion(pose[self.index].mDeviceToAbsoluteTracking)

class vr_tracking_reference(vr_tracked_device):
    def get_mode(self):
        return self.vr.getStringTrackedDeviceProperty(self.index,openvr.Prop_ModeLabel_String).decode('utf-8').upper()
    def sample(self,num_samples,sample_rate):
        print("Warning: Tracking References do not move, sample isn't much use...")
        
class triad_openvr():
    def __init__(self):
        # Initialize OpenVR in the 
        self.vr = openvr.init(openvr.VRApplication_Other)
        
        # Initializing object to hold indexes for various tracked objects 
        self.object_names = {"Tracking Reference":[],"HMD":[],"Controller":[],"Tracker":[]}
        self.devices = {}
        self.vr.resetSeatedZeroPose()
        poses = self.vr.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseStanding, 0,
                                                               openvr.k_unMaxTrackedDeviceCount)
        # Iterate through the pose list to find the active devices and determine their type
        for i in range(openvr.k_unMaxTrackedDeviceCount):
            if poses[i].bPoseIsValid:
                device_class = self.vr.getTrackedDeviceClass(i)
                if (device_class == openvr.TrackedDeviceClass_Controller):
                    device_name = "controller_"+str(len(self.object_names["Controller"])+1)
                    self.object_names["Controller"].append(device_name)
                    self.devices[device_name] = vr_tracked_device(self.vr,i,"Controller")
                elif (device_class == openvr.TrackedDeviceClass_HMD):
                    device_name = "hmd_"+str(len(self.object_names["HMD"])+1)
                    self.object_names["HMD"].append(device_name)
                    self.devices[device_name] = vr_tracked_device(self.vr,i,"HMD")
                elif (device_class == openvr.TrackedDeviceClass_GenericTracker):
                    device_name = "tracker_"+str(len(self.object_names["Tracker"])+1)
                    self.object_names["Tracker"].append(device_name)
                    self.devices[device_name] = vr_tracked_device(self.vr,i,"Tracker")
                elif (device_class == openvr.TrackedDeviceClass_TrackingReference):
                    device_name = "tracking_reference_"+str(len(self.object_names["Tracking Reference"])+1)
                    self.object_names["Tracking Reference"].append(device_name)
                    self.devices[device_name] = vr_tracking_reference(self.vr,i,"Tracking Reference")
    
    def rename_device(self,old_device_name,new_device_name):
        self.devices[new_device_name] = self.devices.pop(old_device_name)
        for i in range(len(self.object_names[self.devices[new_device_name].device_class])):
            if self.object_names[self.devices[new_device_name].device_class][i] == old_device_name:
                self.object_names[self.devices[new_device_name].device_class][i] = new_device_name
    
    def print_discovered_objects(self):   
        for device_type in self.object_names:
            plural = device_type
            if len(self.object_names[device_type])!=1:
                plural+="s"
            print("Found "+str(len(self.object_names[device_type]))+" "+plural)
            for device in self.object_names[device_type]:
                if device_type == "Tracking Reference":
                    print("  "+device+" ("+self.devices[device].get_serial()+
                          ", Mode "+self.devices[device].get_mode()+
                          ", "+self.devices[device].get_model()+
                          ")")
                else:
                    print("  "+device+" ("+self.devices[device].get_serial()+
                          ", "+self.devices[device].get_model()+")")
