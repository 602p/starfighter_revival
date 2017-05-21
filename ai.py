import pygame

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

@register_ai("projectile_ai")
class GoForwardsAI(AI):
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
				if ship.rect.colliderect(self.ship.rect):
					self.ship.marked_for_death=True
					ship.take_damage(self.ship.type.raw.get("damage", 10))

import game