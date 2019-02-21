import pygame, os, random, Globals, Traps
from Globals import *
def loadTerrainPics(terrainPics):
	dirPath = os.path.join("Data", "Pics", "Tiles")
	for file in os.listdir(dirPath):
		file = os.path.splitext(file)
		if file[1].upper() == ".PNG":
			terrainPics[file[0]] = pygame.image.load(os.path.join(dirPath, "".join(file)))
			terrainPics[file[0]].set_colorkey([255, 0, 255])
terrainPics = {}
tilesetMap = {}
itemPics = pygame.image.load(os.path.join("Data", "Pics", "Icons", "Items.png"))
itemPics.set_colorkey([255, 0, 255])
numItems = itemPics.get_height() / itemPics.get_width()
def loadTilesetMap(tilesetMap):
	filePath = os.path.join("Data", "Pics", "Tiles", "Tilesets.txt")
	if os.path.isfile(filePath):
		fileIn = open(filePath)
		line = fileIn.readline()
		while line:
			line = line.split()
			if len(line) == 2 and len(line[1]) < 3 and line[1].isdigit() and len(line[0]) < 30 and line[1] not in tilesetMap:
				tilesetMap[int(line[1])] = line[0]
			line = fileIn.readline()
		fileIn.close()
	else:
		from Data.Pics.Tiles.TSReg import registerTilesets
		registerTilesets()
		
def tilesetLookup(tilesetNum):
	global tilesetMap
	if tilesetNum in tilesetMap:
		return tilesetMap[tilesetNum]
	else:
		return "Default"

def getTileSubsurface(tileset, tile, variation):
	return terrainPics[tileset].subsurface([[tile * TILESIZE[0], variation * TILESIZE[1]], TILESIZE])
	
def generateVariation(tileset):
	noiseTypes = int(terrainPics[tilesetLookup(tileset)].get_height() / TILESIZE[1])
	if noiseTypes:
		nt = random.randint(0, noiseTypes - 1)#int(random.triangular(0, noiseTypes, 0)) + 1
		return nt
	return 0
	
def drawItem(camera, pos, item, drawInWindow = False):
	offset = math.sin(PTRS["FRAME"] / 30.0 * math.pi) * 3
	if not drawInWindow:
		pos = [pos[0] - camera.Left() - itemPics.get_width() / 2, 
					 pos[1] - camera.Top() - itemPics.get_width() / 2 + offset]
	camera.getSurface().blit(itemPics.subsurface(
				((0, item * itemPics.get_width()), 
				 (itemPics.get_width(), itemPics.get_width()))), 
			pos)
	
class PatrolPath:
	def __init__(self, line, loadFromLine = True):
		self.destinations = []
		self.searchAngles = []
		self.scanTime = DEFAULTSCANTIME
		if not loadFromLine:
			self.source = [int(line[0]), int(line[1])]
			return
		self.source = [int(line[1]), int(line[2])]
		on = 3
		try:
			while on < len(line):
				if line[on] == "-d":
					self.destinations += [(int(line[on+1]), int(line[on+2]))]
					on += 2
				elif line[on] == "-t":
					self.scanTime = int(line[on+1])
					on += 1
				elif line[on] == "-a":
					self.searchAngles += [int(line[on+1]) / 180.0 * math.pi]
					on += 1
				on += 1
		except:
			print "Patrol Path Error:", sys.exc_info()[0]
	
	def save(self, fileOut):
		fileOut.write("PATROLPATH " + str(int(self.source[0])) + " " + str(int(self.source[1])) + " ")
		for d in self.destinations:
			fileOut.write("-d " + str(int(d[0])) + " " + str(int(d[1])) + " ")
		fileOut.write("-t " + str(int(self.scanTime)) + " ")
		for a in self.searchAngles:
			fileOut.write("-a " + str(int(a / math.pi * 180)) + " ")
		fileOut.write("\n")
		
	def getScanTime(self):
		return self.scanTime
		
	def getScanAngles(self):
		return self.searchAngles
		
	def setScanTime(self, time):
		self.scanTime = int(time)
		
	def addTargetAngle(self, angle):
		a = angle % (math.pi * 2)
		try:
			self.searchAngles.remove(a)
		except ValueError:
			self.searchAngles += [a]
		
	def addDestination(self, newDest):
		if newDest not in self.destinations and (newDest[0] != self.source[0] or newDest[1] != self.source[1]):
			self.destinations += [newDest]
			
	def removeDestination(self, dest):
		try:
			self.destinations.remove((dest[0], dest[1]))
			return True
		except:
			return False
		
	def getDestination(self, destNum):
		if 0 <= destNum < len(self.destinations):
			return (self.destinations[destNum][0], self.destinations[destNum][1])
		return [self.source[0], self.source[1]]
		
	def getNumDestinations(self):
		return len(self.destinations)
		
	def drawMe(self, camera):
		pygame.draw.rect(camera.getSurface(), [0, 255, 0], [[self.source[0] * TILESIZE[0] - camera.Left(), 
																												 self.source[1] * TILESIZE[1] - camera.Top()], TILESIZE], 1)
		src = [self.source[0] * TILESIZE[0] + TILESIZE[0] / 2 - camera.Left(), self.source[1] * TILESIZE[1] + TILESIZE[1] / 2 - camera.Top()]
		for dest in self.destinations:
			pygame.draw.rect(camera.getSurface(), [0, 255, 0], [[dest[0] * TILESIZE[0] + 2 - camera.Left(), dest[1] * TILESIZE[1] + 2 - camera.Top()], [TILESIZE[0] - 4, TILESIZE[1] - 4]], 1)
			
			dst = [dest[0] * TILESIZE[0] + TILESIZE[0] / 2 - camera.Left(), dest[1] * TILESIZE[1] + TILESIZE[1] / 2 - camera.Top()]
			ang = math.atan2(dst[1] - src[1], dst[0] - src[0])
			dst = [dst[0] - math.cos(ang) * 10, dst[1] - math.sin(ang) * 10]
			
			pygame.draw.line(camera.getSurface(), [0, 255, 0], [src[0] + math.cos(ang) * 10, src[1] + math.sin(ang) * 10], 
																						 dst)
			pygame.draw.line(camera.getSurface(), [0, 255, 0], dst, [dst[0] + math.cos(ang + math.pi * 3 / 4) * 7, dst[1] + math.sin(ang + math.pi * 3 / 4) * 7])
			pygame.draw.line(camera.getSurface(), [0, 255, 0], dst, [dst[0] + math.cos(ang - math.pi * 3 / 4) * 7, dst[1] + math.sin(ang - math.pi * 3 / 4) * 7])
		
		for a in self.searchAngles:
			pygame.draw.line(camera.getSurface(), [200, 0, 0], [src[0] + math.cos(a) * 5, src[1] + math.sin(a) * 5],
																						 [src[0] + math.cos(a) * 20, src[1] + math.sin(a) * 20])
		
class TrapTrigger:
	def __init__(self, line, loadFromLine = True):
		self.destinations = []
		self.delayTime = 1
		if not loadFromLine:
			self.source = [int(line[0]), int(line[1])]
			self.destinations = [(int(line[0]), int(line[1]))]
			return
		self.source = [int(line[1]), int(line[2])]
		self.destinations = [(int(line[1]), int(line[2]))]
		on = 3
		try:
			while on < len(line):
				if line[on] == "-d":
					self.destinations += [(int(line[on+1]), int(line[on+2]))]
					on += 2
				elif line[on] == "-t":
					self.delayTime = int(line[on+1])
					on += 1
				on += 1
		except:
			print "Trap Trigger Error:", sys.exc_info()[0]
			
	def finishedLoading(self):
		if PTRS["TERRAIN"].triggersTraps((self.source[0], self.source[1])):
			for d in self.destinations:
				trap = PTRS["TERRAIN"].getTrapAtCoord(d)
				if trap:
					trap.activate(None)
	
	def save(self, fileOut):
		fileOut.write("TRAPTRIGGER " + str(int(self.source[0])) + " " + str(int(self.source[1])) + " ")
		for d in self.destinations:
			fileOut.write("-d " + str(int(d[0])) + " " + str(int(d[1])) + " ")
		fileOut.write("-t " + str(int(self.delayTime)) + " ")
		fileOut.write("\n")
		
	def getDelayTime(self):
		return self.delayTime
		
	def setDelayTime(self, time):
		self.delayTime = int(time)
		
	def addDestination(self, newDest):
		if newDest not in self.destinations and (newDest[0] != self.source[0] or newDest[1] != self.source[1]):
			self.destinations += [newDest]
			if PTRS["TERRAIN"].triggersTraps((self.source[0], self.source[1])):
				trap = PTRS["TERRAIN"].getTrapAtCoord(newDest)
				if trap:
					trap.activate(None)
			
	def removeDestination(self, dest):
		try:
			if PTRS["TERRAIN"].triggersTraps((self.source[0], self.source[1])):
				on = 0
				while on < len(self.destinations) and self.destinations[on] != (dest[0], dest[1]):
					on += 1
				if on < len(self.destinations):
					trap = PTRS["TERRAIN"].getTrapAtCoord(self.destinations[on])
					trap.deactivate(None)
					del self.destinations[on]
			else:
				self.destinations.remove((dest[0], dest[1]))
			return True
		except:
			return False
			
	def removeAllDestinations(self):
		while len(self.destinations) and self.removeDestination(self.destinations[0]):
			pass
			
	def activate(self):
		for d in self.destinations:
			trap = PTRS["TERRAIN"].getTrapAtCoord(d)
			if trap:
				trap.activate(None)
				
	def deactivate(self):
		for d in self.destinations:
			trap = PTRS["TERRAIN"].getTrapAtCoord(d)
			if trap:
				trap.deactivate(None)
			
	def getDestination(self, destNum):
		if 0 <= destNum < len(self.destinations):
			return (self.destinations[destNum][0], self.destinations[destNum][1])
		return [self.source[0], self.source[1]]
		
	def getNumDestinations(self):
		return len(self.destinations)
		
	def unitEnteredTrigger(self, unit):
		for dest in self.destinations:
			trap = PTRS["TERRAIN"].getTrapAtCoord(dest)
			if trap:
				trap.activate(unit)
		
	def unitExitedTrigger(self, unit):
		for dest in self.destinations:
			trap = PTRS["TERRAIN"].getTrapAtCoord(dest)
			if trap:
				trap.deactivate(unit)
		
	def notifyUnitMovement(self, unit, lastPos, currPos):
		if currPos[0] != lastPos[0] or currPos[1] != lastPos[1]:
			if currPos[0] == self.source[0] and currPos[1] == self.source[1]:
				self.unitEnteredTrigger(unit)
			elif lastPos[0] == self.source[0] and lastPos[1] == self.source[1]:
				self.unitExitedTrigger(unit)
		
	def drawMe(self, camera):
		pygame.draw.rect(camera.getSurface(), [255, 0, 0], [[self.source[0] * TILESIZE[0] - camera.Left(), self.source[1] * TILESIZE[1] - camera.Top()], TILESIZE], 1)
		src = [self.source[0] * TILESIZE[0] + TILESIZE[0] / 2 - camera.Left(), self.source[1] * TILESIZE[1] + TILESIZE[1] / 2 - camera.Top()]
		for dest in self.destinations:
			if dest[0] != self.source[0] or dest[1] != self.source[1]:
				pygame.draw.rect(camera.getSurface(), [255, 0, 0], [[dest[0] * TILESIZE[0] + 2 - camera.Left(), dest[1] * TILESIZE[1] + 2 - camera.Top()], [TILESIZE[0] - 4, TILESIZE[1] - 4]], 1)
				
				dst = [dest[0] * TILESIZE[0] + TILESIZE[0] / 2 - camera.Left(), dest[1] * TILESIZE[1] + TILESIZE[1] / 2 - camera.Top()]
				ang = math.atan2(dst[1] - src[1], dst[0] - src[0])
				dst = [dst[0] - math.cos(ang) * 10, dst[1] - math.sin(ang) * 10]
				
				pygame.draw.line(camera.getSurface(), [255, 0, 0], [src[0] + math.cos(ang) * 10, src[1] + math.sin(ang) * 10], 
																							 dst)
				pygame.draw.line(camera.getSurface(), [255, 0, 0], dst, [dst[0] + math.cos(ang + math.pi * 3 / 4) * 7, dst[1] + math.sin(ang + math.pi * 3 / 4) * 7])
				pygame.draw.line(camera.getSurface(), [255, 0, 0], dst, [dst[0] + math.cos(ang - math.pi * 3 / 4) * 7, dst[1] + math.sin(ang - math.pi * 3 / 4) * 7])
		
		
		
class Terrain:
	def __init__(self, loadMap = True):
		self.terrain = [[[0, 1, 0]] * 40] + [[[0, 1, 0]] + [[0, 0, 0]] * 38 + [[0, 1, 0]]] * 28 + [[[0, 1, 0]] * 40]
		self.spawners = []
		self.terrainChanges = {}
		self.patrolPaths = {}
		self.enemies = {}
		self.trapTriggers = {}
		self.traps = {}
		self.items = {}
		self.backupItems = {}
		self.players = []
		self.backupSpawner = [0, 0]
		self.worldSize = (800, 600)
		self.tileset = "Default"
		if loadMap:
			self.level = "L1.txt"
			self.reset(True)
		self.terrainPic = None
		
	def reset(self, firstLoad = False):
		self.loadFromFile(self.level, firstLoad)
		
	def backup(self):
		self.backupSpawner = self.getSpawnPos()
		for pos in self.traps:
			self.traps[pos].backup()
		self.backupItems = {}
		for pos in self.items:
			self.backupItems[pos] = self.items[pos]
	
	def restore(self):
		self.setSpawner(self.backupSpawner)
		for pos in self.traps:
			self.traps[pos].restore()
		self.items = {}
		for pos in self.backupItems:
			self.items[pos] = self.backupItems[pos]
		
	def getPatrolPathAtPos(self, pos):
		coords = posToCoords(pos)
		if coords in self.patrolPaths:
			return self.patrolPaths[coords]
		return None
		
	def getTrapTriggerAtPos(self, pos):
		coords = posToCoords(pos)
		if coords in self.trapTriggers:
			return self.trapTriggers[coords]
		return None
		
	def notifyUnitMovement(self, unit, lastPos, pos):
		lPos = posToCoords(lastPos)
		cPos = posToCoords(pos)
		if cPos in self.trapTriggers:
			self.trapTriggers[cPos].notifyUnitMovement(unit, lPos, cPos)
		if lPos in self.trapTriggers:
			self.trapTriggers[lPos].notifyUnitMovement(unit, lPos, cPos)
		#for pos in self.trapTriggers:
		#	
		
	def changeItem(self, pos, increase):
		coords = (int(pos[0]), int(pos[1]))
		#TODO: Handle multiple enemy types
		if coords in self.items:
			if increase:
				self.items[coords] += 1
			else:
				self.items[coords] -= 1
			
			if self.items[coords] >= numItems or self.items[coords] < 0:
				del self.items[coords]
		else:
			if increase:
				self.items[coords] = 0
			else:
				self.items[coords] = numItems - 1
				
	def pickUpItem(self, pos, oldItem = None):
		coords = posToCoords(pos)
		if coords in self.items:
			toRet = self.items[coords]
			if oldItem == None:
				del self.items[coords]
			else:
				self.items[coords] = oldItem
			return toRet
		return None
		
	def changeEnemySpawner(self, pos, increase):
		coords = (int(pos[0]), int(pos[1]))
		#TODO: Handle multiple enemy types
		if coords in self.enemies:
			if increase:
				delta = 1
			else:
				delta = -1
			currLoc = (PTRS["ENEMYTYPES"].index(self.enemies[coords][1]) + delta) % len(PTRS["ENEMYTYPES"])
			if PTRS["ENEMYTYPES"][currLoc] == None:
				del self.enemies[coords]
			else:
				self.enemies[coords][1] = PTRS["ENEMYTYPES"][currLoc]
		else:
			if increase:
				self.enemies[coords] = [0, PTRS["ENEMYTYPES"][1]]
			else:
				self.enemies[coords] = [0, PTRS["ENEMYTYPES"][len(PTRS["ENEMYTYPES"]) - 1]]
		PTRS["UNITS"].reload()
		
	def addNumberParameter(self, coord, number):
		coords = (int(coord[0]), int(coord[1]))
		if coords in self.traps:
			self.traps[coords].addNumberParameter(number)
		
	def addAngleParameter(self, coord, angle):
		coords = (int(coord[0]), int(coord[1]))
		if coords in self.traps:
			self.traps[coords].addAngleParameter(angle)
		
	def changeTrapType(self, pos, trapType, remove):
		coords = (int(pos[0]), int(pos[1]))
		newTrap = None
		if coords in self.traps and self.traps[coords].TrapId == trapType:
			del self.traps[coords]
		else:
			if coords in self.traps:
				del self.traps[coords]
			if not remove:
				newTrap = Traps.createTrap(coords, trapType, [])
		if newTrap:
			self.traps[coords] = newTrap
		
	def getSpawnPos(self):
		return [self.spawnPos[0], self.spawnPos[1]]
		#for sp in self.spawners:
		#	if self.getAtCoord(sp) == 2:
		#		return [sp[0] * TILESIZE[0] + TILESIZE[0] / 2, sp[1] * TILESIZE[1] + TILESIZE[1] / 2]
				
	def removePatrolDestination(self, source, dest):
		if (self.patrolPaths[source].removeDestination(dest) and not self.patrolPaths[source].destinations) or source == dest:
			del self.patrolPaths[source]
			
	def removeTrapDestination(self, source, dest):
		if (self.trapTriggers[source].removeDestination(dest) and not self.trapTriggers[source].destinations) or source == dest:
			self.trapTriggers[source].removeAllDestinations()
			del self.trapTriggers[source]
		
	def getTerrainChanges(self, playerNum):
		toRet = []
		if playerNum in self.terrainChanges:
			toRet = " ".join(self.terrainChanges[playerNum])
			del self.terrainChanges[playerNum]
		return toRet
		
	def randomizeVariations(self):
		y = 0
		for line in self.terrain:
			x = 0
			for square in line:
				self.terrain[y][x] = (square[0], square[1], generateVariation(square[0]))
				self.setTile([x, y], self.terrain[y][x])
				x += 1
			y += 1
			
	def getWorldSize(self):
		return self.worldSize
		
	def loadFromFile(self, file, firstLoad = False):
		self.level = file
		del self.terrainPic
		self.terrainPic = None
		self.terrain = []
		self.spawners = []
		self.spawnPos = [-20, -20]
		self.tileset = "Default"
		fileIn = open(os.path.join("Data", "Levels", file))
		on = 0
		line = fileIn.readline()
		line = line.strip().split()
		rows = int(line[0]); cols = int(line[1])
		self.worldSize = (int(cols * TILESIZE[0]), int(rows * TILESIZE[1]))
		line = fileIn.readline()
		while line and not "END" in line:
			line = line.strip().split()
			if line[0].upper() == "TILESET" or line[0].upper() == "TS":
				if len(line) >= 2:
					self.tileset = line[1]
			else:
				self.terrain += [[]]
				x = 0
				while 0 <= x < len(line):
					p = line[x]
					if p.isdigit():
						self.terrain[on] += [[0, int(p), generateVariation(0)]]
						p = int(p)
						self.setTile([len(self.terrain[on]) - 1, on], self.terrain[on][len(self.terrain[on]) - 1])
					elif p.upper() == "TILESET" or p.upper() == "TS":
						if len(line) > x + 1:
							self.tileset = line[x + 1]
							x += 1
					else:
						p = p.split("-")
						if len(p) >= 3 and p[0].isdigit() and p[1].isdigit() and p[2].isdigit():
							self.terrain[on] += [[int(p[0]), int(p[1]), int(p[2])]]
							self.setTile([len(self.terrain[on]) - 1, on], self.terrain[on][len(self.terrain[on]) - 1])
						else:
							self.terrain[on] += [[0, 0, 0]]
							self.setTile([len(self.terrain[on]) - 1, on], self.terrain[on][len(self.terrain[on]) - 1])
					x += 1
				if len(self.terrain[on]) < cols:
					for i in range(cols - len(self.terrain[on])):
						self.terrain[on] += [[0, 0, 0]]
				on += 1
			line = fileIn.readline()
			
			pct = fileIn.tell() / float(os.fstat(fileIn.fileno())[6])
			self.drawProgressBar(pct)

		if len(self.terrain) < rows:
			for i in range(rows - len(self.terrain)):
				self.terrain += [[]]
				for j in range(cols):
					self.terrain[len(self.terrain) - 1] += [[0, 0, 0]]
					
		self.loadLevelObjects(fileIn)
		for p in self.trapTriggers:
			self.trapTriggers[p].finishedLoading()
		self.backup()
		
	def saveToFile(self):
		fileOut = open(os.path.join("Data", "Levels", "temp.lv"), "w")
		fileOut.write(str(int(self.worldSize[1] / TILESIZE[1])) + " " + str(int(self.worldSize[0] / TILESIZE[0])) + "\n")
		for row in self.terrain:
			for col in row:
				fileOut.write(str(col[0]) + "-" + str(col[1]) + "-" + str(col[2]) + " ")
			fileOut.write("\n")
		fileOut.write("END\n")
		
		for p in self.players:
			fileOut.write("PLAYER " + str(p) + "\n")
		for pos in self.enemies:
			fileOut.write("ENEMY " + str(int(pos[0])) + " " + str(int(pos[1])) + " " + 
											str(self.enemies[pos][0]) + " "+ str(self.enemies[pos][1]) + "\n")
		for p in self.patrolPaths:
			self.patrolPaths[p].save(fileOut)
		for p in self.trapTriggers:
			self.trapTriggers[p].save(fileOut)
		for p in self.traps:
			self.traps[p].save(fileOut)
		for p in self.items:
			fileOut.write("ITEM " + str(int(p[0])) + " " + str(int(p[1])) + " " + str(int(self.items[p])) + "\n")
		
		fileOut.close()
		if os.path.exists(os.path.join("Data", "Levels", "deleteMe.txt")):
			os.remove(os.path.join("Data", "Levels", "deleteMe.txt"))
		os.rename(os.path.join("Data", "Levels", self.level), os.path.join("Data", "Levels", "deleteMe.txt"))
		os.rename(os.path.join("Data", "Levels", "temp.lv"), os.path.join("Data", "Levels", self.level))
		os.remove(os.path.join("Data", "Levels", "deleteMe.txt"))
		
	def drawProgressBar(self, pct):
		size = [400, 40]
		pygame.draw.rect(surface, [255, 0, 0], [[SCREENSIZE[0] / 2 - size[0] / 2, SCREENSIZE[1] / 2 - size[1] / 2], [int(size[0] * pct), size[1]]])
		pygame.draw.rect(surface, [255] * 3, [[SCREENSIZE[0] / 2 - size[0] / 2, SCREENSIZE[1] / 2 - size[1] / 2], size], 1)
		pygame.display.update()
			
	def addPatrolPathSource(self, sourcePos):
		p = (int(sourcePos[0]), int(sourcePos[1]))
		if p not in self.patrolPaths:
			self.patrolPaths[p] = PatrolPath(sourcePos, False)
			
	def addTrapTriggerSource(self, sourcePos):
		p = (int(sourcePos[0]), int(sourcePos[1]))
		if p not in self.trapTriggers:
			self.trapTriggers[p] = TrapTrigger(sourcePos, False)
			
	def getTrapAtCoord(self, coord):
		if coord in self.traps:
			return self.traps[coord]
		return None
		
	def updateTrapTrigger(self, coord, activate):
		if coord in self.trapTriggers:
			if activate:
				self.trapTriggers[coord].activate()
			else:
				self.trapTriggers[coord].deactivate()
			
	def loadLevelObjects(self, fileIn):
		self.patrolPaths = {}
		self.trapTriggers = {}
		self.traps = {}
		self.items = {}
		self.enemies = {}
		self.players = []
		line = fileIn.readline().split()
		while line:
			pct = fileIn.tell() / float(os.fstat(fileIn.fileno())[6])
			self.drawProgressBar(pct)
			if not line:
				pass
			elif line[0] == "PATROLPATH": #PATROLPATH startCol startRow endCol endRow
				self.patrolPaths[(int(line[1]), int(line[2]))] = PatrolPath(line)
			elif line[0] == "TRAPTRIGGER":
				self.trapTriggers[(int(line[1]), int(line[2]))] = TrapTrigger(line)
			elif line[0] == "TRAP":
				trapCoords = (int(line[1]), int(line[2]))
				newTrap = Traps.createTrap(trapCoords, int(line[3]), line[4:])
				if newTrap:
					self.traps[trapCoords] = newTrap
			elif line[0] == "ENEMY": #ENEMY startCol startRow type
				self.enemies[(int(line[1]), int(line[2]))] = [line[3], line[4]]
			elif line[0] == "PLAYER": #PLAYER type
				self.players += [line[1]]
			elif line[0] == "ITEM":
				itemCoords = (int(line[1]), int(line[2]))
				self.items[itemCoords] = int(line[3])
			line = fileIn.readline().split()
		fileIn.close()
		
	def getRandomSpawnPos(self, type):
		if type in self.spawners:
			spawner = self.spawners[type][random.randint(0, len(self.spawners[type]) - 1)]
			return [spawner[0] * TILESIZE[0] + int(TILESIZE[0] / 2), spawner[1] * TILESIZE[1] + int(TILESIZE[1])]
		
	def setAtPos(self, pos, newType):
		coords = [int(pos[0] / TILESIZE[0]), int(pos[1] / TILESIZE[1])]
		if 0 <= coords[1] < len(self.terrain) and 0 <= coords[0] < len(self.terrain[coords[1]]):
			self.terrain[coords[1]][coords[0]] = newType
			for pl in range(Globals.players.getNumPlayers()):
				Globals.players.getPlayer(pl).addTerrainChange(str(coords[0]) + "|" + str(coords[1]) + "|" + str(int(newType)))
	
	def getAtPos(self, pos, type=1):
		coords = [int(pos[0] / TILESIZE[0]), int(pos[1] / TILESIZE[1])]
		return self.getAtCoord(coords, type)
		
	def getAtCoord(self, coords, type=1):
		if 0 <= int(coords[1]) < len(self.terrain) and 0 <= int(coords[0]) < len(self.terrain[int(coords[1])]) and 0 <= type <= 2:
			return self.terrain[int(coords[1])][int(coords[0])][type]
		return 1
		
	def convertToString(self):
		toRet = ""
		for y in range(len(self.terrain)):
			for x in range(len(self.terrain[y])):
				if toRet:
					toRet += " "
				toRet += str(x) + "|" + str(y) + "|" + str("-".join(self.terrain[y][x]))
		return toRet

	def setSpawner(self, pos):
		coords = [int(pos[0] / TILESIZE[0]), int(pos[1] / TILESIZE[1])]
		for sp in self.spawners:
			if sp[0] == coords[0] and sp[1] == coords[1]:
				for sp2 in self.spawners:
					self.setTile(sp2, (self.getAtCoord(sp2, 0), 3, self.getAtCoord(sp2, 2)))
				self.setTile(sp, (self.getAtCoord(sp, 0), 2, self.getAtCoord(sp, 2)))
				self.spawnPos = (coords[0] * TILESIZE[0] + TILESIZE[0] / 2, coords[1] * TILESIZE[1] + TILESIZE[1] / 2)
				break

	def recursiveSetTile(self, coords, newValue):
		if 0 > coords[0] or 0 > coords[1] or self.worldSize[0] / TILESIZE[0] <= coords[0] or self.worldSize[1] / TILESIZE[1] <= coords[1]:
			return
		tileAt = self.getAtCoord(coords, 1)
		tileSetAt = self.getAtCoord(coords, 0)
		self.setTile(coords, newValue)
		for mod in [[-1, 0], [1, 0], [0, -1], [0, 1]]:
			tile = self.getAtCoord((coords[0] + mod[0], coords[1] + mod[1]), 1)
			tileSet = self.getAtCoord((coords[0] + mod[0], coords[1] + mod[1]), 0)
			if (tile == tileAt and tileSet == tileSetAt):
				self.recursiveSetTile((coords[0] + mod[0], coords[1] + mod[1]), newValue)
	
	def setTile(self, coords, newValue):
		if self.terrainPic is None:
			self.terrainPic = pygame.Surface(self.worldSize)
			
		if isSpawner(newValue[1]):
			if (coords[0], coords[1]) not in self.spawners:
				self.spawners += [(coords[0], coords[1])]
			if newValue[1] == 2 or self.spawnPos[0] == -20 and self.spawnPos[1] == -20:
				self.spawnPos = (coords[0] * TILESIZE[0] + TILESIZE[0] / 2, coords[1] * TILESIZE[1] + TILESIZE[1] / 2)
		elif (coords[0], coords[1]) in self.spawners:
			self.spawners.remove((coords[0], coords[1]))
		
		self.terrain[coords[1]][coords[0]] = (newValue[0], newValue[1], newValue[2])
		pos = (coords[0] * TILESIZE[0], coords[1] * TILESIZE[1])
		pic = getTileSubsurface(tilesetLookup(newValue[0]), newValue[1], newValue[2])
		self.terrainPic.blit(pic, pos)
		
	def update(self):
		for p in self.traps:
			self.traps[p].update()
		
	def drawMe(self, camera):
		if not self.terrainPic:
			return
		camera.getSurface().blit(self.terrainPic.subsurface([
				(max(camera.Left(), 0), max(camera.Top(), 0)), 
				(min(camera.Width(), self.worldSize[0] - camera.Left()), min(camera.Height(), self.worldSize[1] - camera.Top()))
				]), [max(-camera.Left(), 0), max(-camera.Top(), 0)])
		if PTRS["DRAWDEBUG"] or PTRS["EDITORMODE"]:
			for p in self.patrolPaths:
				self.patrolPaths[p].drawMe(camera)
			for p in self.trapTriggers:
				self.trapTriggers[p].drawMe(camera)
		for p in self.traps:
			self.traps[p].drawMe(camera)
		for p in self.items:
			pos = [p[0] * TILESIZE[0] + TILESIZE[0] / 2, 
						 p[1] * TILESIZE[1] + TILESIZE[1] / 2]
			drawItem(camera, pos, self.items[p])
			
	def canMoveThrough(self, coord, unit = None, ignoreTraps = False):
		if canMoveThrough(self.getAtCoord(coord)):
			if coord not in self.traps or ignoreTraps or self.traps[coord].canMoveThrough(unit):
				return True
		return False
		
	def triggersTraps(self, coord):
		if (not self.canMoveThrough(coord)) or coord in self.traps and self.traps[coord].triggersTraps():
			return True
		return False
	
	def canSeeThrough(self, coord, unit = None):
		coord = (coord[0], coord[1])
		if canSeeThrough(self.getAtCoord(coord)):
			if coord not in self.traps or self.traps[coord].canSeeThrough():
				return True
		return False
		
	def getShortestPath(self, start, target, radius, unit, checkForTraps = False):
		#if ((start[0], start[1]), (target[0], target[1])) in self.cachedPaths:
		#	return self.cachedPaths[((start[0], start[1]), (target[0], target[1]))]
		finish = target
		#walkable = self.createWalkableGrid(chars)
		closedSet = {}
		openSet = {(start[0], start[1]):[0,self.calcH(start,finish),None]}
		closest = (start[0], start[1])
		while openSet:
			curr = self.getLowest(openSet)
			closedSet[curr] = openSet[curr]
			if closedSet[closest][1] > closedSet[curr][1]:
				closest = curr
			if distance(curr, finish) <= radius:
				return self.reconstruct(curr,closedSet)
			del openSet[curr]
			for y in [(curr[0] + 1, curr[1] + 1),(curr[0], curr[1] + 1),(curr[0] - 1, curr[1] + 1),
					  (curr[0] + 1, curr[1]    )                       ,(curr[0] - 1, curr[1]    ),
					  (curr[0] + 1, curr[1] - 1),(curr[0], curr[1] - 1),(curr[0] - 1, curr[1] - 1)]:
				if self.canMoveThrough(y, unit):
					if y in closedSet:
						if closedSet[y][0] > closedSet[curr][0] + self.getCost(curr, y, unit, checkForTraps):
							closedSet[y][0] = closedSet[curr][0] + self.getCost(curr, y, unit, checkForTraps)
							closedSet[y][2] = curr
					elif y not in openSet:
						openSet[y] = [closedSet[curr][0] + self.getCost(curr, y, unit, checkForTraps),self.calcH(y,finish), curr]
					elif y in openSet:
						if openSet[y][0] > closedSet[curr][0] + + self.getCost(curr, y, unit, checkForTraps):
							openSet[y][0] = closedSet[curr][0] + self.getCost(curr, y, unit, checkForTraps)
							openSet[y][2] = curr
		return self.reconstruct(closest,closedSet)
		
	def calcH(self,node,goal):
		diagDist = min(abs(node[0] - goal[0]), abs(node[1] - goal[1]))
		straightDist = abs(node[0] - goal[0]) + abs(node[1] - goal[1])
		return 14 * diagDist + 10 * (straightDist - diagDist * 2)
		
	def getLowest(self, set):
		lowest = (99999, 99999)
		toRet = 0
		for i in set:
			currScore = set[i][0] + set[i][1]
			if lowest[0] + lowest[1] > currScore:
				lowest = (set[i][0], set[i][1])
				toRet = i
			if lowest[0] + lowest[1] == currScore and lowest[1] > set[i][1]:
					lowest = (set[i][0], set[i][1])
					toRet = i	
		return toRet
		
	def getCost(self,	nodeA, nodeB, unit, checkForTraps):
		cost = abs(nodeA[0] - nodeB[0]) + abs(nodeA[1] - nodeB[1])
		toRet = 100000
		if cost == 1:
			toRet = 10
		if cost == 2:
			toRet = 14
		if checkForTraps and (nodeB[0], nodeB[1]) in self.traps:
				toRet += self.traps[(nodeB[0], nodeB[1])].getPathingHeuristic(unit)
		return toRet
		
	def reconstruct(self,tail,set):
		if set[tail][2] != None:
			return [tail] + self.reconstruct(set[tail][2],set)
		else:
			return []
		
def canMoveThrough(terrain):
	return terrain in [0, 2, 3, 4, 5, 8]
	
def canSeeThrough(terrain):
	return terrain in [0, 2, 3, 4, 5]

def isSpawner(terrain):
	return terrain in [2, 3]
	
def isInactiveSpawner(terrain):
	return terrain in [3]
	
def isExitPortal(terrain):
	return terrain in [4]

def distance(p1,p2):
	return max(abs(p1[0] - p2[0]),abs(p1[1] - p2[1]))
	
loadTilesetMap(tilesetMap)
loadTerrainPics(terrainPics)
	
PTRS["TERRAIN"] = Terrain(False)