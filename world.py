import random, pygame

class StarfieldLayer:
	def __init__(self, density, color, size, speed):
		self.density=density
		self.speed=speed
		self.random=random.Random()

		self.particle_surface=pygame.Surface((size, size))
		self.particle_surface.fill(color)

	def bind(self, p):
		self.particles=[]
		self.size=p

	def render(self, surface, p):
		i=0
		self.random.seed(123)
		while i!=self.density:
			#
			pos=(self.random.uniform(0, self.size[0]), self.random.uniform(0, self.size[1]))
			surface.blit(self.particle_surface,
				(
					int((((p[0]+pos[0])/self.speed)%self.size[0])),
					int((((p[1]+pos[1])/self.speed)%self.size[1]))
				)
				)
			i+=1

class StarfieldScroller:
	def __init__(self, size, layers):
		self.layers=layers
		self.pos=[0,0]
		self.bindall(size)
	
	def bindall(self, size):
		for layer in self.layers:
			layer.bind(size)

	def render(self, surface):
		for layer in self.layers:
			layer.render(surface, self.pos)

	def move(self, x, y):
		self.pos[0]+=x
		self.pos[1]+=y

	def move_to(self, x, y):
		self.pos[0]=x
		self.pos[1]=y

class ScrollingWorld:
	def __init__(self, screen):
		self.offset=[0,0]
		self.screen=screen

	def blit(self, image, pos):
		self.screen.blit(image, (pos[0]-self.offset[0], pos[1]-self.offset[1]))

	def draw_rect(self, rect, color, size):
		pygame.draw.rect(self.screen, color, rect.move(*self.offset), size)

	def draw_circle(self, color, pos, radius, width=0):
		pygame.draw.circle(self.screen, color, [pos[0]-self.offset[0], pos[1]-self.offset[1]], radius, width)