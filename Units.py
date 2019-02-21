import pygame, os, math, Equipment, Abilities, random, Terrain, Stats, copy, Projectiles, Effects
from Globals import *
from pygame.locals import *

SPEED_MOD_WHILE_ACTIVATED = 1
SPEED_MOD_WHILE_ATTACKING = 1

animationFrames = {"idle":[1, 1,
													 "idle"],
									 "walk":[0, 1, 2, 1,
													 "walk"],
									 "windup":[5, 6, 7,
												"attack"],
									 "attack":[5, 6, 7, 8, 9,"idle"],
									 "stunned":[3, 3, 3, "idle"],
									 "dead":[3,3,3,"dead"]}
									 
stateTimes = {"walk":20, "idle":20, "windup":30, "attack":7, "stunned":30, "dead":5}

def loadCharPic(pic):
	path = os.path.join("Data", "Pics", "Actors", pic + ".PNG")
	frames = 5
	#if "Tank" in pic:
	#	frames = 4
	if not os.path.exists(path):
		print "ERROR, file not found: '" + path + "'"
		if os.path.exists(os.path.join("Data", "Pics", "Actors", "NoChar.PNG")):
			return loadCharPic("NoChar")
	pic = pygame.image.load(path)
	pic.set_colorkey([0, 255, 255])
	width = pic.get_width() / frames
	toRet = []
	for x in xrange(frames):
		toRet += [[]]
		for y in xrange(pic.get_height() / width):
			toRet[x] += [pic.subsurface([x * width, y * width, width, width])]
	
	return toRet

def drawCharPic(surface, pic, pos, frame, angle, team):
	global CHARPICTURES
	if pic in CHARPICTURES:
		picToDraw = CHARPICTURES[pic][frame % 5][frame / 5]
		tempSurf = pygame.Surface((picToDraw.get_width(), picToDraw.get_height()))
		if team == 1:
			tempSurf.fill([0, 255, 0])
		elif team == 2:
			tempSurf.fill([255, 0, 0])
		tempSurf.blit(picToDraw, [0, 0])
		toDraw = pygame.transform.rotate(tempSurf, 180 - angle + 90)
		toDraw.set_colorkey([255, 0, 255])
		pos = [pos[0] - toDraw.get_width() / 2, pos[1] - toDraw.get_height() / 2]
		surface.blit(toDraw, pos)
	else:
		CHARPICTURES[pic] = loadCharPic(pic)
		drawCharPic(surface, pic, pos, frame, angle, team)
		
class UnitStruct:
	def __init__(self):
		self.enemyUnits = []
		self.alliedUnits = []#ImmobileUnit([400, 299], 1)]

		self.enemyBackup = []		
		self.alliedBackup = []	
		
		self.unitsDone = []
		self.backupUnitsDone = []
		
	def unitExited(self, unit):
		self.unitsDone += [unit]
		
	def selectUnit(self, number, selectedBy):
		for a in self.alliedUnits:
			if a.selected == selectedBy:
				a.selected = 0
		self.alliedUnits[number].selected = selectedBy

	def startBattle(self, selected):
		for i in range(len(selected)):
			self.alliedUnits[selected[i]].controlled = i + 1
			self.alliedUnits[selected[i]].controller = i + 1
			self.alliedUnits[selected[i]].selected = False
			
	def clear(self):
		self.unitsDone = []
		self.backupUnitsDone = []
		
		while len(self.alliedUnits):
			del self.alliedUnits[0]
		while len(self.enemyUnits):
			del self.enemyUnits[0]
			
		while len(self.alliedBackup):
			del self.alliedBackup[0]
		while len(self.enemyBackup):
			del self.enemyBackup[0]
		
	def reload(self):
		self.clear()
		for pl in PTRS["TERRAIN"].players:
			self.addPlayerUnit(pl)
		for i in PTRS["TERRAIN"].enemies:
			self.addEnemyUnit([i[0] * TILESIZE[0] + TILESIZE[0] / 2, i[1] * TILESIZE[1] + TILESIZE[1] / 2], PTRS["TERRAIN"].enemies[i])
		
	def getNextUnit(self, player, curr, reverse = False):
		list = range(curr + 1, len(self.alliedUnits)) + range(0, curr)
		if reverse:
			list = reversed(list)
		for i in list:
			if self.alliedUnits[i].isSelectable(player + 1):
				return self.alliedUnits[i], i
		return None, None

	def backup(self):
		self.enemyBackup = []
		self.alliedBackup = []
		self.backupUnitsDone = [u for u in self.unitsDone]
		for e in self.enemyUnits:
			e.backup()
			new = copy.deepcopy(e)
			self.enemyBackup += [new]
		for a in self.alliedUnits:
			a.backup()
			new = copy.deepcopy(a)
			new.keyRecorder = a.keyRecorder
			self.alliedBackup += [new]
			
	def restore(self):
		self.enemyUnits = []
		self.unitsDone = [u for u in self.backupUnitsDone]
		for e in self.enemyBackup:
			new = copy.deepcopy(e)
			new.restore(e)
			self.enemyUnits += [new]
		oldUnits = self.alliedUnits
		self.alliedUnits = []
		for a in self.alliedBackup:
			new = copy.deepcopy(a)
			new.restore(a)
			self.alliedUnits += [new]
		
	def getFinishedUnits(self):
		return self.unitsDone
		
	def update(self):
		for unit in self.enemyUnits + self.alliedUnits:
			unit.update()
		"""i = 0
		while i < len(self.enemyUnits):
			if self.enemyUnits[i].readyToDelete():
				del self.enemyUnits[i]
			else:
				i += 1
		i = 0
		while i < len(self.alliedUnits):
			if self.alliedUnits[i].readyToDelete():
				del self.alliedUnits[i]
			else:
				i += 1"""
	
	def getTargets(self, team, hitsAllies, hitsEnemies):
		unitList = []
		if (team == 1):
			if hitsAllies:
				unitList += PTRS["UNITS"].getPlayers()
			if hitsEnemies:
				unitList += PTRS["UNITS"].getEnemyUnits()
		else:
			if hitsEnemies:
				unitList += PTRS["UNITS"].getPlayers()
			if hitsAllies:
				unitList += PTRS["UNITS"].getEnemyUnits()
		return unitList
		
	def addEnemyUnit(self, pos, type):
		if type[1].upper() == "CIVILIAN":
			e = EnemyCivilian(pos, 1)
		elif type == "ARCHER":
			e = EnemyUnit(pos, 1)
		else:
			e = EnemyUnit(pos, 1)
		if e != None:
			self.enemyUnits += [e]
		return e
			
	def addPlayerUnit(self, unit):
		newUnit = None
		if unit.upper() in playerUnitMap:
			self.alliedUnits += [playerUnitMap[unit.upper()]([0, 0], 1)]
			
	def getPlayers(self):
		return self.alliedUnits
		
	def getEnemyUnits(self):
		return self.enemyUnits
		
	def drawMe(self, camera, atStart):
		for unit in self.enemyUnits:
			unit.drawMe(camera, atStart)
		on = 1
		for unit in self.alliedUnits:
			if atStart:
				unit.drawMe(camera, False)
			else:
				unit.drawMe(camera, on)
			on += 1
			
	def drawHUD(self, camera, atStart):
		for unit in self.alliedUnits:
			unit.drawHUD(camera, atStart)
			
class RNG(object): #Random Number Generator
	def __init__(self):
		self.randSeed = random.random()
		self.backupSeed = self.randSeed
	
	def primeRNG(self):
		random.seed(self.randSeed)
		self.randSeed = random.random()
	
	def uniform(self, start, end):
		self.primeRNG()
		return random.uniform(start, end)
	
	def randint(self, start, end):
		self.primeRNG()
		return random.randint(start, end)
		
	def random(self):
		self.primeRNG()
		return random.random()
	
	def randChoice(self, list):
		self.primeRNG()
		return random.choice(list)
		
	def backup(self):
		#self.randSeed = random.random()
		self.backupSeed = self.randSeed
		#if self.team == 2:
		#	print "backup: ", self.backupSeed
		
	def restore(self, previousUnit):
		#if self.team == 2:
		#	print "restore: ", previousUnit.backupSeed
		self.randSeed = previousUnit.backupSeed
		#self.backupSeed = self.randSeed
	
class Unit(RNG):
	def __init__(self, startPos, level):
		super(Unit, self).__init__()
		self.pos = [startPos[0], startPos[1]]
		self.startPos = [startPos[0], startPos[1]]
		self.lastPos = [startPos[0], startPos[1]]
		self.speed = [0, 0]
		self.onGround = False
		self.level = level
		self.logicTickIn = 3
		self.angle = math.pi / 2.0 * 3
		self.angleFacing = self.angle
		self.frame = 0
		self.attackCooldown = 0
		self.currState = "idle"
		self.size = 10
		self.maxHealth = 2
		self.health = self.maxHealth
		self.range = 5
		self.stunResistance = 0.0
		self.hitFrames = [3]
		self.attacked = False
		self.abilList = []#[Abilities.ArcAttackAbility()]
		self.attackCallback = None
		self.team = 2
		self.picture = "Player1"
		self.frameRate = 1
		self.knockback = [0, 0]
		self.animationFrames = []
		self.setState(self.currState)
		self.stats = {}
		self.attackBonuses = {}
		self.rageTable = {}
		self.selected = False
		self.damageAngle = 0
		self.itemHeld = None
		
	def backup(self):
		super(Unit, self).backup()
		self.itemHeldBackup = self.itemHeld
		
	def restore(self, previousUnit):
		super(Unit, self).restore(previousUnit)
		self.itemHeld = previousUnit.itemHeldBackup
		
	def getItemHeld(self):
		return self.itemHeld
		
	def isDead(self):
		return self.health <= 0 and (self.currState != "attack" or self.attacked)
		
	def setAttackBonuses(self, bonusDict):
		for k in bonusDict:
			self.attackBonuses[k] = bonusDict[k]
		
	def setStats(self, statDict):
		for key in statDict:
			self.stats[key] = statDict[key]
			
	def getBounty(self):
		return self.getStat("bounty")
		
	def getListenRange(self):
		return self.abilList[0].Range
		
	def getAbilRange(self):
		return self.abilList[0].Range
	
	def getSightRange(self):
		return 0
		
	def getSightArc(self):
		return 0
		
	def unitInSightArc(self, unit):
		ang = math.atan2(self.pos[1] - unit.getPos()[1], self.pos[0] - unit.getPos()[0])
		angDiff = ang + math.pi - (self.angleFacing % (math.pi * 2))
		if math.fabs(angDiff) < self.getSightArc() or math.fabs(angDiff) > math.pi * 2 - self.getSightArc():
			return True
		return False
		
	def canSeeUnit(self, unit):
		if dist(unit.getPos(), self.getPos()) <= self.getListenRange() or \
			(dist(unit.getPos(), self.getPos()) <= self.getSightRange() and self.unitInSightArc(unit)):
			for square in raytrace([int(self.getPos()[0] / TILESIZE[0]), int(self.getPos()[1] / TILESIZE[1])], 
							 [int(unit.getPos()[0] / TILESIZE[0]), int(unit.getPos()[1] / TILESIZE[1])]):
				if not PTRS["TERRAIN"].canSeeThrough(intOf(square)):
					return False
			return True
		return False
			
	def getAttack(self, type):
		toRet = self.getStat("attack")
		if type in self.attackBonuses:
			toRet += self.attackBonuses[type]
		return toRet
		
	def getStat(self, stat):
		if stat in self.stats:
			return self.stats[stat]
		return Stats.baseStats[stat]
						
	def addKnockback(self, baseKnockback, angle, kAttack, stunAmount, forceKnockback = False):
		kOffset = float(kAttack - 500)
		kDefense = self.getStat("knockbackDefense")
		kMod = (1 - (kDefense - kOffset - 250) / kOffset)
		if self.stun(stunAmount * kMod) or forceKnockback:
			amount = min(max(baseKnockback * kMod, 0), baseKnockback)
			knockVals = [math.cos(angle) * amount, math.sin(angle) * amount]
			for i in [0, 1]:
				if (signOf(self.knockback[i]) != signOf(knockVals[i])):
					self.knockback[i] += knockVals[i]
				else:
					if math.fabs(self.knockback[i]) < math.fabs(knockVals[i]):
						self.knockback[i] = knockVals[i]
			
	def addDamage(self, amount, source):
		if source:
			self.damageAngle = math.atan2(source.getPos()[1] - self.getPos()[1], source.getPos()[0] - self.getPos()[0])
		if self.itemHeld == itemTypes.DEFEND:
			self.itemHeld = None
		else:
			self.health -= amount
		
	def readyToDelete(self):
		return self.health <= 0
		
	def resetPosition(self):
		self.pos = [self.startPos[0], self.startPos[1]]
		self.speed = [0, 0]
		
	def update(self):
		if self.isDead():
			if self.currState is not "dead":
				self.setState("dead")
			return
		self.logicTickIn -= 1
		if self.logicTickIn <= 0:
			self.logicTick()
			self.logicTickIn = 3
		
		toDel = []
		for k in self.rageTable:
			self.rageTable[k] -= 0.03
			if self.rageTable[k] < 0:
				toDel += [k]
				
		for k in toDel:
			del self.rageTable[k]
		
		self.move()
		for abil in self.abilList:
			if abil is not None:
				abil.update()
		if self.health < self.maxHealth and self.itemHeld == itemTypes.HEALTH:
			self.itemHeld = None
			self.health += 1
		
	def move(self):
		self.lastPos = [self.pos[0], self.pos[1]]
		self.attackCooldown -= (self.attackCooldown > 0)
		self.frame += self.frameRate
			
		if len(self.hitFrames) > 0 and self.frame >= self.hitFrames[0] and not self.attacked:
			self.abilList[0].useCallback(self)
			del self.hitFrames[0]
			if len(self.hitFrames) <= 0:
				self.attacked = True
			
		if (self.frame >= len(self.animationFrames) - 1):
			self.setState(self.animationFrames[len(self.animationFrames) - 1])
	
		speed = [self.knockback[0], self.knockback[1]]
		#if math.fabs(self.knockback[0]) == 0 and math.fabs(self.knockback[1]) == 0:
		if (self.currState is not "stunned"):
			speed[0] += self.speed[0]
			speed[1] += self.speed[1]

		if PTRS["TERRAIN"].canMoveThrough(posToCoords([self.pos[0] + speed[0], self.pos[1]]), self):
			self.pos[0] += speed[0]
		else:
			if speed[0] > 0:
				self.pos[0] = int(self.pos[0] / 20 + 1) * 20 - 0.001
			else:
				self.pos[0] = int(self.pos[0] / 20) * 20 + 0.001
		if PTRS["TERRAIN"].canMoveThrough(posToCoords([self.pos[0], self.pos[1] + speed[1]]), self):
			self.pos[1] += speed[1]
		else:
			if speed[1] > 0:
				self.pos[1] = int(self.pos[1] / 20 + 1) * 20 - 0.001
			else:
				self.pos[1] = int(self.pos[1] / 20) * 20 + 0.001
			
		if self.lastPos[0] != self.pos[0] or self.lastPos[1] != self.pos[1]:
			PTRS["TERRAIN"].notifyUnitMovement(self, self.lastPos, self.pos)
		if int(self.lastPos[0] / TILESIZE[0]) != int(self.pos[0] / TILESIZE[0]) or \
			 int(self.lastPos[1] / TILESIZE[1]) != int(self.pos[1] / TILESIZE[1]):
			item = PTRS["TERRAIN"].pickUpItem(self.pos, self.itemHeld)
			if item != None:
				self.itemHeld = item
			
		for i in [0, 1]:
			self.knockback[i] *= 0.96
			if math.fabs(self.knockback[i]) <= 0.1:
				self.knockback[i] = 0
			if math.fabs(self.knockback[i]) <= 1 and self.currState == "attack":
				self.knockback[i] = 0
				
		if self.currState == "walk" and self.lastPos[0] == self.pos[0] and self.lastPos[1] == self.pos[1]:
			self.setState("idle")
		elif self.currState == "idle" and (self.lastPos[0] != self.pos[0] or self.lastPos[1] != self.pos[1]):
			self.setState("walk")
			
	def logicTick(self):
		pass
		
	def isSpawned(self):
		return True
		
	def setState(self, stateName, duration=-1, animationFramesToUse = []):
		self.attacked = True
		if (stateName == "attack"):
			self.attacked = False
			
		if animationFramesToUse == []:
			self.animationFrames = animationFrames[stateName]
		else:
			self.animationFrames = animationFramesToUse
		if (duration == -1):
			duration = stateTimes[stateName]
		self.currState = stateName
		self.frameRate = (len(self.animationFrames) - 1) / float(duration)
		self.frame = 0
		
	def attack(self, abil):
		if self.currState == "idle" or self.currState == "walk":
			abil.use(self)
		
	def getPos(self):
		return [self.pos[0], self.pos[1]]
	
	def drawMe(self, camera, atStart):
		pos = intOf([self.pos[0] - camera.Left(), self.pos[1] - camera.Top()])
		size = int(self.size)
		if self.selected == 1:
			pygame.draw.circle(camera.getSurface(), [255, 0, 0], pos, size, 3)
		elif self.selected == 2:
			pygame.draw.circle(camera.getSurface(), [0, 0, 255], pos, size, 3)
		drawCharPic(camera.getSurface(), self.picture, pos, int(self.animationFrames[int(self.frame)]), int(self.angleFacing * 180 / math.pi), self.team)
		if self.itemHeld != None:
			Terrain.drawItem(camera, [self.pos[0], self.pos[1] - self.size], self.itemHeld)
	
	def drawHUD(self, camera, atStart):
		if self.controlled or self.selected == 1:
			for i in range(self.maxHealth):
				xWiggle = 1
				yWiggle = 2
				pos = [xWiggle + 2 + 10 * i, yWiggle + 2]
				icon = 7
				if self.health <= i:
					icon = 8
					xWiggle = 0
					yWiggle = 0
					
				pos[0] += int(math.cos((PTRS["FRAME"] + i * 11 % 23) * math.pi / 10.0) * xWiggle)
				pos[1] += int(math.sin((PTRS["FRAME"] + i * 11 % 23) * math.pi / 40.0) * yWiggle)
				Terrain.drawItem(camera, pos, icon, True)
		
class KeyRecorder:
	def __init__(self):
		self.pressed = {}
		self.mousePos = {}
		self.mouseButtons = {}
		self.lastFrame = 0
		
	def isActivated(self):
		return PTRS["FRAME"] < self.lastFrame
		
	def getMousePos(self):
		if PTRS["FRAME"] in self.mousePos:
			return self.mousePos[PTRS["FRAME"]]
		if self.lastFrame in self.mousePos:
			return self.mousePos[self.lastFrame]
		return [400, -100000]
		
	def getMouseButtons(self):
		if PTRS["FRAME"] in self.mouseButtons:
			return self.mouseButtons[PTRS["FRAME"]]
		return []
		
	def keyPressed(self, key):
		if PTRS["FRAME"] in self.pressed:
			return key in self.pressed[PTRS["FRAME"]]
		return False
		
	def getKeys(self):
		if PTRS["FRAME"] in self.pressed:
			return self.pressed[PTRS["FRAME"]]
		return []
	
	def setCurrFrame(self, keys):
		self.lastFrame = max(PTRS["FRAME"], self.lastFrame)
		self.mouseButtons[PTRS["FRAME"]] =  copy.deepcopy(keys.getMouseButtons())
		self.mousePos[PTRS["FRAME"]] = copy.deepcopy(keys.getMousePos())
		self.pressed[PTRS["FRAME"]] = copy.deepcopy(keys.getKeys())
		
class PlayerUnit(Unit):
	def __init__(self, startPos, level):
		Unit.__init__(self, startPos, level)
		self.frame = 0
		self.team = 1
		self.maxHealth = 3
		self.health = self.maxHealth
		self.picture = "Knight"
		self.abilList = [Abilities.SwordsmanAbil()]#[Abilities.PlayerArcAttackAbility()]
		self.abilSelected = 1
		self.stunResistance = 0.5
		self.keyRecorder = KeyRecorder()
		self.controlled = False
		self.controller = 0
		self.spawned = False
		self.inPortal = False
		self.respawnTimer = 0
		
	def isSpawned(self):
		return self.spawned
		
	def getSightRange(self):
		return 350
		
	def getSightArc(self):
		return math.pi * 0.2
		
	def backup(self):
		super(PlayerUnit, self).backup()
		
	def restore(self, previousUnit):
		if self.controlled:
			previousUnit.keyRecorder.setCurrFrame(PTRS["KEYS"])
		super(PlayerUnit, self).restore(previousUnit)
		self.controlled = False
		self.keyRecorder = previousUnit.keyRecorder
		self.controller = previousUnit.controller
		
	def setAbils(self, abils):
		self.abilList = [self.abilList[0]] + abils
		
	def findTargetForAbil(self):
		validTargets = []
		for unit in PTRS["UNITS"].getEnemyUnits():
			if not unit.isDead() and unit.isSpawned() and dist(self.pos, unit.pos) < self.getAbilRange() and self.canSeeUnit(unit):
				validTargets += [unit]
		if validTargets:
			return self.randChoice(validTargets)
		return None
		
	def isSelectable(self, player):
		return not self.isDead() and not self.inPortal and self.selected in [player, 0]
				
	def getKeysObject(self):
		if self.controlled:
			keys = PTRS["KEYS"]
		else:
			keys = self.keyRecorder
		return keys
		
	def move(self):
		if self.isDead() or self.inPortal:
			return
			
		if self.controlled:
			keys = PTRS["KEYS"]
			self.keyRecorder.setCurrFrame(keys)
		else:
			keys = self.keyRecorder
			
		if keys != None:
			if not self.spawned and self.respawnTimer <= 0:
				if self.controller:#keys.keyPressed(getPlayerControls(self.controller, "ACTIVATE")):
					self.spawned = True
					self.pos = PTRS["TERRAIN"].getSpawnPos()
				else:
					return
			elif self.respawnTimer > 0:
				self.pos = PTRS["TERRAIN"].getSpawnPos()
				self.respawnTimer -= 1
				return
			self.speed[1] = 0
			self.speed[0] = 0
			
			#if keys.keyPressed(K_1):
			#	self.abilSelected = 1
			#elif keys.keyPressed(K_2):
			#	self.abilSelected = 2
			
			#if (1 in keys.buttonsDown() and self.currState in ["idle", "walk"]):
			#	self.attack(self.abilList[0])
			#elif (3 in keys.buttonsDown() and self.currState in ["idle", "walk"]):
			#	if self.abilList[self.abilSelected] is not None and 1 <= self.abilSelected < len(self.abilList):
			#		self.attack(self.abilList[self.abilSelected])
			
			speedMod = 1
			if (self.currState in ["idle", "walk"]):
				if keys.keyPressed(getPlayerControls(self.controller, "ACTIVATE")):
					targ = self.findTargetForAbil()
					if targ:
						self.target = targ
						self.moveState = "alerted"
						self.abilList[0].use(self)
						speedMod = SPEED_MOD_WHILE_ATTACKING
					else:
						speedMod = SPEED_MOD_WHILE_ACTIVATED
			
			if SPEED_MOD_WHILE_ATTACKING != 0 or (self.currState in ["idle", "walk"]):
				if not (self.currState in ["idle", "walk"]):
					speedMod = SPEED_MOD_WHILE_ATTACKING
				if keys.keyPressed(getPlayerControls(self.controller, "UP")):
					self.speed[1] += -self.getMaxSpeed() * speedMod
				if keys.keyPressed(getPlayerControls(self.controller, "DOWN")):
					self.speed[1] += self.getMaxSpeed() * speedMod
			
				if keys.keyPressed(getPlayerControls(self.controller, "LEFT")):
					self.speed[0] += -self.getMaxSpeed() * speedMod
				if keys.keyPressed(getPlayerControls(self.controller, "RIGHT")):
					self.speed[0] += self.getMaxSpeed() * speedMod
			#if keys.getMouseButtons():
			#	ang = math.atan2(keys.getMousePos()[1] - self.pos[1], keys.getMousePos()[0] - self.pos[0])
			#	PTRS["BULLETS"].add(Projectiles.Bullet(self.pos, [self.pos[0] + math.cos(ang) * 50, self.pos[1] + math.sin(ang) * 50]))
			if self.currState == "attack":
				self.angle = math.atan2(self.target.getPos()[1] - self.pos[1], self.target.getPos()[0] - self.pos[0])
			elif self.speed[1] != 0 or self.speed[0] != 0:
				self.angle = math.atan2(self.speed[1], self.speed[0])
		Unit.move(self)
		if Terrain.isInactiveSpawner(PTRS["TERRAIN"].getAtPos(self.pos)):
			if (int(self.lastPos[0] / TILESIZE[0]) != int(self.pos[0] / TILESIZE[0]) or \
					int(self.lastPos[1] / TILESIZE[1]) != int(self.pos[1] / TILESIZE[1])):
				PTRS["TERRAIN"].setSpawner(self.pos)
		if Terrain.isExitPortal(PTRS["TERRAIN"].getAtPos(self.pos)):
			self.inPortal = True
			PTRS["UNITS"].unitExited(self)
		self.angleFacing = self.angle
		
		if keys.keyPressed(getPlayerControls(self.controller, "RESTORE")):
			if Terrain.isSpawner(PTRS["TERRAIN"].getAtPos(self.pos)):
				self.spawned = False
				self.respawnTimer = RESPAWNTIME
				self.controlled = False
				self.controller = 0
		
	def getMaxSpeed(self):
		toRet = MAXRUNSPEED
		return toRet
		
	def drawMe(self, camera, atStart):
		if self.inPortal:
			return
				
		if atStart:
			if self.keyRecorder.isActivated():
				pygame.draw.circle(camera.getSurface(), [0, 255, 0], intOf([self.pos[0] - camera.Left(), self.pos[1] - camera.Top()]), int(self.size + 2))
				
		if not atStart and self.controlled:
			if self.respawnTimer > 1:
				pct = self.respawnTimer / float(RESPAWNTIME)
				pygame.draw.circle(camera.getSurface(), [255, 255, 0], 
					intOf([self.pos[0] - camera.Left(), self.pos[1] - camera.Top()]), 
					int(50 * pct), 1)
			else:
				keys = self.getKeysObject()
				size = self.getAbilRange()
				if keys.keyPressed(getPlayerControls(self.controller, "ACTIVATE")) and size > self.size - 5:
					pct = self.abilList[0].getCooldownPercent()
					pos = intOf([self.pos[0] - camera.Left(), self.pos[1] - camera.Top()])
					if self.abilList[0].getCooldownPercent != 1:
						pygame.draw.circle(camera.getSurface(), [255, 0, 0], pos, int(size), 1)
						pygame.draw.circle(camera.getSurface(), [255, 255, 0], pos, max(int(size * pct), 1), 1)
					else:
						pygame.draw.circle(camera.getSurface(), [255, 255, 0], pos, int(size), 1)
		
		if self.spawned:
			Unit.drawMe(self, camera, atStart)
		elif atStart:
			spawnP = PTRS["TERRAIN"].getSpawnPos()
			offsetMap = [[-1, -1], [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0]]
			self.pos = [spawnP[0] + offsetMap[atStart % len(offsetMap)][0] * 20, spawnP[1] + offsetMap[atStart % len(offsetMap)][1] * 20]
			Unit.drawMe(self, camera, atStart)

class PlayerArcher(PlayerUnit):
	def __init__(self, startPos, level):
		PlayerUnit.__init__(self, startPos, level)
		self.picture = "Archer"
		self.abilList = [Abilities.ArcherShotAbil()]#[Abilities.PlayerArcAttackAbility()]
		
class EnemyUnit(Unit):
	enemyType = "basic"
	def __init__(self, startPos, level):
		Unit.__init__(self, startPos, level)
		self.maxHealth = self.getStat("health")
		self.health = self.maxHealth
		self.frame = 0
		self.target = None
		self.abilList = [Abilities.ArcherShotAbil()]
		self.nextDistanceCheck = 0
		self.team = 2
		self.stunResistance = 0.0
		self.picture = "Archer"
		self.offset = 0
		self.patrolTarget = PTRS["TERRAIN"].getPatrolPathAtPos(self.pos)
		if self.patrolTarget and self.patrolTarget.getNumDestinations():
			self.patrolDestination = self.randint(0, self.patrolTarget.getNumDestinations() - 1)
		else:
			self.patrolDestination = 0
		self.scanTime = 1
		self.scanDeltaTime = 1
		self.scanDeltaAng = 0
		self.scanType = "Passive"
		self.scanAngle = 0
		self.angleFacing = self.angle
		self.moveState = "patrol"
		self.alerted = 0
		self.reachedTarget = False
		self.deathInvestigated = False
		self.moveTarget = None
		self.walkList = []
		self.investigateAngle = 0
		self.itemHeld = 0
	
	def getStat(self, stat):
		if stat in self.stats and self.stats[stat][0] == self.level:
			return self.stats[stat][1]
		if self.enemyType in Stats.enemyStats and stat in Stats.enemyStats[self.enemyType]:
			s = Stats.enemyStats[self.enemyType][stat]
		else:
			s = Stats.baseEnemyStats[stat]
		self.stats[stat] = [self.level, (s[0] + (s[1]) * self.level) * (1 + self.uniform(-s[2], s[2]))]
		return self.stats[stat][1]
		
	def getPreferredRange(self):
		return self.getStat("preferredRange")
		
	def getListenRange(self):
		if self.alerted:
			return self.getStat("alertedListenRad")
		return self.getStat("listenRad")
	
	def getSightRange(self):
		if self.alerted:
			return self.getStat("alertedSightRad")
		return self.getStat("sightRad")
		
	def getSightArc(self):
		if self.alerted:
			return self.getStat("alertedSightArc")
		return self.getStat("sightArc")
		
	def pickTarget(self):
		self.nextDistanceCheck = 10
		highPri = 1
		closest = None
		for unit in PTRS["UNITS"].getTargets(self.team, False, True):
			dMod = max(2000 - dist(unit.pos, self.pos), 0) / 2000.0 #1 at close range, 0 at 500 or more
			pri = 0
			if unit.health > 0 and self.canSeeUnit(unit):
				pri = 50 + dMod
				
			#if unit in self.rageTable:
			#	pri += self.rageTable[unit] / (self.maxHealth * 5.0) #0 to 2 (assuming rageMult of 10)
			#pri += d
			#pri += self.uniform(0, 0.1)

			if (closest == None or pri > highPri) and pri > 0:
				closest = unit
				highPri = pri
		if closest != None:
			self.target = closest
			self.moveState = "alerted"
			
	def activateConditionCheck(self):
		if dist(self.pos, self.target.getPos()) <= self.getStat("activateRange"):
			#targAng = math.atan2(self.target.getPos()[1] - self.pos[1], self.target.getPos()[0] - self.pos[0]) % (math.pi * 2)
			#selfAng = self.angleFacing % (math.pi * 2)
			#angDiff = getAngDiff(selfAng, targAng)
			#if math.fabs(angDiff) < self.getSightArc():
			#unitInSightArc
			if self.unitInSightArc(self.target):
				return True
		return False
		
	def getMoveSpeed(self):
		if self.alerted:
			return self.getStat("runSpeed")
		return self.getStat("walkSpeed")
		
	def activate(self):
		self.abilList[0].use(self)

	def updateAngleFacing(self):
		targAng = self.angle % (math.pi * 2)
		selfAng = self.angleFacing % (math.pi * 2)
		angDiff = getAngDiff(selfAng, targAng)
		
		if self.alerted:
			rotationSpeed = math.pi / 32.0
		elif math.fabs(angDiff) > math.pi / 3.0:
			rotationSpeed = math.pi / 32.0
		else:
			rotationSpeed = math.pi / 64.0
			
		if math.fabs(angDiff) < rotationSpeed:
			self.angleFacing = targAng
		else:
			self.angleFacing = (self.angleFacing + max(min(angDiff, rotationSpeed), -rotationSpeed)) % (math.pi * 2)

	def getScanAngle(self):
		if self.patrolTarget:
			scanAngs = self.patrolTarget.getScanAngles()
			if scanAngs:
				toRet = self.randChoice(scanAngs)
				if toRet is not None:
					return toRet
		return self.scanAngle
			
	def scanMove(self):
		self.moveState == "scan"
		self.speed = [0, 0]
		if self.scanTime <= 0:#When we just reached the spot
			if self.patrolTarget:
				self.scanTime = self.patrolTarget.getScanTime()
			else:
				self.scanTime = DEFAULTSCANTIME
			self.scanAngle = self.angle
			self.startAng = self.angle
			self.targAng = self.angle
			self.scanDeltaTime = 1
			self.scanDeltaAng = 0
			
		self.scanTime -= self.scanTime > 0
		if self.alerted:
			self.scanTime -= self.scanTime > 0
		
		#While we're still scanning
		self.scanDeltaTime -= 1
		#self.angle += self.scanDeltaAng
		if self.scanDeltaTime <= 0:
			self.startAng = self.angle
			if self.scanType == "Stop":
				self.scanDeltaTime = self.randint(10, 15)
				self.targAng = self.angle
				self.scanType = "Passive"
			elif self.scanType == "Passive":
				if not self.alerted:
					self.scanType = "Stop"
					self.scanDeltaTime = self.randint(30, 40)
					self.targAng = self.getScanAngle() + math.pi / 4 * (self.random() - 0.5)
				else:
					self.scanDeltaTime = self.randint(20, 25)
					self.targAng = self.getScanAngle() + math.pi / 2 * (self.random() - 0.5)
			elif self.scanType == "Active":
				self.scanDeltaTime = self.randint(20, 25)
				self.targAng = self.getScanAngle() + math.pi / 2 * (self.random() - 0.5)
			self.angle = self.targAng
			#self.scanDeltaAng = (self.targAng - self.angle) / (self.scanDeltaTime)
		
		if self.scanTime <= 0:#When the counter has run down.
			if self.patrolTarget and self.patrolTarget.getNumDestinations():
				self.patrolDestination = self.randint(0, self.patrolTarget.getNumDestinations() - 1)
				self.moveState = "patrol"
			else:
				self.scanTime = 5000
		
	def patrolMove(self):
		if self.patrolTarget == None:
			self.moveState = "scan"
		else:
			moveTarg = (self.patrolTarget.getDestination(self.patrolDestination)[0] * TILESIZE[0] + TILESIZE[0] / 2, 
									self.patrolTarget.getDestination(self.patrolDestination)[1] * TILESIZE[1] + TILESIZE[1] / 2)
			if (math.fabs(self.pos[0] - moveTarg[0]) <= 1 and
					math.fabs(self.pos[1] - moveTarg[1]) <= 1 ):
				self.moveState = "scan"
				if self.patrolTarget != None:
					pos = (self.patrolTarget.getDestination(self.patrolDestination)[0], self.patrolTarget.getDestination(self.patrolDestination)[1])
				else:
					pos = (int(self.pos[0] / TILESIZE[0]), int(self.pos[1] / TILESIZE[1]))
				if pos in PTRS["TERRAIN"].patrolPaths:
					self.patrolTarget = PTRS["TERRAIN"].patrolPaths[pos]
					if self.patrolTarget:
						if self.patrolTarget.getNumDestinations():
							self.patrolDestination = self.randint(0, self.patrolTarget.getNumDestinations() - 1)
						self.patrolDestination = None
					self.scanTime = 0
				else:
					self.patrolTarget = None
			else:
				self.moveTowardsTile(self.patrolTarget.getDestination(self.patrolDestination))
		
	def alertedMove(self):
		if (self.target != None):
			self.angle = math.atan2(self.target.pos[1] - self.pos[1], self.target.pos[0] - self.pos[0])
		else:
			pass
			
	def moveTowards(self, pos, ignoreAngle = False):
		sp = self.getMoveSpeed()
		if not ignoreAngle:
			targAng = self.angle % (math.pi * 2)
			selfAng = self.angleFacing % (math.pi * 2)
			angDiff = getAngDiff(selfAng, targAng)
			moveAng = math.pi / 3.0
			if math.fabs(angDiff) > moveAng:
				sp *= 0.3
		d = dist(self.pos, pos)
		ang = math.atan2(pos[1] - self.pos[1], pos[0] - self.pos[0])
		if d < sp:
			self.speed = [math.cos(ang) * d, math.sin(ang) * d]
		else:
			self.speed = [math.cos(ang) * sp, math.sin(ang) * sp]
			self.angle = ang
		
	def moveTowardsTile(self, coords):
		oldMode = False
		
		#moveTarg = (self.patrolTarget.getDestination(self.patrolDestination)[0] * TILESIZE[0] + TILESIZE[0] / 2, 
		#							self.patrolTarget.getDestination(self.patrolDestination)[1] * TILESIZE[1] + TILESIZE[1] / 2)
		#	if (math.fabs(self.pos[0] - moveTarg[0]) <= 1 and 
		#			math.fabs(self.pos[1] - moveTarg[1]) <= 1 ):
		
		if not oldMode:
			selfPos = intOf([self.pos[0] / TILESIZE[0], self.pos[1] / TILESIZE[1]])
			
			if self.moveTarget != (int(coords[0]), int(coords[1])):
				self.moveTarget = (int(coords[0]), int(coords[1]))
				self.walkList = PTRS["TERRAIN"].getShortestPath(selfPos, self.moveTarget, 0, self, self.alerted)
			elif (not self.walkList):
				pass
				#print "This is the case"
			elif self.moveTarget == (int(coords[0]), int(coords[1])):
				checkDist = 1
				if len(self.walkList) > 1:
					checkDist = self.getMoveSpeed()
				moveTarg = (self.walkList[len(self.walkList) - 1][0] * TILESIZE[0] + TILESIZE[0] / 2, 
										self.walkList[len(self.walkList) - 1][1] * TILESIZE[1] + TILESIZE[1] / 2)
				if math.fabs(moveTarg[0] - self.pos[0]) <= checkDist and math.fabs(moveTarg[1] - self.pos[1]) <= checkDist:
					del self.walkList[len(self.walkList) - 1]
				if self.walkList:
					self.moveTowards(moveTarg)
		else:
			pos = [int(coords[0]) * TILESIZE[0] + TILESIZE[0] / 2, int(coords[1]) * TILESIZE[1] + TILESIZE[1] / 2]
			self.moveTowards(pos)
		
	def moveTowardsTarget(self, unit):
		self.moveTarget = None
		self.walkList = []
		self.moveTowards(unit.getPos())
			
	def InvestigateMove(self):	
		if not self.reachedTarget:
			self.moveTowardsTile(self.investigateTile)
			if math.fabs(self.pos[0] / TILESIZE[0] - self.investigateTile[0]) + math.fabs(self.pos[1] / TILESIZE[1] - self.investigateTile[1]) < 1:
				self.reachedTarget = True
				self.angle = self.uniform(0, math.pi * 2)
				self.scanTime = 106
				self.speed = [0, 0]
		else:
			self.scanTime -= 1
			if self.scanTime % 15 == 0:
				if self.investigateAngle:
					self.angle = self.investigateAngle + self.uniform(-math.pi / 3, math.pi / 3)
				else:
					self.angle = self.uniform(0, math.pi * 2)
			if self.scanTime <= 0:
				self.moveState = "patrol"
			return
				
	def move(self):
		Unit.move(self)
		if self.moveState == "patrol":
			self.patrolMove()
		elif self.moveState == "alerted":
			self.alertedMove()
		elif self.moveState == "scan":
			self.scanMove()
		elif self.moveState == "investigate":
			self.InvestigateMove()
		self.updateAngleFacing()
			
	def logicTick(self):
		if self.target != None and (self.target.health <= 0 or not self.canSeeUnit(self.target)):
			if self.moveState != "investigate":
				self.moveState = "patrol"
			if self.target.health > 0:
				self.moveState = "investigate"
				self.investigateAngle = math.atan2(self.target.speed[1], self.target.speed[0])
				self.investigateTile = [self.target.getPos()[0] / TILESIZE[0], self.target.getPos()[1] / TILESIZE[1]]
				if (PTRS["TERRAIN"].canMoveThrough((self.investigateTile[0] + round(math.cos(self.investigateAngle)), 
																						self.investigateTile[1] + round(math.sin(self.investigateAngle))))):
					self.investigateTile = [self.investigateTile[0] + round(math.cos(self.investigateAngle)), 
																	self.investigateTile[1] + round(math.sin(self.investigateAngle))]
				self.reachedTarget = False
			self.target = None
		self.nextDistanceCheck -= self.nextDistanceCheck > 0

		if (self.target == None or self.nextDistanceCheck <= 0):
			self.pickTarget()
		
		if (self.target != None):
			if not self.alerted:
				PTRS["EFFECTS"].addEffect(Effects.ExclamationEffect([self.target.getPos()[0], self.target.getPos()[1]], 50))
			self.alerted = max(self.alerted, 100)
			if self.currState == "attack" or self.currState == "windup" or dist(self.pos, self.target.getPos()) <= self.getAbilRange():
				self.speed = [0, 0]
				self.angle = math.atan2(self.target.getPos()[1] - self.pos[1], self.target.getPos()[0] - self.pos[0])
				#self.angleFacing = self.angle
				if len(self.abilList) > 0 and self.activateConditionCheck():
					self.attack(self.abilList[0])
			else:
				self.moveTowardsTarget(self.target)
				#self.speed = [math.cos(self.angle) * self.getMoveSpeed(), math.sin(self.angle) * self.getMoveSpeed()]
				
		self.alerted -= self.alerted > 0
		if self.alerted % 5 == 1:
			PTRS["EFFECTS"].addEffect(Effects.ExclamationEffect([self.pos[0], self.pos[1]], 50))
		for unit in PTRS["UNITS"].getEnemyUnits():
			if unit.isDead() and not unit.deathInvestigated and not self.alerted and self.canSeeUnit(unit):
				self.alerted = max(200, self.alerted)
				self.moveState = "investigate"
				self.investigateAngle = unit.damageAngle
				self.investigateTile = [unit.getPos()[0] / TILESIZE[0], unit.getPos()[1] / TILESIZE[1]]
				self.reachedTarget = False
				unit.deathInvestigated = True
				PTRS["EFFECTS"].addEffect(Effects.ExclamationEffect([unit.pos[0], unit.pos[1]], 50))
			elif not unit.isDead() and ((self.alerted or unit.alerted) and not (self.alerted and unit.alerted)) and self.canSeeUnit(unit):
				unit.alerted = max(self.alerted, unit.alerted)
				self.alerted = max(self.alerted, unit.alerted)
			
	def drawMe(self, camera, atStart):
		pos = intOf([self.pos[0] - camera.Left(), self.pos[1] - camera.Top()])
		size = int(self.size)
		d = int(self.getSightRange())
		a = self.getSightArc()
		drawCharPic(camera.getSurface(), self.picture, pos, int(self.animationFrames[int(self.frame)]), int(self.angleFacing * 180 / math.pi), self.team)
		if PTRS["DRAWDEBUG"]:
			if not self.isDead():
				pygame.draw.line(camera.getSurface(), [255, 0, 0], pos, [pos[0] + math.cos(self.angleFacing + a) * d, pos[1] + math.sin(self.angleFacing + a) * d])
				pygame.draw.line(camera.getSurface(), [255, 0, 0], pos, [pos[0] + math.cos(self.angleFacing - a) * d, pos[1] + math.sin(self.angleFacing - a) * d])
				pygame.draw.circle(camera.getSurface(), [155, 0, 0], pos, int(self.getListenRange()), 1)
			for p in self.walkList:
				pygame.draw.circle(camera.getSurface(), [0, 0, 255], [p[0] * TILESIZE[0] + TILESIZE[0] / 2 - camera.Left(), 
																															p[1] * TILESIZE[1] + TILESIZE[1] / 2 - camera.Top()], 5, 3)

class EnemyCivilian(EnemyUnit):
	enemyType = "civilian"
	def __init__(self, startPos, level):
		EnemyUnit.__init__(self, startPos, level)
		self.picture = "Civilian"
		self.abilList = [Abilities.SwordsmanAbil()]
	
playerUnitMap = {"ARCHER":PlayerArcher, "SWORDSMAN":PlayerUnit}
PTRS["UNITS"] = UnitStruct()

PTRS["ENEMYTYPES"] = [None, "ARCHER", "CIVILIAN"]