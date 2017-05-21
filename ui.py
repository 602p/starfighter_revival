import pygame, game, ship, math

class Radar:
	def __init__(self, player, screen):
		self.ring_count=10
		self.extra_time=7
		self.ring_spacing=10
		self.ring_timing=50
		self.full_scale=5000
		self.curr_ring=0
		self.curr_ring_time=pygame.time.get_ticks()
		self.sz=(self.ring_count+1)*self.ring_spacing*2
		self.rect=pygame.Rect(screen.get_width()-self.sz, 0, self.sz, self.sz)
		self.fill_surf=pygame.Surface(self.rect.size).convert_alpha()
		self.fill_surf.fill((150,150,150,80))
		self.screen=screen
		self.player=player
		self.scale_factor=self.sz/self.full_scale

		self.green_arrow = game.get_image("assets/radar/green_arrow.png").convert_alpha()
		self.red_arrow = game.get_image("assets/radar/red_arrow.png").convert_alpha()
		self.grey_arrow = game.get_image("assets/radar/grey_arrow.png").convert_alpha()
		self.target_icon = game.get_image("assets/radar/target.png").convert_alpha()

	def render(self, dt):
		if pygame.time.get_ticks()-self.curr_ring_time>self.ring_timing:
			self.curr_ring+=1
			self.curr_ring_time=pygame.time.get_ticks()

		if self.curr_ring>self.ring_count+self.extra_time:
			self.curr_ring=0

		pygame.draw.rect(self.screen, (200,200,200,100), self.rect, 4)
		self.screen.blit(self.fill_surf, self.rect)

		for i in range(self.ring_count):
			pygame.draw.circle(self.screen, 
				(255,255,255) if i==self.curr_ring else (150,150,150), self.rect.center, (i+1)*self.ring_spacing, 1)

		for e in list(game.client.owned_entities.values()):
			self.draw_ship(e)
		for e in list(game.client.remote_entities.values()):
			self.draw_ship(e)

	def draw_ship(self, e):
		if e.faction==self.player.faction and e.type.raw.get("render_only_for_enemy"):
			return
		icon=(self.grey_arrow if e is self.player else self.green_arrow) if e.faction==self.player.faction else self.red_arrow
		self.screen.blit(icon, (0,0))
		image, rect = ship.rot_center(icon, icon.get_rect(), e.angle)
		rect=rect.move(((e.rect.centerx-self.player.rect.centerx)*self.scale_factor,
						(e.rect.centery-self.player.rect.centery)*self.scale_factor))
		if math.sqrt((rect.centerx**2)+(rect.centery**2))>(self.sz/2)-10:
			return
		rect=rect.move(self.rect.center).move((-icon.get_width()/2, -icon.get_height()/2))

		overlay_pos=(((e.rect.centerx-self.player.rect.centerx)*self.scale_factor)+self.rect.centerx-(e.type.map_icon.get_width()/2),
			((e.rect.centery-self.player.rect.centery)*self.scale_factor)+self.rect.centery-(e.type.map_icon.get_height()/2))
		self.screen.blit(e.type.map_icon, (overlay_pos[0], overlay_pos[1]-5))

		if e.type.do_normal_map_icon:
			self.screen.blit(image, rect)
			if rect.collidepoint(pygame.mouse.get_pos()):
				if pygame.mouse.get_pressed()[0]:
					if e.faction!=self.player.faction:
						self.player.target=e
			# pygame.draw.rect(self.screen, (255,0,0), rect, 2)
		if e is self.player.target:
			self.screen.blit(self.target_icon, overlay_pos)