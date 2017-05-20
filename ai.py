
ais={}

def register_ai(name):
	def _internal(cls):
		ais[name]=cls
		cls.name=name
		return cls
	return _internal

@register_ai("empty")
class AI(object):
	def update(self, dt):
		pass

@register_ai("go_forwards")
class GoForwardsAI(AI):
	def update(self, dt):
		self.ship.accel_direction=1
		self.ship.turn_direction=0