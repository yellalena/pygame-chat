import sys
from time import sleep, localtime
from weakref import WeakKeyDictionary

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel

class ClientChannel(Channel):
	def __init__(self, *args, **kwargs):
		# This happens whenever a new client is connected
		self.userid = 0
		Channel.__init__(self, *args, **kwargs)
	
	def Close(self):
		self._server.DelPlayer(self)
	
	##################################
	### Network specific callbacks ###
	##################################
	
	def Network_message(self, data):
		self._server.SendToAll({"action": "message", "history": data['history'], "who": self.userid})
	
	def Network_userid(self, data):
		self.userid = data['userid']
		self._server.SendPlayers()

class ChatServer(Server):
	channelClass = ClientChannel
	
	def __init__(self, *args, **kwargs):
		Server.__init__(self, *args, **kwargs)
		self.players = WeakKeyDictionary()
		print('Server launched')
	
	def Connected(self, channel, addr):
		self.AddPlayer(channel)
	
	def AddPlayer(self, player):
		print("New Player" + str(player.addr))
		self.players[player] = True
		self.SendPlayers()
		print("players", [p for p in self.players])
	
	def DelPlayer(self, player):
		print("Deleting Player" + str(player.addr))
		del self.players[player]
		self.SendPlayers()
	
	def SendPlayers(self):
		self.SendToAll({"action": "players", "players": [p.userid for p in self.players]})
	
	def SendToAll(self, data):
		[p.Send(data) for p in self.players]
		
	def Launch(self):
		while True:
			self.Pump()
			sleep(0.0001)

# get command line argument of server, port
if len(sys.argv) != 2:
	print("Usage:", sys.argv[0], "host:port")
	print("e.g.", sys.argv[0], "localhost:31425")
else:
	host, port = sys.argv[1].split(":")
	s = ChatServer(localaddr=(host, int(port)))
	s.Launch()