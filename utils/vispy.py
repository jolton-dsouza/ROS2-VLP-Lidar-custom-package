import numpy as np
import vispy.scene
from vispy.scene import visuals
from vispy import app
import glob
import time
from multiprocessing import Queue, Process

class VispyViz():
	def __init__(self):
		self.q = Queue()

		self.l = list()

		self.p = Process(target = self.start_vis, args = ())
		self.p.start()
		self.p.join()


	def update_here(self, event):
		if self.q.empty():
			pass
		else:
			_content = self.q.get()
			_X = _content['X']
			_Y = _content['Y']
			_Z = _content['Z']

			_pcld = np.float64(np.asmatrix(np.column_stack(( _X,_Y,_Z))))
			
			norm = plt.Normalize()
			colors = plt.cm.jet(norm(ref))
			_colors = colors[:,:-1]
			
			_colr = np.float64(np.asmatrix(_colors))

			self.scatter = self.l[0]['scatter']

			# _content = self.q.get()

			# _pcld = _content['pcld']
			
			# _colr = _content['colr']

			self.scatter.set_data(_pcld, edge_color=(0.5, 0.1, 0, .5), face_color=_colr, size=5)

			print("TIME TAKEN, ", time.time() - self.l[0]['time'])

			self.l[0]['time'] = time.time()



	def start_vis(self):

		self.canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)

		self.view = canvas.central_widget.add_view()

		self.scatter = visuals.Markers()

		self.view.camera = 'arcball'
		self.axis = visuals.XYZAxis(parent= self.view.scene)
		self.view.add(self.scatter)

		self.l.append({'scatter':self.scatter, 'time':time.time()})
		self.timer = app.Timer('auto', connect= self.update_here, start=0.05)

		import sys
		if sys.flags.interactive != 1:
			self.vispy.app.run()

	def vispy_que_parse(self, que):
		self.q = que


	
# def update_que():
# 	pclds = glob.glob('/media/jolton/LaCie/data_jolton/*.npz')
# 	for pcld in pclds:
		
# 		pcld = np.load(pcld)

# 		pcld = pcld['Pts_mtx']

# 		colr = np.random.uniform(low=0, high=1, size=(524288,3))

# 		q.put({'pcld':pcld, 'colr': colr})

	
	# while True:

	# 	pcld = np.random.normal(size=(524288, 3), scale=0.2) 

	# 	colr = np.random.uniform(low=0, high=1, size=(524288,3))

	# 	q.put({'pcld':pcld, 'colr': colr})


if __name__ == "__main__":


	q = Queue()
	l = list()

	p1 = Process(target = start_vis, args = ())
	p2 = Process(target = update_que, args = ())

	p1.start()
	p2.start()

	p1.join()
	p2.join()
