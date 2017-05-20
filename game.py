import pygame, json

def get_image(path):
	return pygame.image.load(path).convert_alpha()

def load_json(path):
	with open(path, 'r') as fd:
		return json.load(fd)

options=load_json("global_options.json")

class GameClient:
	def __init__(self):
		self.owned_entities=[]
		self.remote_entities=[]

	@property
	def entities(self):
		return self.owned_entities+self.remote_entities

	def render(self, screen, dt):
		for e in self.entities:
			e.render(screen, dt)

	def update(self, screen, dt):
		for e in self.entities:
			e.update(screen, dt)

	def add_owned(self, e):
		self.owned_entities.append(e)

	def add_remote(self, e):
		self.remote_entities.append(e)