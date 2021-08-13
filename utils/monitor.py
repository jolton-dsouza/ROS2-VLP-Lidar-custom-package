import os.path
import os
import time

import tkinter as tk
from tkinter import messagebox as mb
import subprocess

# class Monitor():
# 	def __init__(self, gui, l, m):
# 		x = 20
# 		y = 20
# 		if l+m == 5:
# 			gui.canvas.create_oval(x + 130, y + 5, x + 150, y + 25, outline="black", fill = 'green', width=0)



class makeGUI():
	def __init__(self):
		self.sensors = ['/Radar_1', '/Radar_2', '/Radar_3', '/Radar_4', '/Radar_5', '/Radar_6', '/Radar_7', '/gmsl_camera/port_0/cam_0/image_raw/compressed', '/gmsl_camera/port_0/cam_1/image_raw/compressed', '/gmsl_camera/port_0/cam_2/image_raw/compressed', '/gmsl_camera/port_0/cam_3/image_raw/compressed', '/gmsl_camera/port_1/cam_0/image_raw/compressed', '/gmsl_camera/port_1/cam_1/image_raw/compressed', '/gmsl_camera/port_1/cam_2/image_raw/compressed', '/gmsl_camera/port_1/cam_3/image_raw/compressed']
		self.root = tk.Tk()
		self.root.title('System Monitor GUI')
		self.root.geometry('300x300')

		self.createWindow()

		tk.mainloop()
		# self.root.mainloop()


	def createWindow(self):
		self.x = 20
		self.y = 20

		self.cameras = self.sensors[7:]

		self.radars = self.sensors[0:7]

		self.canvas = tk.Canvas(self.root, width=500, height=500, borderwidth=0, highlightthickness=0, bg="white")
		self.canvas.grid()

		self.topicListButton = tk.Button(text = 'Check Topic List', command = self.topicListCheck)
		self.topicListButton.place(x= self.x, y = self.y)

		self.circle1 = self.canvas.create_oval(self.x + 150, self.y + 5, self.x + 170, self.y + 25, outline="red", fill = 'red', width=0)

		self.cameraButton = tk.Button(text = 'Check Cameras', command = lambda : self.checkSensors(self.cameras))
		self.cameraButton.place(x= self.x, y = self.y+50)

		self.circle2 = self.canvas.create_oval(self.x + 150, self.y + 55, self.x + 170, self.y + 75, outline="black", fill = 'red', width=0)

		self.radarButton = tk.Button(text = 'Check Radars', command = lambda : self.checkSensors(self.radars))
		self.radarButton.place(x= self.x, y = self.y+100)

		self.circle3 = self.canvas.create_oval(self.x + 150, self.y + 105, self.x + 170, self.y + 125, outline="black", fill = 'red', width=0)

		self.lidarButton = tk.Button(text = 'Check Lidar')
		self.lidarButton.place(x= self.x, y = self.y+150)

		self.circle4 = self.canvas.create_oval(self.x + 150, self.y + 155, self.x + 170, self.y + 175, outline="black", fill = 'red', width=0)

		self.quitButton = tk.Button(text = 'QUIT', bg = 'red', command = self.quitButton)
		self.quitButton.place(x= self.x+200, y = self.y+200)

	def topicListCheck(self):




		# if not os.path.exists('monitor_topic_list.txt'):
		# 	mb.showinfo(title = 'Error', message = 'monitor_topic_list.txt file not ready')
		# else:
			# self.f= open("monitor_topic_list.txt","r")
			# self.txt = self.f.read()
			# self.topic_list = self.txt.split('\n')

		time.sleep(5)
		self.p = subprocess.Popen(['ros2','topic', 'list'], stdout = subprocess.PIPE)
		self.out = ''

		while self.out is '':
			# print('proc_flag', proc_flag)
			try:
				self.out = self.p.communicate()[0].decode("utf-8")
			except Exception as e:
				print('Exception occured', e)
				

		
		self.topic_list = self.out.split('\n')	
		self.p.kill()

		self._tmp_sensors = []
		self._tmp_non_pub = []

		for sensor in self.sensors:
			if sensor in self.topic_list:
				#print(sensor, 'topic publishing')
				self._tmp_sensors.append(sensor)
			else:
				if ('Radar' or 'gmsl' or 'Lidar') in sensor: 
					mb.showinfo(title = 'Error', message = sensor+' not publishing')
					self._tmp_non_pub.append(sensor)

		if self._tmp_sensors == self.sensors:
			self.canvas.itemconfig(self.circle1, fill = 'green')
			mb.showinfo(title = 'Message', message = 'All topics publishing')
			self._tmp_sensors = []
		else:
			mb.showinfo(title = 'Message', message = 'Not all sensor topics publishing, check terminal for details')
			raise Exception(self._tmp_non_pub, ' not published, check sensors')

	
	def checkSensors(self, sensors):
		num_of_sensors = len(sensors)

		out_list = []
		for sensor in sensors:
			out = ''
			# p = subprocess.Popen(['ros2','topic', 'hz', cam], stdout = subprocess.PIPE)
			# time.sleep(5)
			self.p = subprocess.Popen(['timeout', '-s', 'INT', '5','ros2','topic', 'hz', sensor], stdout = subprocess.PIPE)
			proc_flag = False
			while out is '':
				# print('proc_flag', proc_flag)
				if proc_flag == True:
					self.p = subprocess.Popen(['timeout', '-s', 'INT', '5','ros2','topic', 'hz', sensor], stdout = subprocess.PIPE)
					proc_flag = False

				try:
					out = self.p.communicate()[0].decode("utf-8")
				except ValueError:
					mb.showinfo(title = 'Message', message = 'The ros command is not printing yet. Wait for 30 seconds')
					self.p.kill()
					time.sleep(30)
					proc_flag = True

			
			out_first_line = out.split('\n')[0]
			out_list.append(out_first_line)
			mb.showinfo(title = 'Message', message = sensor+ ' publishing with ' + out_first_line)
			print('out_first_line', out_first_line)	
			self.p.kill()
			
		if len(out_list) == num_of_sensors:
			if 'gmsl' in sensors[0]:			
				self.canvas.itemconfig(self.circle2, fill = 'green')
			elif 'Radar' in sensors[0]:
				self.canvas.itemconfig(self.circle3, fill = 'green')
			elif 'Lidar' in sensors[0]:
				self.canvas.itemconfig(self.circle4, fill = 'green')



	def quitButton(self):
		# os.remove('monitor_topic_list.txt')
		self.root.destroy()



if __name__ == "__main__":
	
	gui = makeGUI()
	# l = 2
	# m = 2
	# monitor_sys = Monitor(gui, l, m)

	
