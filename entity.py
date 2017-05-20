import time

class Entity:
	def __init__(self):
		self.eid=int(time.time()*1000)&(2**32)