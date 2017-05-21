import pygame, json, socket, threading, random, os, ai, item

client=None

def get_image(path):
	if path is None: return pygame.Surface((0,0))
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
		self.sendj({"msg":"hello", "cid":self.cid})
		self.other_clients=[]
		self.reliable_message_buffer={}

	def sendj(self, data):
		self.sock.sendto(json.dumps(data).encode("utf-8"), self.saddr)

	def sendj_reliable(self, data):
		data["reliable"]=True
		data["mid"]=random.randint(0,999999)
		print("Sending reliable message:"+str(data))
		self.reliable_message_buffer[data["mid"]]=[data, {cid:False for cid in self.other_clients}]

	def render(self, screen, dt):
		for e in list(self.owned_entities.values()):
			e.render(screen, dt)
		for e in list(self.remote_entities.values()):
			e.render(screen, dt)

	def update(self, screen, dt):
		for e in list(self.owned_entities.values()):
			e.update(screen, dt)
			if e.marked_for_death:
				self.sendj_reliable({"msg":"del_entity", "eid":e.eid})
				del self.owned_entities[e.eid]
		for e in list(self.remote_entities.values()):
			e.update(screen, dt)
			if e.marked_for_death:
				self.sendj_reliable({"msg":"del_entity", "eid":e.eid})
				del self.remote_entities[e.eid]

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
		if "cid" in data:
			if data["cid"] not in self.other_clients:
				print("New peer:"+str(data["cid"]))
				self.other_clients.append(data["cid"])
		if data["msg"]=="entity":
			if data["eid"] not in self.remote_entities:
				new=ship.Ship(ship_types[data["type"]], ai.ais[data["ai"]]())
				new.load_data(data)
				self.remote_entities[data["eid"]]=new
			else:
				self.remote_entities[data["eid"]].load_data(data)
		elif data["msg"]=="reliable_ack":
			try:
				print("Client "+str(self.cid)+" got ack of reliable message "+str(data["mid"])+" by client "+str(data["cid"]))
				self.reliable_message_buffer[data["mid"]][1][data["cid"]]=True
				if all(self.reliable_message_buffer[data["mid"]][1]):
					print("reliable message "+str(data["mid"])+" fully delivered")
					del self.reliable_message_buffer[data["mid"]]
			except KeyError as e:
				print("Error is ack:"+str(e))
		elif data["msg"]=="del_entity":
			if data["eid"] in self.owned_entities:
				del self.owned_entities[data["eid"]]
			elif data["eid"] in self.remote_entities:
				del self.remote_entities[data["eid"]]

		if data.get("reliable", False):
			print("Client "+str(self.cid)+" acknowledging reliable message "+str(data["mid"]))
			self.sendj({"msg":"reliable_ack", "mid":data["mid"], "cid":self.cid})

	def send_updates(self):
		for e in self.owned_entities.values():
			if e.should_send_update():
				data=e.save_data()
				data["cid"]=self.cid
				data["msg"]="entity"
				self.sendj(data)
		for e in list(self.reliable_message_buffer.values()):
			self.sendj(e[0])

	def get_ship(self, eid):
		return self.owned_entities[eid] if eid in self.owned_entities else self.remote_entities[eid]

	def owns_ship(self, ship):
		return ship in self.owned_entities.values()

import ship, item

ship_types={}
def load_ship_types():
	for filename in os.listdir("assets/ships"):
		if filename.endswith(".ship"):
			shty=ship.ShipType(load_json("assets/ships/"+filename))
			ship_types[shty.name]=shty

item_types={}
def load_item_types():
	for filename in os.listdir("assets/items"):
		if filename.endswith(".item"):
			shty=item.ItemType(load_json("assets/items/"+filename))
			item_types[shty.name]=shty

def make_enemy(data):
	e=ship.Ship(ship_types[data["ship"]], ai.ais[data["ai"]](), faction=1)
	for k,v in data["equipment"].items():
		e.set_equipment(k, item.Item(item_types[v]))
		e.selected_weapon=k
	return e