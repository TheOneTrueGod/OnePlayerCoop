import sys, Globals, pygame, random, math, os, subprocess, Abilities
from twisted.spread import pb
from twisted.internet import reactor
from twisted.python import util
from pygame.locals import *

from Globals import *
from Effects import EffectStruct
from Units import UnitStruct
from Terrain import Terrain
from Projectiles import ProjectileStruct
frame = 0
for i in range(len(sys.argv)):
	if sys.argv[i] == "-d":
		DEBUGMODE = 1
		
pMax = -1

Globals.units = []
Globals.effects = []
class Player:
	def __init__(self, pNum):
		self.keys = Keys()
		self.lastActive = {}
		t = [[1] * 40] + [[1] + [0] * 38 + [1]] * 28 + [[1] * 40]
		self.terrainChanges = Globals.terrain.convertToString()
		self.inStore = False
		self.pNum = pNum
		self.abilsSelected = [Abilities.ProjectileAbility()] + [None] * (Globals.NUMABILS - 1)
		self.abilInstances = {}
		for k in Abilities.abilDict:
			self.abilInstances[k] = Abilities.abilDict[k]()
		self.gold = STARTGOLD
		self.stats = {"defense":1000, 
								 "attack" :1000,
								 "knockbackAttack":1000,
								 "knockbackDefense":1000}
		self.createUnit()
		
	def createUnit(self):
		self.stats["attack"]  = 1000 + self.abilInstances["attack"].getStatAmount()
		self.stats["defense"] = 1000 + self.abilInstances["defense"].getStatAmount()
		
		self.stats["knockbackAttack"] = 1000 + self.abilInstances["attack"].getStatAmount()
		self.stats["knockbackDefense"] = 1000 + self.abilInstances["defense"].getStatAmount()
		
		newUnit = Globals.units.addPlayerUnit([300, 300], self.pNum)
		newUnit.setStats(self.stats)
		newUnit.setAbils([a for a in self.abilsSelected])
		for k in Abilities.attackTypes:
			newUnit.setAttackBonuses({k:self.abilInstances[k].getAttackAmount()})
		
	def setAbilSelected(self, abilNum, abilIndex):
		if isInt(abilIndex) and self.abilInstances[abilIndex].level > 0:
			self.abilsSelected[abilNum] = self.abilInstances[abilIndex]
			return True
		return False
		
	def buyAbil(self, abilIndex):
		if self.gold > self.abilInstances[abilIndex].getCost():
			self.gold -= self.abilInstances[abilIndex].getCost()
			self.abilInstances[abilIndex].level += 1
			return True
		return False
		
	def getStoreStats(self):
		toRet = [int(self.gold)]
		abils = []
		for abil in self.abilsSelected:
			if abil == None:
				abils += [None]
			else:
				abils += [abil.icon]
		toRet += [abils]
		return toRet
		
	def getKeys(self):
		return self.keys.getKeys()
		
	def enterStore(self):
		self.inStore = True
		
	def exitStore(self):
		self.inStore = False
		self.createUnit()
		
	def getLastActivity(self, type):
		if type in self.lastActive:
			return self.lastActive[type]
		return 0
	
	def setLastActivity(self, type, frame):
		self.lastActive[type] = frame
		
	def keyPressed(self, key):
		return self.keys.keyPressed(key)
		
	def buttonsDown(self):
		return self.keys.getMouseButtons()
		
	def getMousePos(self):
		p = self.keys.getMousePos()
		return p
		
	def handleEvent(self, ev):
		self.keys.handleEvent(ev)
		
	def addTerrainChange(self, terrainChange):
		self.terrainChanges += " " + terrainChange
		
	def getTerrainChanges(self):
		toRet = self.terrainChanges
		self.terrainChanges = ""
		return toRet
		
class Players:
	def __init__(self):
		self.players = {}
		self.playerDropped = False
	
	def addPlayer(self):
		if len(self.players) not in self.players:
			self.players[len(self.players)] = Player(len(self.players))
			return len(self.players) - 1
		else:
			return -1
			
	def distributeBounty(self, amount):
		for p in self.players:
			self.players[p].gold += amount
			
	def resetRequested(self):
		for p in self.players:
			if self.players[p].keyPressed(K_r):
				return True
		return False
		
	def getNumPlayers(self):
		return len(self.players)
		
	def dropPlayer(self, num):
		print "Deleting player:", num
		if num in self.players:
			del self.players[num]
			self.playerDropped = True
			
	def everDroppedPlayer(self):
		return self.playerDropped
		
	def addTerrainChange(self, terrainChange):
		for num in self.players:
			self.players[num].addTerrainChange(terrainChange)
		
	def getPlayer(self, num):
		if num in self.players:
			return self.players[num]
		else:
			return None
		
	def handleEvent(self, id, ev):
		if id in self.players:
			self.players[id].handleEvent(ev)
		elif DEBUGMODE:
			print "***************"
			print "ERROR IN HANDLEEVENT:", id, "not a valid player."
			print self.players
			print "***************"

class Keys:
	def __init__(self):
		self.pressed = {}
		self.mousePos = [0, 0]
		self.mouseButtons = []

	def getMousePos(self):
		return self.mousePos
		
	def getMouseButtons(self):
		return self.mouseButtons
		
	def keyPressed(self, key):
		return key in self.pressed
		
	def getKeys(self):
		return self.pressed
	
	def handleEvent(self, ev):
		if ev['type'] == KEYDOWN:
			self.pressed[ev['key']] = True
		elif ev['type'] == KEYUP:
			if ev['key'] in self.pressed:
				del self.pressed[ev['key']]
		elif ev['type'] == MOUSEMOTION:
			self.mousePos = ev['pos']
		elif ev['type'] == MOUSEBUTTONDOWN:
			self.mousePos = ev['pos']
			self.mouseButtons += [ev['button']]
		elif ev['type'] == MOUSEBUTTONUP:
			self.mousePos = ev['pos']
			if ev['button'] in self.mouseButtons:
				self.mouseButtons.remove(ev['button'])

class RootOb(pb.Root):
	def remote_createNewPlayer(self):
		return Globals.players.addPlayer()
	
	def remote_updateEvents(self, playerID, ev):
		Globals.players.handleEvent(playerID, ev)
		
	def remote_dropPlayer(self, playerNum):
		global _done
		print "Player Dropped..."
		Globals.players.dropPlayer(playerNum)
		_done = True
		
	def remote_getStoreStats(self, pID):
		return Globals.players.getPlayer(pID).getStoreStats()
		
	def remote_setSkill(self, pID, abilNum, abilIndex):
		if Globals.players.getPlayer(pID).setAbilSelected(abilNum, abilIndex):
			return [abilNum, abilIndex]
		return None
		
	def remote_buySkill(self, pID, abilIndex):
		if Globals.players.getPlayer(pID).buyAbil(abilIndex):
			return abilIndex
		return None
		
	def remote_getCharDrawList(self, pID):
		global frame
		player = Globals.players.getPlayer(pID)
		if player:
			if player.inStore:
				return "EnterStore"
			if player.getLastActivity("chars") != frame:
				player.setLastActivity("chars", frame)
			return Globals.units.getDrawList(player)
		return ""
		
	def remote_exitStore(self, pID):
		player = Globals.players.getPlayer(pID)
		if player:
			player.exitStore()
		
	def remote_getTerrainDrawList(self, pID):
		global frame
		player = Globals.players.getPlayer(pID)
		if player and player.getLastActivity("terrain") != frame:
			player.setLastActivity("terrain", frame)
			return player.getTerrainChanges()
		return ""
		
	def remote_getEffectDrawList(self, pID):
		global frame
		player = Globals.players.getPlayer(pID)
		if player and player.getLastActivity("effects") != frame:
			player.setLastActivity("effects", frame)
			return Globals.effects.getDrawList(player)
		return ""
		
Globals.players = Players()
Globals.effects = EffectStruct()
Globals.units = UnitStruct()
Globals.terrain = Terrain()
Globals.projectiles = ProjectileStruct()

started = True
_done = False
nextReset = 0
spawnDelta = 100

def mainLoop():
	global _done, handicap, frame, nextReset, nextSpawn
	frame = (frame + 1) % 5000
	
	if started:
		Globals.units.update()
		Globals.effects.update()
		Globals.projectiles.update()
		nextReset -= nextReset > 0
		if Globals.players.resetRequested() and nextReset <= 0:
			Globals.terrain.reset()
			nextReset = spawnDelta
			spawnDelta = max(spawnDelta - 5, 20)

	if False:#units.getWinner():
		print "WINNER!:", Globals.units.getWinner()
		reactor.stop()
		_done = True
	if Globals.players.everDroppedPlayer():
		_done = True
		reactor.stop()
		if Globals.CLIENTPROCESS and Globals.CLIENTPROCESS.returncode != None:
			Globals.CLIENTPROCESS.poll()
			if Globals.CLIENTPROCESS.returncode == None:
				Globals.CLIENTPROCESS.kill()
				
	if not _done:
		reactor.callLater(0.03, mainLoop)
	
def startClient():
	path = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'Client.py')
	p = subprocess.Popen([sys.executable, path], 
																		#stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                                    stdout=sys.stdout, stdin=sys.stdin,stderr=sys.stderr)
	Globals.CLIENTPROCESS = p

if __name__ == '__main__':
	reactor.listenTCP(8789, pb.PBServerFactory(RootOb()))
	reactor.callLater(0, mainLoop)
	print "Server Created."
	startClient()
	reactor.run()