import pygame, math, game, entity

def rot_center(image, rect, angle):
	"""rotate an image while keeping its center"""
	rot_image = pygame.transform.rotate(image, angle)
	rot_rect = rot_image.get_rect(center=rect.center)
	return rot_image,rot_rect

def clamp(i, hi, lo):
	return max(min(i, hi), lo)

class ShipType(object):
	def __init__(self, data):
		for key in ["name", "max_rot_speed", "rot_accel", "max_speed", "accel"]:
			setattr(self, key, data[key])
		self.image=game.get_image(data["image"])
		self.image=pygame.transform.scale(self.image, [int(i*data.get("image_scale", 1)) for i in self.image.get_size()])
		self.trail = data.get("trails", True)

class Floof():
	def __init__(self, pos, ct):
		self.position = pos
		self.creation_time = ct
		self.image = pygame.image.load("floof.png").convert()
		self.image.set_colorkey([255,255,255])

class Ship(entity.Entity):
	def __init__(self, ship_type, ai):
		entity.Entity.__init__(self)
		self.base_image=ship_type.image.copy()
		self.last_angle=None
		self.image=None
		self.rect=None
		self.type=ship_type
		self.turn_direction=0
		self.accel_direction=0
		self.ai=ai
		self.ai.ship=self

		self.angle=0
		self.position=[200,200]
		self.rotation_speed=0
		self.speed=0

		self.floofs = []

		self.make_rotated_image()

	def make_rotated_image(self):
		if self.angle != self.last_angle:
			self.image,self.rect = rot_center(self.base_image, pygame.Rect(self.position, self.base_image.get_size()), self.angle)

	def turn_left(self):
		self.turn_direction=1

	def turn_right(self):
		self.turn_direction=-1

	def accelerate(self):
		self.accel_direction=1

	def decelerate(self):
		self.accel_direction=-1

	def update(self, screen, dt):

		for floof in self.floofs:
			u = (pygame.time.get_ticks()-floof.creation_time) > 1000
			if u:
				self.floofs.remove(floof)
		self.ai.update(dt)

		if self.turn_direction:
			self.rotation_speed+=self.turn_direction*self.type.rot_accel*dt
		else:
			if abs(self.rotation_speed)>=game.options["turn_drag_rate"]*dt:
				self.rotation_speed-=(1 if self.rotation_speed>0 else -1)*game.options["turn_drag_rate"]*dt
			else:
				self.rotation_speed=0

		self.rotation_speed=clamp(self.rotation_speed, self.type.max_rot_speed, -self.type.max_rot_speed)
		self.speed=clamp(self.speed, self.type.max_speed, -self.type.max_speed*.5)
		self.angle+=self.rotation_speed*dt
		if self.angle<=-360:
			self.angle+=360
		if self.angle>=360:
			self.angle-=360
		self.make_rotated_image()
		self.position[0]+=-self.speed*math.sin(math.radians(self.angle))*dt
		self.position[1]+=-self.speed*math.cos(math.radians(self.angle))*dt

		if self.accel_direction:
			if self.type.trail:
				self.floofs.append(Floof(list(self.rect.center),pygame.time.get_ticks()))
			self.speed+=self.accel_direction*dt*(0.5 if (self.accel_direction==-1 and self.speed>0) else 1)*self.type.accel
		else:
			if abs(self.speed)>=game.options["drag_rate"]*dt:
				self.speed-=(1 if self.speed>0 else -1)*game.options["drag_rate"]*dt
			else:
				self.speed=0

	def reset_controls(self):
		self.turn_direction=0
		self.accel_direction=0

	def render(self, screen, dt):
		for floof in self.floofs:
			screen.blit(floof.image, floof.position)
		screen.blit(self.image, self.rect)

	def save_data(self):
		return {
			"angle":self.angle,
			"speed":self.speed,
			"position":self.position,
			"rotation_speed":self.rotation_speed,
			"eid":self.eid,
			"type":self.type.name,
			"acc_dir":self.accel_direction,
			"tur_dir":self.turn_direction,
			"ai":type(self.ai).name
		}

	def load_data(self, data):
		self.angle=data["angle"]
		self.speed=data["speed"]
		self.position=data["position"]
		self.rotation_speed=data["rotation_speed"]
		self.eid=data["eid"]
		self.accel_direction=data["acc_dir"]
		self.tur_dir=data["tur_dir"]
