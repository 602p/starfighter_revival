import time, pygame, random

class Entity:
	def __init__(self):
		self.eid=random.randint(0,999999999)
		self.update_freq=100
		self.last_update=pygame.time.get_ticks()

	def should_send_update(self):
		u=(pygame.time.get_ticks()-self.last_update)>self.update_freq
		if u:
			self.last_update=pygame.time.get_ticks()
		return u