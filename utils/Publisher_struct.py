import rclpy
import time
import collections
import numpy as np
#import matplotlib.pyplot as plt

#from tempfile import TemporaryFile
from b360.msg import DetectionStructure,RadarMessage,RadarStatusMessage,LidarMessage,LidarPointStructure
from multiprocessing import Manager
from multiprocessing.managers import BaseManager

nodes = {}

def NodeCreate(node_name):
    global nodes
    rclpy.init(args=None)
    node = rclpy.create_node(node_name)
    
    nodes[node_name] = node
    
    print(node_name,' node created!!!!')
    
    #print(nodes)

def ROS2CreatePublisherTopic(obj, pub_arg, node_name, topic_name):
    if pub_arg == True:
        # nodes_upd = {}
        # BaseManager.register('ROS2Publisher', ROS2Publisher)
        # manager = BaseManager()
        # manager.start()
        if node_name not in nodes:
            NodeCreate(node_name)
        # nodes_upd = nodes

        # obj.pub_obj = manager.ROS2Publisher(nodes, node_name, topic_name)
        obj.pub_obj = ROS2Publisher(node_name, topic_name)
        obj.pub_flag = True
    else:
        obj.pub_flag = False
    
class ROS2Publisher():
    def __init__(self, node_name, topic_name):
        self.node_name = node_name
        self.topic_name = topic_name
        if 'radar' in self.node_name.lower():
            self.publisher = nodes[self.node_name].create_publisher(RadarMessage, self.topic_name)
        elif 'lidar' in self.node_name.lower():
            self.publisher = nodes[self.node_name].create_publisher(LidarMessage, self.topic_name)
        #print('Created publisher', self.publisher, 'at node ', nodes[self.node_name])

    def timer_callback(self, ros_msg):
        # nodes[self.node_name].get_logger().info('Publishing: "%s" \n \n' %(ros_msg.points[-1].timestamp))
        nodes[self.node_name].get_logger().info('Publishing: "%s" \n \n' %(ros_msg.ip))
        self.publisher.publish(ros_msg)

    def set_publish_as_ros2msg(self, msglist, mountingparms):
        if 'radar' in self.node_name.lower(): 
            print('Publishing Radar')
            ros_msg = RadarMessage()
            detection_list=[]
            for msg in self.flatten(msglist):
                ros_msg.ip = msg.ip
                ros_msg.rdi_type = msg.rdiType
                ros_msg.message_counter = 0
                #ros_msg.message_counter = msg.messageCounter
                ros_msg.utc_time_stamp = msg.utcTimeStamp
                ros_msg.time_stamp = msg.timeStamp
                # ros_msg.mesurment_counter = msg.mesurmentCounter
                ros_msg.mesurment_counter = 0
                # ros_msg.cycle_counter = msg.cycleCounter
                ros_msg.cycle_counter = 0
                ros_msg.nof_detections = msg.nofDetections

                ros_msg.v_ambig = msg.vAmbig
                # ros_msg.center_frequency = msg.centerFrequency
                ros_msg.center_frequency = 0
                # ros_msg.detections_in_packet = msg.detectionsInPacket
                ros_msg.detections_in_packet = 0
                iter_lim = 38
                if msg.rdiType == 'Far1' or msg.rdiType == 'Near2':
                    iter_lim = 32
                # print(msg.rdiType, iter_lim)
                for i in range(0, iter_lim):
                    # print(msg.rdiType,iter_lim, i, len(msg.radarDetectionList))
                    detection_struct = DetectionStructure()
                    detection_struct.f_range = float(msg.radarDetectionList[i].f_Range) *0.00457777642139958
                    detection_struct.f_v_rel_rad = float(msg.radarDetectionList[i].f_VrelRad) * 0.00457777642139958
                    detection_struct.f_az_ang0 = float(msg.radarDetectionList[i].f_AzAng0)* 0.0000958767251683096
                    detection_struct.f_az_ang1 = float(msg.radarDetectionList[i].f_AzAng1)* 0.0000958767251683096
                    detection_struct.f_el_ang = float(msg.radarDetectionList[i].f_ElAng)* 0.0000958767251683096
                    detection_struct.f_rcs0 = float(msg.radarDetectionList[i].f_RCS0) * 0.00305185094759972
                    detection_struct.f_rcs1 = float(msg.radarDetectionList[i].f_RCS1) * 0.00305185094759972
                    detection_struct.f_prob0 = float(msg.radarDetectionList[i].f_Prob0) * 0.00393700787401575
                    detection_struct.f_prob1 = float(msg.radarDetectionList[i].f_Prob1) * 0.00393700787401575
                    detection_struct.f_range_var = float(msg.radarDetectionList[i].f_RangeVar) * 0.000152592547379986
                    detection_struct.f_vrel_rad_var = float(msg.radarDetectionList[i].f_VrelRadVar) * 0.000152592547379986
                    detection_struct.f_az_ang_var0 = float(msg.radarDetectionList[i].f_AzAngVar0) * 0.0000152592547379986
                    detection_struct.f_az_ang_var1 = float(msg.radarDetectionList[i].f_AzAngVar1) * 0.0000152592547379986
                    detection_struct.f_el_ang_var = float(msg.radarDetectionList[i].f_ElAngVar) * 0.0000152592547379986
                    detection_struct.f_pdh0 = float(msg.radarDetectionList[i].f_Pdh0)
                    detection_struct.f_snr = float(msg.radarDetectionList[i].f_SNR) * 0.1
                    detection_struct.ros_timestamp = float(nodes[self.node_name].get_clock().now().nanoseconds)

                    if detection_struct.f_range > 0:
                        detection_struct.f_range, detection_struct.f_az_ang0, detection_struct.f_el_ang =  offset_adj_radar(detection_struct.f_range, detection_struct.f_az_ang0, detection_struct.f_el_ang, mountingparms)
                    detection_list.append(detection_struct)
                    
            ros_msg.radar_detection_list = detection_list[0:ros_msg.nof_detections]
            self.timer_callback(ros_msg)

        elif 'lidar' in self.node_name.lower():
            while True:
                ros_msg = LidarMessage()
                
                msg = msglist.get()
                message = msg[0]

                ros_msg.id = msg[1]
                ros_msg.ip = msg[2]

                # start = time.time()
                for point in message:
                    point_struct = LidarPointStructure()
                    point = list(point)
                    
                    point_struct.x = point[0]
                    point_struct.y = point[1]
                    point_struct.z = point[2]
                    point_struct.reflectivity = point[3]
                    point_struct.ros_timestamp = float(nodes[self.node_name].get_clock().now().nanoseconds)
                    # point_struct.timestamp = str(nodes[self.node_name].get_clock().now())
                
                    ros_msg.points.append(point_struct)

                self.timer_callback(ros_msg)
                # print('Time taken to publish', time.time() - start)
        
    def flatten(self,l):
        for el in l:
            if isinstance(el, collections.Iterable) and not isinstance(el, (str, bytes)):
                yield from self.flatten(el)
            else:
                yield el

def offset_adj_radar(r,az,el,mountingparms):
    X = Y = Z = 0
    if mountingparms.y > 0:
        if np.absolute(mountingparms.orientation) > 0:
            az = float(np.deg2rad(np.degrees(az) + mountingparms.orientation))
        X = mountingparms.x + r*np.sin(np.deg2rad(90)-el)*np.cos(np.deg2rad(90)+az)
        Y = mountingparms.y + r*np.sin(np.deg2rad(90)-el)*np.sin(np.deg2rad(90)+az)
        Z = mountingparms.z + r*np.cos(np.deg2rad(90)-el)
    elif mountingparms.y < 0:
        if np.absolute(mountingparms.orientation) > 0:
            az = float(np.deg2rad(np.degrees(az) - mountingparms.orientation))
        X = mountingparms.x - r*np.sin(np.deg2rad(90)-el)*np.cos(np.deg2rad(90)+az)
        Y = mountingparms.y - r*np.sin(np.deg2rad(90)-el)*np.sin(np.deg2rad(90)+az)
        Z = mountingparms.z - r*np.cos(np.deg2rad(90)-el)

    f_range = float(np.sqrt(np.square(X) + np.square(Y) + np.square(Z)))
    f_az_ang0 = float(np.degrees(np.arctan2(Y,X)) - 90)
    f_el_ang = float(90 - np.degrees(np.arctan2(np.sqrt(np.square(X) + np.square(Y)), Z)))
    
    return f_range, f_az_ang0, f_el_ang

def offset_adj_lidar(r, az,el,mountingparms):
    r = np.asarray(r)
    az = np.asarray(az)
    el = np.asarray(el)

    X = mountingparms.x + r*np.sin(az)*np.cos(el)
    Y = mountingparms.y + r*np.cos(az)*np.cos(el)
    Z = mountingparms.z + r*np.sin(el)
    
    return X,Y,Z
        
