import socket, json

class GameServer:
	def __init__(self, server_address=('',1245)):
		self.clients=[]
		self.recv_buf_size=8192
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind(server_address)

	def handlej(self, data, address):
		self.clients[address].handlej(data)

	def handle_loop(self):
		while True:
			try:
				data, addr = self.sock.recvfrom(self.recv_buf_size)
				# print("Message recieved: "+data.decode("utf-8"))
				if addr not in self.clients:
					print("Client Connected: "+str(addr))
					self.clients.append(addr)

				for client in self.clients:
					if client != addr:
						self.sock.sendto(data, client)
			except socket.error as e:
				print(e)

GameServer().handle_loop()