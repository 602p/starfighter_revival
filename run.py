import pygame
import ship
import game
import world
import sys
import ai
import ui
import item
worldsize=(1000,600)

pygame.init()
screen = pygame.display.set_mode(worldsize)
game.load_ship_types()
game.load_item_types()

team2=len(sys.argv)>1

player = ship.Ship(game.ship_types["med_fighter"], ai.AI(), 1 if team2 else 0)
player.target=None
print(player.type.slots)
player.set_equipment("left_wing", item.Item(game.item_types["laser"]))
player.set_equipment("right_wing", item.Item(game.item_types["laser"]))
player.selected_weapon="left_wing"

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

client=game.GameClient(('10.0.0.100', 1245))
client.add_owned(player)
game.client=client

radar=ui.Radar(player, screen)

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
			if e.key==pygame.K_p:
				player.target=ship.Ship(game.ship_types["med_fighter"], ai.HostileAI(), faction=1)
				player.target.set_equipment("left_wing", item.Item(game.item_types["homing_missile"]))
				player.target.selected_weapon="left_wing"
				player.target.target=player
				client.add_owned(player.target)

	if keys[pygame.K_q]:
		run=False

	if keys[pygame.K_SPACE]:
		player.fire_selected()

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

	radar.render(dt)

	bg.move_to(*player.position)
	pygame.display.flip()
	client.send_updates()
	if player.marked_for_death:
		print("\n"*100)
		print("YOU ARE DEAD")
		run=False