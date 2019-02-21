print "Loading Pygame."
import pygame
print "Pygame Loaded.  Initializing."
pygame.init()
print "Pygame Initialized."
import sys, math, Projectiles, Effects, Terrain, Units, Globals, Traps
from pygame.locals import *
from Globals import *
class Camera:
	def __init__(self, dimensions = [400, 600]):
		self.top = 0
		self.left = 0
		self.width = dimensions[0]
		self.height = dimensions[1]
		self.surface = pygame.Surface([self.width, self.height])
		
	def setPos(self, pos):
		self.left = pos[0] - self.width / 2
		self.top = pos[1] - self.height / 2
	
	def getSurface(self):
		return self.surface
	
	def Top(self):
		return self.top
	
	def Left(self):
		return self.left
		
	def Width(self):
		return self.width
		
	def Height(self):
		return self.height
class MainGame:
	def loadLevel(self, levelName, selected):
		PTRS["TERRAIN"].loadFromFile(levelName)
		PTRS["UNITS"].reload()
		for i in range(min(NUMPLAYERS, len(selected))):
			PTRS["UNITS"].selectUnit(selected[i], i + 1)
		PTRS["UNITS"].backup()
		
	def resetUnits(self):
		PTRS["UNITS"].reload()
		#for pl in PTRS["TERRAIN"].players:
		#	PTRS["UNITS"].addPlayerUnit(pl)
		#for i in PTRS["TERRAIN"].enemies:
		#	PTRS["UNITS"].addEnemyUnit([i[0] * TILESIZE[0] + TILESIZE[0] / 2, i[1] * TILESIZE[1] + TILESIZE[1] / 2], PTRS["TERRAIN"].enemies[i])

	def drawHUD(self):
		drawTextBox(surface, [860, 0], [200, 20], self.stateNames[self.currState], False)
		if self.currState == self.States.BLOCK:
			drawTextBox(surface, [805, 30], [194, 300], "LClick - set block type\n# Key - Change current tile\nCtrl + # Key - Change current tileset\nShift+LClick - Area fill (BUGGY - SAVE BEFORE USING)\n" +
																									"Ctrl + r - Re-randomize all tiles", False)
			topLeft = [815, 135]
			for i in range(9):
				drawTextBox(surface, [topLeft[0] + i * TILESIZE[0], topLeft[1] - 20], [200, 20], str(i + 1), False)
			for j in range(len(Terrain.tilesetMap)):
				drawTextBox(surface, [topLeft[0] - 15, topLeft[1] - 3 + j * TILESIZE[1]], [200, 20], str(j + 1), False)
			for i in range(9):
				for j in range(len(Terrain.tilesetMap)):
					surface.blit(Terrain.getTileSubsurface(Terrain.tilesetLookup((j) % len(Terrain.tilesetMap)), i, 0), (topLeft[0] + i * TILESIZE[0], topLeft[1] + j * TILESIZE[1]))
			pygame.draw.rect(surface, [255, 255, 0], ((topLeft[0] + self.curTile * TILESIZE[0] - 1, topLeft[1] - 1 + self.curTileset * TILESIZE[1]), (TILESIZE[0] + 2, TILESIZE[1] + 2)), 1)
		elif self.currState == self.States.PATROL:
			drawTextBox(surface, [805, 30], [194, 300], "LClick - add patrol position / select patrol position\nRClick - remove patrol position\nClick and Drag - add/remove destination\nShift + LClick - add multiple patrol destinations\n" +
																									"# Key - Change AI search time\n'A' - add/remove search target", False)
		elif self.currState == self.States.TRAPTRIGGERS:
			drawTextBox(surface, [805, 30], [194, 300], "LClick - add pressure plate\nRClick - remove pressure plate\nClick and Drag - add/remove trap to be triggered\nShift-LClick - add multiple triggers\n'a' - add search angle\n# Key - Set search time", False)
		elif self.currState == self.States.ENEMIES:
			drawTextBox(surface, [805, 30], [194, 300], "LClick - change enemy type\nRClick - change enemy type", False)
		elif self.currState == self.States.TRAPS:
			drawTextBox(surface, [805, 30], [194, 300], "LClick - set / remove spawner at location\nRClick - remove spawner at location\n" + 
																									"# Key - set current trap", False)
			topLeft = [815, 110]
			if self.trapPreviews == []:
				for i in range(Traps.NumTrapTypes):
					self.trapPreviews += [Traps.createTrap((42 + i, 1), i, [])]
			on = 0
			for i in self.trapPreviews:
				if i:
					surface.blit(i.previewTrap(), (topLeft[0] + on * TILESIZE[0], topLeft[1]))
					if on == self.curTrap:
						pygame.draw.rect(surface, [255, 255, 255], ((topLeft[0] + on * TILESIZE[0], topLeft[1]), TILESIZE), 2)
				on += 1
		elif self.currState == self.States.ITEMS:
			drawTextBox(surface, [805, 30], [194, 300], "LClick - change item\nRClick - remove item\n", False)
				
	def getLocalMousePos(self, mPos, camera):
		toRet = (int(min(mPos[0] + camera.Left(), PTRS["TERRAIN"].getWorldSize()[0] - 1) / TILESIZE[0]), 
						 int(min(mPos[1] + camera.Top(), PTRS["TERRAIN"].getWorldSize()[1] - 1) / TILESIZE[1]))
		return toRet
				
	def editor(self, level):
		if not os.path.exists(os.path.join("Data", "Levels", level)):
			fileOut = open(os.path.join("Data", "Levels", level), "w")
			fileOut.write("30 40\n")
			fileOut.close()
		PTRS["EDITORMODE"] = True
		self.States = enum('BLOCK',  'PATROL', 'ENEMIES', 'TRAPTRIGGERS',  'TRAPS', 'ITEMS')
		self.stateNames = ['Blocks', 'Patrol', 'Enemies', 'Trap Triggers', 'Traps', 'Items']
		self.trapPreviews = []
		camera = Camera((800, 600))
		self.currState = self.States.BLOCK
		gamestate = {"done":False}
		#if level in os.listdir(""):
		#	pass
		self.loadLevel(level, [])
		lastTime = 0
		self.curTile = 0
		self.curTileset = 0
		self.curTrap = 0
		gamestate["done"] = False
		mDown = False
		mPos = [0, 0]
		selectedTile = (0,0)
		ArrowKeys = {}
		while not gamestate["done"]:
			for ev in pygame.event.get():
				if ev.type == QUIT:
					sys.exit()
				if ev.type == KEYDOWN:
					if ev.key == K_s and (ev.mod in [KMOD_LCTRL, KMOD_RCTRL]):
						PTRS["TERRAIN"].saveToFile()
					if ev.key == K_t and (ev.mod in [KMOD_LCTRL, KMOD_RCTRL]):
						PTRS["EDITORMODE"] = False
						Globals.surface = pygame.display.set_mode(SCREENSIZE, 0)
						self.playGame(level)
						Globals.surface = pygame.display.set_mode(EDITORSCREENSIZE, 0)
						PTRS["EDITORMODE"] = True
						self.loadLevel(level, [])
					elif ev.key >= K_1 and ev.key <= K_9:
						if self.currState == self.States.PATROL:
							if selectedTile in PTRS["TERRAIN"].patrolPaths:
								PTRS["TERRAIN"].patrolPaths[selectedTile].setScanTime(ScanTimeLookup[ev.key - K_1])
								PTRS["EFFECTS"].addEffect(Effects.TextEffect([selectedTile[0] * TILESIZE[0], selectedTile[1] * TILESIZE[1]], 
																														 [255] * 3, 30, str(ScanTimeLookup[ev.key - K_1])))
						elif self.currState == self.States.BLOCK:
							if ev.mod in [KMOD_LCTRL, KMOD_RCTRL]:
								self.curTileset = min(ev.key - K_1, len(Terrain.tilesetMap))
							else:
								self.curTile = ev.key - K_1
						elif self.currState == self.States.TRAPS:
							if ev.mod in [KMOD_LCTRL, KMOD_RCTRL]:
								self.curTrap =  min((self.curTrap % 9) + (ev.key - K_1) * 9, Traps.NumTrapTypes - 1)
							elif ev.mod in [KMOD_LSHIFT, KMOD_RSHIFT]:
								PTRS["TERRAIN"].addNumberParameter(mPos, ev.key - K_1)
							else:
								self.curTrap =  min((self.curTrap / 9) * 9 + (ev.key - K_1), Traps.NumTrapTypes - 1)
							#mod = (ev.key == K_RIGHT) - (ev.key == K_LEFT)
							#mod += (ev.key == K_DOWN) * 10 - (ev.key == K_UP) * 10
							#self.curTrap = min(max(self.curTrap + mod,0), Traps.NumTrapTypes - 1)
					elif ev.key == K_r and (ev.mod in [KMOD_LCTRL, KMOD_RCTRL]):
						PTRS["TERRAIN"].randomizeVariations()
					elif ev.key == K_a:
						if self.currState == self.States.PATROL:
							if selectedTile in PTRS["TERRAIN"].patrolPaths:
								numAngles = 8
								
								ang = ((math.atan2(mPos[1] - selectedTile[1], mPos[0] - selectedTile[0])) % (math.pi * 2) + math.pi / float(numAngles)) % (math.pi * 2)
								ang = int(ang / (math.pi / float(numAngles / 2.0)))
								ang = ang * (math.pi / float(numAngles / 2.0))
								PTRS["TERRAIN"].patrolPaths[selectedTile].addTargetAngle(ang)
						elif self.currState == self.States.TRAPS:
							ang = ((math.atan2(mPos[1] - selectedTile[1], mPos[0] - selectedTile[0])) % (math.pi * 2) + math.pi / float(numAngles)) % (math.pi * 2)
							ang = int(ang / (math.pi / float(numAngles / 2.0)))
							ang = ang * (math.pi / float(numAngles / 2.0))
							PTRS["TERRAIN"].addAngleParameter(ang)
					elif ev.key == K_l and (ev.mod == 64 or ev.mod == 4160):
						self.loadLevel(level, [])
					elif ev.key == K_TAB and not mDown:
						if ev.mod == KMOD_LSHIFT:
							self.currState -= 1
						else:
							self.currState += 1
						if self.currState > self.States.ITEMS:
							self.currState = self.States.BLOCK
						elif self.currState < self.States.BLOCK:
							self.currState = self.States.ITEMS
					elif ev.key in [K_DOWN, K_UP, K_LEFT, K_RIGHT, K_LSHIFT]:
						ArrowKeys[ev.key] = True
				elif ev.type == KEYUP:
					if ev.key in ArrowKeys:
						del ArrowKeys[ev.key]
					
				elif ev.type == MOUSEBUTTONDOWN:
					if not mDown:
						mDown = True
						if K_LSHIFT not in ArrowKeys or self.currState not in [self.States.PATROL, self.States.TRAPTRIGGERS]:
							mPos = self.getLocalMousePos(ev.pos, camera)
							selectedTile = mPos
						if self.currState == self.States.BLOCK:
							if K_LSHIFT in ArrowKeys:
								PTRS["TERRAIN"].recursiveSetTile(mPos, (self.curTileset, self.curTile, Terrain.generateVariation(self.curTileset)))
							else:
								PTRS["TERRAIN"].setTile(mPos, (self.curTileset, self.curTile, Terrain.generateVariation(self.curTileset)))
						elif self.currState == self.States.PATROL and ev.button == 1 and K_LSHIFT not in ArrowKeys:
							PTRS["TERRAIN"].addPatrolPathSource(mPos)
						elif self.currState == self.States.TRAPTRIGGERS and K_LSHIFT not in ArrowKeys:
							PTRS["TERRAIN"].addTrapTriggerSource(mPos)
						elif self.currState == self.States.ENEMIES:
							PTRS["TERRAIN"].changeEnemySpawner(mPos, ev.button == 1)
						elif self.currState == self.States.TRAPS:
							PTRS["TERRAIN"].changeTrapType(mPos, self.curTrap, ev.button == 3)
						elif self.currState == self.States.ITEMS:
							PTRS["TERRAIN"].changeItem(mPos, ev.button == 1)
				elif ev.type == MOUSEBUTTONUP:
					if mDown:
						endPos = self.getLocalMousePos(ev.pos, camera)
						if self.currState == self.States.PATROL and selectedTile in PTRS["TERRAIN"].patrolPaths:
							if ev.button == 1:
								PTRS["TERRAIN"].patrolPaths[selectedTile].addDestination(endPos)
							elif ev.button == 3:
								PTRS["TERRAIN"].removePatrolDestination(selectedTile, endPos)
						elif self.currState == self.States.TRAPTRIGGERS and selectedTile in PTRS["TERRAIN"].trapTriggers:
							if ev.button == 1:
								PTRS["TERRAIN"].trapTriggers[selectedTile].addDestination(endPos)
							elif ev.button == 3:
								PTRS["TERRAIN"].removeTrapDestination(selectedTile, endPos)
					mDown = False
				elif ev.type == MOUSEMOTION:
					newPos = self.getLocalMousePos(ev.pos, camera)
					if mDown:
						if self.currState == self.States.BLOCK:
							for square in raytrace(mPos, newPos):
								PTRS["TERRAIN"].setTile(square, (self.curTileset, self.curTile, Terrain.generateVariation(self.curTileset)))
					mPos = newPos
			time = pygame.time.get_ticks()
			if time - lastTime > 40:
				lastTime = time
				
				camera.top += (K_DOWN in ArrowKeys) * 20 - (K_UP in ArrowKeys) * 20
				camera.left += (K_RIGHT in ArrowKeys) * 20 - (K_LEFT in ArrowKeys) * 20
				
				PTRS["EFFECTS"].update()
				
				PTRS["TERRAIN"].drawMe(camera)
				PTRS["UNITS"].drawMe(camera, False)
				PTRS["EFFECTS"].drawMe(camera)
				if mPos[1] < SCREENSIZE[1] / 2 / TILESIZE[1]:
					p = [SCREENSIZE[0] - 60, SCREENSIZE[1] - 23]
				else:
					p = [SCREENSIZE[0] - 60, -5]
				
				surface.blit(camera.getSurface(), (0, 0))
				
				if self.currState == self.States.PATROL or self.currState == self.States.TRAPTRIGGERS:
					pygame.draw.rect(surface, [0, 255, 255], [[selectedTile[0] * TILESIZE[0] - 1 - camera.Left(), 
																										 selectedTile[1] * TILESIZE[1] - 1 - camera.Top()], 
																									[TILESIZE[0] + 2, TILESIZE[1] + 2]], 1)
				if mDown and (self.currState == self.States.PATROL or self.currState == self.States.TRAPTRIGGERS):
					src = [selectedTile[0] * TILESIZE[0] + TILESIZE[0] / 2 - camera.Left(), 
								 selectedTile[1] * TILESIZE[1] + TILESIZE[1] / 2 - camera.Top()]
					dst = [mPos[0] * TILESIZE[0] + TILESIZE[0] / 2 - camera.Left(), mPos[1] * TILESIZE[1] + TILESIZE[1] / 2 - camera.Top()]
					pygame.draw.line(surface, [0, 255, 255], src, dst)
					pygame.draw.rect(surface, [0, 255, 255], ((dst[0] - TILESIZE[0] / 2, dst[1] - TILESIZE[1] / 2), TILESIZE), 1)
				
				self.drawHUD()
				
				pygame.display.update()
				surface.fill([0] * 3)
				camera.getSurface().fill([0] * 3)
				
				
	def backup(self):
		pass
		
	def restore(self):
		pass
		
	def update(self):
		PTRS["BULLETS"].update()
		PTRS["EFFECTS"].update()
		PTRS["UNITS"].update()
		PTRS["TERRAIN"].update()
		
	def drawMe(self, started, cams):
		on = 0
		for c in cams:
			PTRS["TERRAIN"].drawMe(c)
			PTRS["UNITS"].drawMe(c, started)
			PTRS["EFFECTS"].drawMe(c)
			PTRS["BULLETS"].drawMe(surface)
			PTRS["UNITS"].drawHUD(c, started)
			pygame.draw.rect(c.getSurface(), [255] * 3, ((0, 0), (c.Width(), c.Height())), 1)
			surface.blit(c.getSurface(), (400 * on, 0))
			on += 1
		if FOGOFWAR:
			surface.blit(PTRS["FOGOFWAR"], (0, 0))
		
		pygame.display.update()
		surface.fill([0] * 3)
		if FOGOFWAR:
			PTRS["FOGOFWAR"].fill([0] * 3)
		for c in cams:
			c.getSurface().fill([0] * 3)
		
	def playGame(self, levelName):
		surface.fill([0] * 3)
		pygame.display.update()
		gamestate = {"done":False}
		gamestate["done"] = False
		backupFrame = 0
		selected = range(NUMPLAYERS)
		started = False
		self.loadLevel(levelName, selected)
		lastTime = 0
		backupOnRestore = True
		cams = [Camera((800, 600))]
		while not gamestate["done"]:
			for ev in pygame.event.get():
				if ev.type == QUIT:
					sys.exit()
				elif ev.type in [KEYDOWN, KEYUP, MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP]:
					PTRS["KEYS"].handleEvent(ev)
				if ev.type == KEYDOWN:
					if ev.key == getPlayerControls(0, "RESTART") and ev.mod in [KMOD_LCTRL, KMOD_RCTRL]:
						PTRS["FRAME"] = 1
						started = False
						self.loadLevel(levelName, selected)
					elif ev.key == getPlayerControls(0, "BACKUP"):
						someoneStillAlive = False
						someoneDone = False
						for u in PTRS["UNITS"].getPlayers():
							if u.inPortal:
								someoneDone = True
							elif not u.isDead():
								someoneStillAlive = True
						if not someoneStillAlive and someoneDone:
							return True
						PTRS["UNITS"].backup()
						PTRS["TERRAIN"].backup()
						backupFrame = PTRS["FRAME"]
					elif ev.key == getPlayerControls(0, "RESTORE"):
						PTRS["UNITS"].restore()
						PTRS["TERRAIN"].restore()
						started = False
						PTRS["FRAME"] = backupFrame
						for i in range(NUMPLAYERS):
							PTRS["UNITS"].selectUnit(selected[i], i + 1)
						backupOnRestore = True
					elif ev.key == getPlayerControls(0, "QUIT"):
						return "QUIT"
					elif ev.key == getPlayerControls(0, "SWITCH") and started:
						started = False
						for i in range(NUMPLAYERS):
							PTRS["UNITS"].selectUnit(selected[i], i + 1)
							PTRS["UNITS"].getPlayers()[selected[i]].controlled = False
					elif ev.key == getPlayerControls(0, "START") and not started:
						started = True
						PTRS["UNITS"].startBattle(selected)
						if backupOnRestore:
							backupOnRestore = False
							PTRS["UNITS"].backup()
					elif not started and ev.key in [getPlayerControls(1, "UP"), getPlayerControls(1, "DOWN")]:
						unit, number = PTRS["UNITS"].getNextUnit(0, selected[0], ev.key == getPlayerControls(1, "DOWN"))
						if unit is not None and number is not None:
							PTRS["UNITS"].selectUnit(number, 0 + 1)
							selected[0] = number
					elif not started and ev.key in [getPlayerControls(2, "UP"), getPlayerControls(2, "DOWN")] and NUMPLAYERS > 1:
						unit, number = PTRS["UNITS"].getNextUnit(1, selected[1], ev.key == getPlayerControls(2, "DOWN"))
						if unit is not None and number is not None:
							PTRS["UNITS"].selectUnit(number, 1 + 1)
							selected[1] = number
			time = pygame.time.get_ticks()
			if time - lastTime > MINFPS:
				if started:
					lastTime = time
					self.update()
				for i in range(NUMPLAYERS):
					cams[i].setPos(intOf(PTRS["UNITS"].getPlayers()[selected[i]].getPos()))
				self.drawMe(started, cams)
				if started:
					PTRS["FRAME"] += 1
						
	def mainMenu(self):
		levelOn = 1
		_done = False
		while not _done:
			result = self.playGame("L" + str(levelOn) + ".txt")
			if result == "QUIT":
				_done = True
			elif result == True:
				levelOn += 1
					
	def testGame(self):
		surface.fill([0] * 3)
		pygame.display.update()
		
		gamestate = {"done":False}
		gamestate["done"] = False
		
		selected = range(NUMPLAYERS)
		started = False
		#self.loadLevel("L1.txt", [])
		e = PTRS["UNITS"].addEnemyUnit([300, 400], [2, "ARCHER"])
		#e.moveState = "test"
		e.angle = 2
		lastTime = 0
		while not gamestate["done"]:
			for ev in pygame.event.get():
				if ev.type == QUIT:
					sys.exit()
				elif ev.type in [KEYDOWN, KEYUP, MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP]:
					PTRS["KEYS"].handleEvent(ev)
				if ev.type == MOUSEBUTTONDOWN:
					#e.angle = math.atan2(ev.pos[1] - 400, ev.pos[0] - 300)
					#e.moveState = "patrol"
					#e.patrolTarget = Terrain.PatrolPath(["BLAH", str(int(e.pos[0] / TILESIZE[0])),  str(int(e.pos[1] / TILESIZE[1])), "-d",])
																											 
					e.moveState = "investigate"
					e.investigateAngle = math.atan2(1, 0)
					e.investigateTile = [int(ev.pos[0] / TILESIZE[0]), int(ev.pos[1] / TILESIZE[1])]
					e.reachedTarget = False

			time = pygame.time.get_ticks()
			if time - lastTime > 30:
				lastTime = time
				self.update()
					
				self.drawMe(started)
				pygame.draw.line(surface, [255, 0, 0], e.pos, [e.pos[0] + math.cos(e.angle) * 200, e.pos[1] + math.sin(e.angle) * 200])
MG = MainGame()
if "-d" in sys.argv:
	PTRS["DRAWDEBUG"] = True
if "-e" in sys.argv:
	Globals.surface = pygame.display.set_mode(EDITORSCREENSIZE, 0)
	if len(sys.argv) >= 3:
		MG.editor(sys.argv[2])
	else:
		MG.editor("editorFile.txt")
elif "-t" in sys.argv:
	MG.testGame()
else:
	MG.mainMenu()