from multiprocessing import Queue, Manager
from b360.msg import LidarMessage,LidarPointStructure

class Lidar(object):
	def __init__(self, l):
		
		self.m = Manager()

		self.port = None
		self.id = l["id"]
		self.ip = l["ip"]
		
		self.MOUNTINGPARMS = MountingParameters()
		self.MOUNTINGPARMS.x = l["mounting_parameter"]["X"]
		self.MOUNTINGPARMS.y = l["mounting_parameter"]["Y"]
		self.MOUNTINGPARMS.z = l["mounting_parameter"]["Z"]
		self.MOUNTINGPARMS.orientation = l["orientation"]

		self.PUB_FLAG = None
		self.DISPLAY_FLAG = None
		
		self.LASER_ANGLES = []
		self.NUM_LASERS = None
		self.EXPECTED_PACKET_TIME = None
		self.EXPECTED_SCAN_DURATION = None
		self.DISTANCE_RESOLUTION = None
		self.ROTATION_RESOLUTION = None
		self.ROTATION_MAX_UNITS = None
		self.DATA_QUEUE = Queue()
		self.POINT_QUEUE = Queue()
		self.POINTS = self.m.Queue()

		self.lidar_attributes()


	def lidar_attributes(self):
		if self.id == 'VLP-16':
			self.port = 2368
			self.LASER_ANGLES = [-15, 1, -13, 3, -11, 5, -9, 7, -7, 9, -5, 11, -3, 13, -1, 15]
			self.NUM_LASERS = 16
			self.EXPECTED_PACKET_TIME = 0.001327
			self.EXPECTED_SCAN_DURATION = 0.1
			self.DISTANCE_RESOLUTION = 0.002
			self.ROTATION_RESOLUTION = 0.01
			self.ROTATION_MAX_UNITS = 36000
		elif self.id == 'VLP-32':
			self.port = 2368
			self.LASER_ANGLES = [-25, -1, -1.667, -15.639, -11.31, 0, -0.667, -8.843, -7.254, 0.333, -0.333, -6.148, -5.333, 1.333, 0.667, -4, -4.667, 1.667, 1, -3.667, -3.333, 3.333, 2.333, -2.667, -3, 7, 4.667, -2.333, -2, 15, 10.333, -1.333]
			self.AZIMUTH_OFFSET = [1.4, -4.2, 1.4, -1.4, 1.4, -1.4, 4.2, -1.4, 1.4, -4.2, 1.4, -1.4, 4.2, -1.4, 4.2, -1.4, 1.4, -4.2, 1.4, -4.2, 4.2, -1.4, 1.4, -1.4, 1.4, -1.4, 1.4, -4.2, 4.2, -1.4, 1.4, -1.4]
			self.NUM_LASERS = 32
			self.EXPECTED_PACKET_TIME = 0.001327
			self.EXPECTED_SCAN_DURATION = 0.1
			self.DISTANCE_RESOLUTION = 0.002
			self.ROTATION_RESOLUTION = 0.01
			self.ROTATION_MAX_UNITS = 36000


class MountingParameters(object):
	def __init__(self):
		self.x = 0
		self.y = 0
		self.z = 0
		self.orientation = 0