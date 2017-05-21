import pygame, math

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

def get_angle(x1, x2, y1, y2):
	delta_angle=math.degrees(math.atan2(y2-y1, -(x2-x1)))+90
	return delta_angle

def get_rel_angle(delta_angle, self_angle):
	return math.degrees(math.atan2(
			math.sin(math.radians(delta_angle)-math.radians(self_angle)),
			math.cos(math.radians(delta_angle)-math.radians(self_angle))
		))

@register_ai("projectile_ai")
class ProjectileAI(AI):
	def __init__(self):
		self.create_time=pygame.time.get_ticks()
	def update(self, dt):
		self.ship.accel_direction=1
		self.ship.turn_direction=0
		if pygame.time.get_ticks()-self.create_time>self.ship.type.raw.get("lifetime", 5000):
			self.ship.marked_for_death=True

		for ship in game.client.owned_entities.values():
			if ship.faction!=self.ship.faction and ship is not self.ship:
				# print(ship.rect, self.ship.rect)
				if ship.rect.colliderect(self.ship.rect) and not ship.type.raw.get("is_projectile"):
					self.ship.marked_for_death=True
					ship.take_damage(self.ship.type.raw.get("damage", 10))

		if self.ship.target:
			if self.ship.type.max_rot_speed>0 and not self.ship.target.marked_for_death:
				angle=get_rel_angle(get_angle(self.ship.rect.centerx, self.ship.target.rect.centerx,
					self.ship.rect.centery, self.ship.target.rect.centery), self.ship.angle)
				if abs(angle)>10:
					if angle>0:
						self.ship.turn_direction=1
					else:
						self.ship.turn_direction=-1

@register_ai("hostile_ai")
class HostileAI(AI):
	def update(self, dt):
		if self.ship.target:
			if self.ship.type.max_rot_speed>0 and not self.ship.target.marked_for_death:
				angle=get_rel_angle(get_angle(self.ship.rect.centerx, self.ship.target.rect.centerx,
					self.ship.rect.centery, self.ship.target.rect.centery), self.ship.angle)
				if abs(angle)>20:
					self.ship.accel_direction=0
					if angle>0:
						self.ship.turn_direction=1
					else:
						self.ship.turn_direction=-1
				else:
					self.ship.accel_direction=1
					self.ship.fire_selected()

import game