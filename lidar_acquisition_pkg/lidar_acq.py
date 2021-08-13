import argparse
import os
import csv
import sys
sys.path.append('/home/conti/Desktop/SensorAcquisition/sensor_packages/src/utils')

from Publisher_struct import ROS2CreatePublisherTopic, offset_adj_lidar

import socket
import glob
from datetime import datetime, timedelta
import struct
import time
import traceback
import numpy as np
from multiprocessing import Process, Queue, Pool
import yaml
import matplotlib.pyplot as plt
from multiprocessing import Manager
from multiprocessing.managers import BaseManager
from Lidar_struct import Lidar
from displaz import *
from vispy_visualizer import VispyViz

obj_count = 0
data = None
ts = 0
pub_arg = True

def displaz_plot(lidar):
	while True:
		if lidar.POINT_QUEUE.empty():
			pass
		else:
			msg = lidar.POINT_QUEUE.get()
			X = msg['X']
			Y = msg['Y']
			Z = msg['Z']
			ref = msg['Ref']
			tim = msg['Time']

			to_return_pts = np.float64(np.asmatrix(np.column_stack(( X,Y,Z))))
			norm = plt.Normalize()
			colors = plt.cm.jet(norm(ref))
			_colors = colors[:,:-1]
			to_return_clr = np.float64(np.asmatrix(_colors))
			plot(to_return_pts, color = to_return_clr, label=lidar.id)

def vispy_plot(lidar, vispy_obj):
	while True:
		if lidar.POINT_QUEUE.empty():
			pass
		else:
			vispy_obj.q.put(lidar.POINT_QUEUE.get())
	

def unpack(lidar):
	scan_index = 0
	prev_azimuth = None
	start = time.time()
	_dist = []
	_azimuth = []
	_elevation = []
	_time_offset=[]
	_reflectivity = []

	while True:
		if lidar.DATA_QUEUE.empty():
			pass
		else:
			
			msg = lidar.DATA_QUEUE.get()
			data = msg['data']
			ts = msg['time']
	
			timestamp, factory = struct.unpack_from("<IH", data, offset=1200)
				# print(lidar.ip)
			if lidar.id == 'VLP-16':	
				assert factory == 0x2237, hex(factory)	  # 0x22=VLP-16, 0x37=Strongest Return
			elif lidar.id == 'VLP-32':
				assert factory == 0x2837, hex(factory)

			timestamp = float(ts)
			seq_index = 0
			for offset in range(0, 1200, 100):
				flag, azimuth = struct.unpack_from("<HH", data, offset)
				
				
				assert flag == 0xEEFF, 'Flag is %s' %hex(flag)
				if lidar.id == 'VLP-16':
					for step in range(2):
						seq_index += 1
						azimuth += step
						azimuth %= lidar.ROTATION_MAX_UNITS
						# print('azimuth angle', azimuth/100.0)

						if prev_azimuth is not None and azimuth < prev_azimuth:
							scan_index += 1
							# X,Y,Z = calc(_dist,_azimuth,_elevation,lidar.MOUNTINGPARMS)

							X,Y,Z = offset_adj_lidar(_dist, _azimuth, _elevation, lidar.MOUNTINGPARMS)

							ref = np.asarray(_reflectivity)
							tim = np.asarray(_time_offset)

							# print(len(X))
							# lidar.POINT_QUEUE.put({'X': X, 'Y': Y, 'Z': Z, 'Ref': ref, 'Time': tim})
							lidar.POINTS.put([np.column_stack((X,Y,Z,ref,tim)), lidar.id, lidar.ip])
							norm = plt.Normalize()
							colors = plt.cm.jet(norm(ref))
							_colors = colors[:,:-1]
							_colr = np.float64(np.asmatrix(_colors))
							lidar.POINT_QUEUE.put({'pcld': np.column_stack((X,Y,Z)), 'colr': _colr})
							
							_dist = []
							_azimuth = []
							_elevation = []
							_reflectivity =[]
							_time_offset= []

						prev_azimuth = azimuth
						arr = struct.unpack_from('<' + "HB" * 16, data, offset + 4 + step * 48)

						for i in range(lidar.NUM_LASERS):
							_time_offset.append((55.296 * seq_index + 2.304 * i) / 1000000.0)
							_dist.append(arr[i * 2])
							_azimuth.append(azimuth / 100.0 * np.pi / 180.0)
							_elevation.append(lidar.LASER_ANGLES[i] * np.pi / 180.0)
							_reflectivity.append(i*2+1)

				elif lidar.id == 'VLP-32':
				# if lidar.id == 'VLP-32':
					seq_index += 1
					azimuth %= lidar.ROTATION_MAX_UNITS

					if prev_azimuth is not None and azimuth < prev_azimuth:
						scan_index += 1
						# X,Y,Z = calc(_dist,_azimuth,_elevation,lidar.MOUNTINGPARMS)

						X,Y,Z = offset_adj_lidar(_dist, _azimuth, _elevation, lidar.MOUNTINGPARMS)

						ref = np.asarray(_reflectivity)
						tim = np.asarray(_time_offset)

						# print(len(X))
						lidar.POINTS.put([np.column_stack((X,Y,Z,ref,tim)), lidar.id, lidar.ip])
						# lidar.POINT_QUEUE.put({'X': X, 'Y': Y, 'Z': Z, 'Ref': ref, 'Time': tim})

						norm = plt.Normalize()
						colors = plt.cm.jet(norm(ref))
						_colors = colors[:,:-1]
						
						_colr = np.float64(np.asmatrix(_colors))
						lidar.POINT_QUEUE.put({'pcld': np.column_stack((X,Y,Z)), 'colr': _colr})
						
						_dist = []
						_azimuth = []
						_elevation = []
						_reflectivity =[] 
						_time_offset= []

					prev_azimuth = azimuth
					arr = struct.unpack_from('<' + "HB" * 32, data, offset + 4)

					for i in range(lidar.NUM_LASERS):
						_time_offset.append((46.080 * seq_index + 1.152 * i) / 1000000.0)
						_dist.append(arr[i * 2])

						_azimuth.append((azimuth / 100.0 * np.pi / 180.0) + np.deg2rad(lidar.AZIMUTH_OFFSET[i]))
						_elevation.append(lidar.LASER_ANGLES[i] * np.pi / 180.0)
						_reflectivity.append(i*2+1)
				else:
					# print('In 64')
					pass

def capture(lidar, sock):
	# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
	sock.bind(('', 2368))
	try:
		while True:
			try:
				data, addr = sock.recvfrom(2000)
				# 
				if len(data) > 0 and addr[0] == lidar.ip:
					assert len(data) == 1206
					lidar.DATA_QUEUE.put({'data': data, 'time': time.time()})
			except Exception as e:
				print(dir(e), e.message, e.__class__.__name__)
				traceback.print_exc(e)
	except KeyboardInterrupt as e:
		print(e)

if __name__ == "__main__":
	sensors = []
	parser = argparse.ArgumentParser(description='Parsing Voxel project arguments')

	parser.add_argument("-pub", "--publish_ros2_msg", required=False, help="yes to publish as ros2 msg")
	parser.add_argument("-display", "--displaz", required=False, help="yes to display lidar points")

	args = vars(parser.parse_args())

	processes = []

	config = None
	os.chdir('/home/conti/Desktop/SensorAcquisition/sensor_packages/src/utils/')
	with open('config.yaml') as f:
		config = yaml.safe_load(f)

	_t = config["Sensors"]["Lidars"]
	
	for lid in _t:
		obj_count += 1
		l = Lidar(lid)
		
		sensors.append(l)
		if args['publish_ros2_msg'] == 'yes':
			# BaseManager.register('ROS2Publisher', ROS2Publisher)
			# manager = BaseManager()
			# manager.start()
			# l.pub_obj = manager.ROS2Publisher(node_name = 'lidar_publisher', topic_name = 'Lidar_%d'%(obj_count))
			ROS2CreatePublisherTopic(l, pub_arg, node_name = 'lidar_publisher', topic_name = 'Lidar_%d'%(obj_count))
			# l.pub_obj = ROS2Publisher(node_name = 'lidar_publisher', topic_name = 'Lidar_%d'%(obj_count))
			l.PUB_FLAG = True
		else:
			l.PUB_FLAG = False

		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
		
		if args['displaz'] == 'yes':
			l.DISPLAY_FLAG = True
		p1 = Process(target = capture, args = (l,sock))
		# p1.start()
		processes.append(p1)	
		p2 = Process(target = unpack, args = (l,))
		# p2.start()
		processes.append(p2)

		if l.DISPLAY_FLAG == True:

			# p3 = Process(target = displaz_plot, args = (l,))
			# processes.append(p3)
			vispy_obj = VispyViz()


			p3 = Process(target = vispy_obj.start_vis, args =())
			p4 = Process(target = vispy_plot, args =(l, vispy_obj))

			processes.append(p3)
			processes.append(p4)

		if l.pub_flag == True:
		# if l.PUB_FLAG == True:
			p5 = Process(target = l.pub_obj.set_publish_as_ros2msg, args = (l.POINTS, l.MOUNTINGPARMS))
			processes.append(p5)
	
	# print('No. of processes', len(processes))
	for process in processes:
		process.start()
	for process in processes:
		process.join()

	top_dir = datetime.now().strftime('%Y-%m-%d_%H%M%S')
