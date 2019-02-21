import pygame, sys, Effects, random
from Globals import *
PTRS["TRAPTYPES"] = enum('POWEREDDOOR', 'SECRETDOOR', 'WALLSPIKETRAP', 'FLOORSPIKETRAP', 'REPEATER', 'DEFAULT')
NumTrapTypes = 6 - 1
lockPics = pygame.image.load(os.path.join("Data", "Pics", "Icons", "DoorLocks.png"))
lockPics.set_colorkey([255, 0, 255])
class Trap:
	TrapId = PTRS["TRAPTYPES"].DEFAULT
	def __init__(self, source, args=[]):
		self.source = source
		self.activated = 0
		self.backupActivated = 0
		self.parseArgs(args)
		
	def parseArgs(self, args):
		pass
		
	@staticmethod
	def previewTrap(self):
		return None
		
	def getPathingHeuristic(self, unit):
		return 0
		
	def addNumberParameter(self, number):
		pass
		
	def addAngleParameter(self, angle):
		pass
		
	def triggersTraps(self):
		return False
	
	def backup(self):
		self.backupActivated = self.activated
		
	def restore(self):
		self.activated = self.backupActivated
				
	def canMoveThrough(self, unit):
		return False
		
	def canSeeThrough(self):
		return False

	def activate(self, unit):
		self.activated += 1
		
	def deactivate(self, unit):
		self.activated = max(self.activated - 1, 0)
		
	def save(self, fileOut):
		fileOut.write("TRAP " + str(int(self.source[0])) + " " + str(int(self.source[1])) + " " + str(self.TrapId) + " ")
		self.saveParameters(fileOut)
		fileOut.write(" " + "\n")
		
	def saveParameters(self, fileOut):
		pass
		
	def update(self):
		pass
		
	def drawMe(self, camera):
		if self.activated:
			pygame.draw.rect(camera.getSurface(), [255, 255, 0], [[self.source[0] * TILESIZE[0] - camera.Left(), 
																														 self.source[1] * TILESIZE[1] - camera.Top()], TILESIZE])
		else:
			pygame.draw.rect(camera.getSurface(), [255, 0, 255], [[self.source[0] * TILESIZE[0] - camera.Left(), 
																														 self.source[1] * TILESIZE[1] - camera.Top()], TILESIZE])
			
class PoweredDoor(Trap):
	TrapId = PTRS["TRAPTYPES"].POWEREDDOOR
	def parseArgs(self, args):
		self.unitHasKey = 0
		self.backupUnitHasKey = 0
		self.key = 0
		on = 0
		try:
			while on < len(args):
				if args[on] == "-k":
					self.key = int(args[on+1])
					on += 1
				on += 1
		except:
			print "Powered Door Error:", sys.exc_info()[0]
			
	def getPathingHeuristic(self, unit):
		if unit.getItemHeld() == self.key or unit.getItemHeld() == -1:
			return 0
		if self.activated:
			return 0
		else:
			return 10000
			
	def update(self):
		self.unitHasKey -= self.unitHasKey > 0
		
	def saveParameters(self, fileOut):
		fileOut.write("-k " + str(self.key))
		
	def drawMe(self, camera):
		variation = 0
		if (not PTRS["TERRAIN"].canMoveThrough((self.source[0], self.source[1] + 1)) or
				not PTRS["TERRAIN"].canMoveThrough((self.source[0], self.source[1] - 1))):
			variation = 1
		pos = [self.source[0] * TILESIZE[0] - camera.Left(), self.source[1] * TILESIZE[1] - camera.Top()]
		from Terrain import getTileSubsurface
		if self.activated or self.unitHasKey:
			if PTRS["EDITORMODE"]:
				pic = getTileSubsurface("Traps", 1, 0)
			else:
				pic = getTileSubsurface("Traps", 0, 0)
		else:
			pic = getTileSubsurface("Traps", 0, 1 + variation)
		camera.getSurface().blit(pic, pos)
		if self.key != 0 and (PTRS["EDITORMODE"] or not self.activated and not self.unitHasKey):
			pos = [pos[0] + TILESIZE[0] / 2 - lockPics.get_width() / 2, 
						 pos[1] + TILESIZE[1] /2 - lockPics.get_width() / 2]
			pic = lockPics.subsurface(((0, (self.key - 1) * lockPics.get_width()), (lockPics.get_width(), lockPics.get_width())))
			camera.getSurface().blit(pic, pos)
		
	def activate(self, unit):
		PTRS["TERRAIN"].updateTrapTrigger(self.source, True)
		self.activated += 1
		
	def deactivate(self, unit):
		self.activated = max(self.activated - 1, 0)
		PTRS["TERRAIN"].updateTrapTrigger(self.source, False)
		
	def canMoveThrough(self, unit):
		if unit and (unit.getItemHeld() == self.key or unit.getItemHeld() == -1):
			p = posToCoords(unit.getPos())
			if p[0] == self.source[0] and p[1] == self.source[1]:
				self.unitHasKey = 30
			return True
		return self.activated or self.unitHasKey
		
	def canSeeThrough(self):
		return self.activated or self.unitHasKey
		
	def backup(self):
		Trap.backup(self)
		self.backupUnitHasKey = self.unitHasKey
		
	def restore(self):
		Trap.restore(self)
		self.unitHasKey = self.backupUnitHasKey
		
	def previewTrap(self):
		from Terrain import getTileSubsurface
		return getTileSubsurface("Traps", 1, 0)
		
	def addNumberParameter(self, number):
		if 0 <= number < 5:
			PTRS["EFFECTS"].addEffect(Effects.TextEffect([self.source[0] * TILESIZE[0], self.source[1] * TILESIZE[1]], 
																											[255] * 3, 30, str(number)))
			self.key = number

class SecretDoor(Trap):
	TrapId = PTRS["TRAPTYPES"].SECRETDOOR
	def drawMe(self, camera):
		variation = 0
		pos = [[self.source[0] * TILESIZE[0] - camera.Left(), self.source[1] * TILESIZE[1] - camera.Top()], TILESIZE]
		from Terrain import getTileSubsurface, tilesetLookup
		if PTRS["EDITORMODE"]:
			pic = self.previewTrap()
		elif not self.activated:
			tileset = tilesetLookup(PTRS["TERRAIN"].getAtCoord((self.source[0], self.source[1]), 0))
			pic = getTileSubsurface(tileset, 1, 0)
		else:
			pic = getTileSubsurface("Traps", 0, 0)
		camera.getSurface().blit(pic, pos)
		
	def getPathingHeuristic(self, unit):
		return 0
		
	def activate(self, unit):
		PTRS["TERRAIN"].updateTrapTrigger(self.source, True)
		self.activated += 1
		
	def deactivate(self, unit):
		self.activated = max(self.activated - 1, 0)
		PTRS["TERRAIN"].updateTrapTrigger(self.source, False)
		
	def canMoveThrough(self, unit):
		return self.activated
		
	def canSeeThrough(self):
		return self.activated
		
	def previewTrap(self):
		from Terrain import getTileSubsurface, tilesetLookup
		return getTileSubsurface("Traps", 6, 0)
		
class WallSpikeTrap(Trap):
	TrapId = PTRS["TRAPTYPES"].WALLSPIKETRAP
	def parseArgs(self, args):
		self.timer = 0
		
	def getPathingHeuristic(self, unit):
		return 50
		
	def drawMe(self, camera):
		pos = [[self.source[0] * TILESIZE[0] - camera.Left(), self.source[1] * TILESIZE[1] - camera.Top()], TILESIZE]
		from Terrain import getTileSubsurface
		if PTRS["EDITORMODE"]:
			pic = self.previewTrap()
		elif self.timer >= 30:
			if (not PTRS["TERRAIN"].canMoveThrough((self.source[0] - 1, self.source[1]), True)):
				x = 2; y = 1;
			elif (not PTRS["TERRAIN"].canMoveThrough((self.source[0], self.source[1] - 1), True)):
				x = 1; y = 1;
			elif (not PTRS["TERRAIN"].canMoveThrough((self.source[0], self.source[1] + 1), True)):
				x = 2; y = 2;
			else:
				x = 1; y = 2;
			if self.timer <= 40 or self.timer > 48:
				x += 2
			pic = getTileSubsurface("Traps", x, y)
		else:
			pic = getTileSubsurface("Traps", 0, 0)
		camera.getSurface().blit(pic, pos)
		
	def update(self):
		if self.activated:
			self.timer = max(self.timer - 1, 48)
			self.timer %= 50
			if self.timer > 47 and self.timer <= 48 and self.timer % 2 == 0:
				self.fire()
		else:
			self.timer = max(self.timer - 1, 0)
				
	def fire(self):
		for u in PTRS["UNITS"].getTargets(1, True, True):
			p = posToCoords(u.getPos())
			if p[0] == self.source[0] and p[1] == self.source[1]:
				u.addDamage(1, None)
		
	def previewTrap(self):
		from Terrain import getTileSubsurface
		return getTileSubsurface("Traps", 2, 2)
		
	def canMoveThrough(self, unit):
		return True
		
	def canSeeThrough(self):
		return True
		
class FloorSpikeTrap(WallSpikeTrap):
	TrapId = PTRS["TRAPTYPES"].FLOORSPIKETRAP
	def parseArgs(self, args):
		self.timer = 0
		
	def getPathingHeuristic(self, unit):
		return 50
		
	def drawMe(self, camera):
		pos = [[self.source[0] * TILESIZE[0] - camera.Left(), self.source[1] * TILESIZE[1] - camera.Top()], TILESIZE]
		from Terrain import getTileSubsurface
		if PTRS["EDITORMODE"]:
			pic = self.previewTrap()
		elif self.timer >= 35:
			x = 4; y = 0;
			if self.timer <= 42 or self.timer > 48:
				x = 3; y = 0;
			pic = getTileSubsurface("Traps", x, y)
		else:
			pic = getTileSubsurface("Traps", 2, 0)
		camera.getSurface().blit(pic, pos)
		
	def previewTrap(self):
		from Terrain import getTileSubsurface
		return getTileSubsurface("Traps", 4, 0)
"""
class BoulderTrap(Trap):
	TrapId = PTRS["TRAPTYPES"].POWEREDDOOR
	def parseArgs(self, args):
		self.unitHasKey = 0
		self.backupUnitHasKey = 0
		self.key = 0
		on = 0
		try:
			while on < len(args):
				if args[on] == "-k":
					self.key = int(args[on+1])
					on += 1
				on += 1
		except:
			print "Powered Door Error:", sys.exc_info()[0]
			
	def getPathingHeuristic(self, unit):
		if unit.getItemHeld() == self.key or unit.getItemHeld() == -1:
			return 0
		if self.activated:
			return 0
		else:
			return 10000
			
	def update(self):
		self.unitHasKey -= self.unitHasKey > 0
		
	def saveParameters(self, fileOut):
		fileOut.write("-k " + str(self.key))
		
	def drawMe(self, camera):
		pos = [self.source[0] * TILESIZE[0] - camera.Left(), self.source[1] * TILESIZE[1] - camera.Top()]
		from Terrain import getTileSubsurface
		if self.activated or self.unitHasKey:
			if PTRS["EDITORMODE"]:
				pic = getTileSubsurface("Traps", 1, 0)
			else:
				pic = getTileSubsurface("Traps", 0, 0)
		else:
			pic = getTileSubsurface("Traps", 0, 1 + variation)
		camera.getSurface().blit(pic, pos)
		if self.key != 0 and (PTRS["EDITORMODE"] or not self.activated and not self.unitHasKey):
			pos = [pos[0] + TILESIZE[0] / 2 - lockPics.get_width() / 2, 
						 pos[1] + TILESIZE[1] /2 - lockPics.get_width() / 2]
			pic = lockPics.subsurface(((0, (self.key - 1) * lockPics.get_width()), (lockPics.get_width(), lockPics.get_width())))
			camera.getSurface().blit(pic, pos)
		
	def activate(self, unit):
		self.activated = True
		
	def deactivate(self, unit):
		pass
		
	def canMoveThrough(self, unit):
		return self.activated
		
	def canSeeThrough(self):
		return self.activated
		
	def deactivate(self):
		pass
		
	def previewTrap(self):
		from Terrain import getTileSubsurface
		return getTileSubsurface("Traps", 5, 1)
		
	def addNumberParameter(self, number):
		if 0 <= number < 5:
			PTRS["EFFECTS"].addEffect(Effects.TextEffect([self.source[0] * TILESIZE[0], self.source[1] * TILESIZE[1]], 
																											[255] * 3, 30, str(number)))
			self.key = number

		"""
class Repeater(Trap):
	TrapId = PTRS["TRAPTYPES"].REPEATER
	def parseArgs(self, args):
		self.time = 70
		self.timer = random.randint(0, self.time / 2)
		self.backupTime = 0
		on = 0
		try:
			while on < len(args):
				if args[on] == "-t":
					self.time = int(args[on+1])
					on += 1
				on += 1
		except:
			print "Repeater Error:", sys.exc_info()[0]
			
		self.timer = random.randint(0, self.time / 2)
			
	def addNumberParameter(self, number):
		numberLookup = {0:6, 1:20, 2:40, 3:60, 4:80, 5:100, 6:150, 7:200, 8:300, 9:600}
		PTRS["EFFECTS"].addEffect(Effects.TextEffect([self.source[0] * TILESIZE[0], self.source[1] * TILESIZE[1]], 
																										[255] * 3, 30, str(numberLookup[number])))
		self.time = numberLookup[number]
		
	def saveParameters(self, fileOut):
		fileOut.write("-t " + str(self.time))
		
	def backup(self):
		self.backupTime = self.timer
		
	def restore(self):
		self.timer = self.backupTime
		
	def update(self):
		self.timer = (self.timer + 1) % self.time
		if self.timer == self.time - 1:
			PTRS["TERRAIN"].updateTrapTrigger(self.source, True)
		elif self.timer == 0:
			PTRS["TERRAIN"].updateTrapTrigger(self.source, False)
			
	def drawMe(self, camera):
		if PTRS["EDITORMODE"]:
			pic = self.previewTrap()
			pos = [[self.source[0] * TILESIZE[0] - camera.Left(), self.source[1] * TILESIZE[1] - camera.Top()], TILESIZE]
			camera.getSurface().blit(pic, pos)
			
	def previewTrap(self):
		from Terrain import getTileSubsurface
		return getTileSubsurface("Traps", 5, 0)
		
	def canMoveThrough(self, unit):
		return True
		
	def canSeeThrough(self):
		return True
		
	def triggersTraps(self):
		return self.timer > self.time / 2
		
		
	def activate(self, unit):
		pass
		
	def deactivate(self, unit):
		pass
	
def createTrap(coords, type, args):
	toRet = None
	if type == PTRS["TRAPTYPES"].POWEREDDOOR:
		toRet = PoweredDoor
	elif type == PTRS["TRAPTYPES"].WALLSPIKETRAP:
		toRet = WallSpikeTrap
	elif type == PTRS["TRAPTYPES"].FLOORSPIKETRAP:
		toRet = FloorSpikeTrap
	elif type == PTRS["TRAPTYPES"].REPEATER:
		toRet = Repeater
	elif type == PTRS["TRAPTYPES"].SECRETDOOR:
		toRet = SecretDoor
	else:
		toRet = Trap
	if toRet:
		return toRet(coords, args)
	return None
	