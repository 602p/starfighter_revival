import game, pygame, ship, ai

class ItemType:
	def __init__(self, data):
		for name in ["name", "fire_action"]:
			setattr(self, name, data[name])
		self.raw=data
		self.cooldown=data.get("cooldown", 1000)
		self.image=game.get_image(data["image"])

class Item:
	def __init__(self, type):
		self.type=type
		self.last_fired=pygame.time.get_ticks()

	def fire(self):
		if pygame.time.get_ticks()-self.last_fired>self.type.cooldown:
			self.last_fired=pygame.time.get_ticks()
			print(self.type.fire_action)
			if self.type.fire_action=="spawn_projectile":
				proj=ship.Ship(game.ship_types[self.type.raw["proj_type"]], ai.ProjectileAI(), faction=self.ship.faction)
				proj.position=list(self.ship.rect.center)
				proj.angle=self.ship.angle
				proj.target=self.ship.target
				proj.make_rotated_image()
				game.client.add_owned(proj)

	def save_data(self):
		return {
			"type":self.type.name
		}

	def load_data(self, data):
		pass