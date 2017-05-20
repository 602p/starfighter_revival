import pygame, json, socket, threading, random, os, ai

def get_image(path):
	return pygame.image.load(path).convert_alpha()

def load_json(path):
	with open(path, 'r') as fd:
		return json.load(fd)

options=load_json("assets/global_options.json")

class GameClient:
	def __init__(self, address):
		self.cid=random.randint(0,99999)
		self.recv_buf_size=8192
		self.owned_entities={}
		self.remote_entities={}
		self.sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.saddr=address
		self.handle_thread=threading.Thread(target=self.handle_loop, name="Client_handle")
		self.handle_thread.daemon=True
		self.handle_thread.start()
		self.sendj({"msg":"hello"})

	def sendj(self, data):
		self.sock.sendto(json.dumps(data).encode("utf-8"), self.saddr)

	def render(self, screen, dt):
		for e in list(self.owned_entities.values()):
			e.render(screen, dt)
		for e in list(self.remote_entities.values()):
			e.render(screen, dt)

	def update(self, screen, dt):
		for e in list(self.owned_entities.values()):
			e.update(screen, dt)
		for e in list(self.remote_entities.values()):
			e.update(screen, dt)

	def add_owned(self, e):
		self.owned_entities[e.eid]=e

	def add_remote(self, e):
		self.remote_entities[e.eid]=e

	def handle_loop(self):
		while True:
			try:
				data, addr = self.sock.recvfrom(self.recv_buf_size)
				msg=json.loads(data.decode("utf-8"))
				# print("Message recieved: "+str(msg))
				self.handlej(msg)
			except socket.error as e:
				print(e)

	def handlej(self, data):
		if data["msg"]=="entity":
			if data["eid"] not in self.remote_entities:
				self.remote_entities[data["eid"]]=ship.Ship(ship_types[data["type"]], ai.ais[data["ai"]]())
			self.remote_entities[data["eid"]].load_data(data)

	def send_updates(self):
		for e in self.owned_entities.values():
			if e.should_send_update():
				data=e.save_data()
				data["owner"]=self.cid
				data["msg"]="entity"
				self.sendj(data)

import ship

ship_types={}
def load_ship_types():
	for filename in os.listdir("assets"):
		if filename.endswith(".ship"):
			shty=ship.ShipType(load_json("assets/"+filename))
			ship_types[shty.name]=shty