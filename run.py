import pygame
import ship
import game
import world
import sys
import ai
worldsize=(600,400)

pygame.init()
screen = pygame.display.set_mode(worldsize)
game.load_ship_types()

player = ship.Ship(game.ship_types[sys.argv[1] if len(sys.argv)>1 else "test"], ai.AI())

bg=world.StarfieldScroller(
	worldsize,
	[
		world.StarfieldLayer(20, (255,150,150), 2, -1.25),
		world.StarfieldLayer(30, (150,255,150), 2, -1.5),
		world.StarfieldLayer(40, (200,200,200), 3, -1),
		world.StarfieldLayer(40, (100,100,100), 2, -0.6)
	]
)

world=world.ScrollingWorld(screen)

client=game.GameClient(('localhost', 1245))
client.add_owned(player)

clock=pygame.time.Clock()
run=True
while run:
	fps=clock.tick(60)
	dt=(1/fps) if fps!=0 else 999
	keys=pygame.key.get_pressed()

	for e in pygame.event.get():
		if e.type==pygame.QUIT:
			run=False
		elif e.type==pygame.KEYDOWN:
			if e.key==pygame.K_SPACE:
				laser=ship.Ship(game.ship_types["laser_projectile"], ai.GoForwardsAI())
				laser.position=list(player.rect.center)
				laser.angle=player.angle
				client.add_owned(laser)
	
	if keys[pygame.K_q]:
		run=False

	player.reset_controls()
	if keys[pygame.K_a]:
		player.turn_left()
	elif keys[pygame.K_d]:
		player.turn_right()
	
	if keys[pygame.K_w]:
		player.accelerate()
	elif keys[pygame.K_s]:
		player.decelerate()

	client.update(world, dt)
	
	world.offset=[player.rect.centerx-(worldsize[0]/2), player.rect.centery-(worldsize[1]/2)]

	screen.fill((0,0,0))
	bg.render(screen)
	
	client.render(world, dt)

	bg.move_to(*player.position)
	pygame.display.flip()
	client.send_updates()