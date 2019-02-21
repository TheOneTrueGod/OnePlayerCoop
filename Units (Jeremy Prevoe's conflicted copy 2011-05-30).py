import pygame, os, math, Equipment, Abilities, random, Terrain, Stats, copy, Projectiles
from Globals import *
from pygame.locals import *

animationFrames = {"idle":[1, 1,
													 "idle"],
									 "walk":[0, 1, 2, 1,
													 "walk"],
									 "windup":[5, 6, 7,
												"attack"],
									 "attack":[5, 6, 7, 8, 9,"idle"],
									 "stunned":[3, 3, 3, "idle"],
									 "dead":[3,3,3,"dead"]}
									 
stateTimes = {"walk":40, "idle":20, "windup":30, "attack":7, "stunned":30, "dead":5}

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
	pic.set_colorkey([255, 0, 255])
	width = pic.get_width() / frames
	toRet = []
	for x in xrange(frames):
		toRet += [[]]
		for y in xrange(pic.get_height() / width):
			toRet[x] += [pic.subsurface([x * width, y * width, width, width])]
	
	return toRet

def drawCharPic(surface, pic, pos, frame, angle):
	global CHARPICTURES
	if pic in CHARPICTURES:
		toDraw = pygame.transform.rotate(CHARPICTURES[pic][frame % 5][frame / 5], 180 - angle + 90)
		pos = [pos[0] - toDraw.get_width() / 2, pos[1] - toDraw.get_height() / 2]
		surface.blit(toDraw, pos)
	else:
		CHARPICTURES[pic] = loadCharPic(pic)
		drawCharPic(surface, pic, pos, frame, angle)
		
class UnitStruct:
	def __init__(self):
		self.enemyUnits = []
		self.alliedUnits = []#ImmobileUnit([400, 299], 1)]
		self.enemyBackup = []		
		self.alliedBackup = []		
		
	def backup(self):
		self.enemyBackup = []
		self.alliedBackup = []
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
		e = EnemyUnit(pos, 1)
		if e != None:
			self.enemyUnits += [e]
		return e
			
	def addPlayerUnit(self, unit):
		self.alliedUnits += [unit]
			
	def getPlayers(self):
		return self.alliedUnits
		
	def getEnemyUnits(self):
		return self.enemyUnits
		
	def drawMe(self):
		for unit in self.enemyUnits + self.alliedUnits:
			unit.drawMe()
		
class Unit:
	def __init__(self, startPos, level):
		self.pos = [startPos[0], startPos[1]]
		self.startPos = [startPos[0], startPos[1]]
		self.speed = [0, 0]
		self.onGround = False
		self.level = level
		self.logicTickIn = 3
		self.angle = math.pi / 2.0 * 3
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
		self.stunResidue = 0.0
		self.rageTable = {}
		self.selected = False
		
	def backup(self):
		pass
		
	def isDead(self):
		return self.health <= 0 and self.currState != "attack"
		
	def restore(self, previousUnit):
		pass
		
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
	
	def getSightRange(self):
		return 0
		
	def getSightArc(self):
		return 0
		
	def unitInSightArc(self, unit):
		ang = math.atan2(self.pos[1] - unit.getPos()[1], self.pos[0] - unit.getPos()[0])
		angDiff = ang + math.pi - (self.angle % (math.pi * 2))
		
		if math.fabs(angDiff) < self.getSightArc() or math.fabs(angDiff) > math.pi * 2 - self.getSightArc():
			return True
		return False
		
	def canSeeUnit(self, unit):
		if dist(unit.getPos(), self.getPos()) <= self.getListenRange() or \
			(dist(unit.getPos(), self.getPos()) <= self.getSightRange() and self.unitInSightArc(unit)):
			for square in raytrace([int(self.getPos()[0] / TILESIZE[0]), int(self.getPos()[1] / TILESIZE[1])], 
							 [int(unit.getPos()[0] / TILESIZE[0]), int(unit.getPos()[1] / TILESIZE[1])]):
				if not Terrain.canSeeThrough(PTRS["TERRAIN"].getAtCoord(intOf(square))):
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
		
	def stun(self, duration):
		if self.currState != "stunned":
			self.stunResidue += duration * (1 - self.stunResistance)
			if self.stunResidue >= 1:
				self.setState("stunned", max(self.stunResidue * 5, 10))
				self.stunResidue = 0
				return True
		return False
				
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
		
	def move(self):
		lastPos = [self.pos[0], self.pos[1]]
		self.attackCooldown -= (self.attackCooldown > 0)
		self.frame += self.frameRate
			
		if len(self.hitFrames) > 0 and self.frame >= self.hitFrames[0] and not self.attacked:
			self.abilList[0].useCallback(self)
			del self.hitFrames[0]
			if len(self.hitFrames) <= 0:
				self.attacked = True
			
		if (self.frame >= len(self.animationFrames) - 1):
			self.setState(self.animationFrames[len(self.animationFrames) - 1])
	
		self.stunResidue = max(0, self.stunResidue - 0.001)
	
		speed = [self.knockback[0], self.knockback[1]]
		#if math.fabs(self.knockback[0]) == 0 and math.fabs(self.knockback[1]) == 0:
		if (self.currState is not "stunned"):
			speed[0] += self.speed[0]
			speed[1] += self.speed[1]

		if Terrain.canMoveThrough(PTRS["TERRAIN"].getAtPos([self.pos[0] + speed[0], self.pos[1]])):
			self.pos[0] += speed[0]
		else:
			if speed[0] > 0:
				self.pos[0] = int(self.pos[0] / 20 + 1) * 20 - 0.001
			else:
				self.pos[0] = int(self.pos[0] / 20) * 20 + 0.001
		if Terrain.canMoveThrough(PTRS["TERRAIN"].getAtPos([self.pos[0], self.pos[1] + speed[1]])):
			self.pos[1] += speed[1]
		else:
			if speed[1] > 0:
				self.pos[1] = int(self.pos[1] / 20 + 1) * 20 - 0.001
			else:
				self.pos[1] = int(self.pos[1] / 20) * 20 + 0.001
			
		for i in [0, 1]:
			self.knockback[i] *= 0.96
			if math.fabs(self.knockback[i]) <= 0.1:
				self.knockback[i] = 0
			if math.fabs(self.knockback[i]) <= 1 and self.currState == "attack":
				self.knockback[i] = 0
				
		if self.currState == "walk" and lastPos[0] == self.pos[0] and lastPos[1] == self.pos[1]:
			self.setState("idle")
		elif self.currState == "idle" and (lastPos[0] != self.pos[0] or lastPos[1] != self.pos[1]):
			self.setState("walk")
			
	def logicTick(self):
		pass
		
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
	
	def drawMe(self):
		pos = intOf(self.pos)
		size = int(self.size)
		if self.selected == 1:
			pygame.draw.circle(surface, [255, 0, 0], pos, size, 1)
		elif self.selected == 2:
			pygame.draw.circle(surface, [0, 0, 255], pos, size, 1)
		drawCharPic(surface, self.picture, pos, int(self.animationFrames[int(self.frame)]), int(self.angle * 180 / math.pi))
		
class KeyRecorder:
	def __init__(self):
		self.pressed = {}
		self.mousePos = {}
		self.mouseButtons = {}
		self.lastFrame = 0
		
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
		self.maxHealth = 1
		self.health = self.maxHealth
		self.picture = "MageKnight"
		self.abilList = [Abilities.SwordsmanAbil()]#[Abilities.PlayerArcAttackAbility()]
		self.abilSelected = 1
		self.stunResistance = 0.5
		self.keyRecorder = KeyRecorder()
		self.controlled = False
		self.controller = 0
		
	def backup(self):
		pass
		
	def restore(self, previousUnit):
		self.controlled = False
		self.keyRecorder = previousUnit.keyRecorder
		self.controller = previousUnit.controller
		
	def setAbils(self, abils):
		self.abilList = [self.abilList[0]] + abils
		
	def findTargetForAbil(self):
		validTargets = []
		for unit in PTRS["UNITS"].getEnemyUnits():
			if not unit.isDead() and self.canSeeUnit(unit):
				validTargets += [unit]
		if validTargets:
			return random.choice(validTargets)
		return None
				
	def move(self):
		if self.isDead():
			return
		if self.controlled:
			keys = PTRS["KEYS"]
			self.keyRecorder.setCurrFrame(keys)
		else:
			keys = self.keyRecorder
			
		if keys != None:
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
			
			if (self.currState in ["idle", "walk"]):
				speedMod = 1
				if keys.keyPressed(getPlayerControls(self.controller, "ACTIVATE")):
					targ = self.findTargetForAbil()
					if targ:
						self.target = targ
						self.abilList[0].use(self)
						speedMod = 0
					else:
						speedMod = 0.5
					
				if keys.keyPressed(getPlayerControls(self.controller, "UP")):
					self.speed[1] += -self.getMaxSpeed() * speedMod
				if keys.keyPressed(getPlayerControls(self.controller, "DOWN")):
					self.speed[1] += self.getMaxSpeed() * speedMod
			
				if keys.keyPressed(getPlayerControls(self.controller, "LEFT")):
					self.speed[0] += -self.getMaxSpeed() * speedMod
				if keys.keyPressed(getPlayerControls(self.controller, "RIGHT")):
					self.speed[0] += self.getMaxSpeed() * speedMod
			if keys.getMouseButtons():
				ang = math.atan2(keys.getMousePos()[1] - self.pos[1], keys.getMousePos()[0] - self.pos[0])
				PTRS["BULLETS"].add(Projectiles.Bullet(self.pos, [self.pos[0] + math.cos(ang) * 50, self.pos[1] + math.sin(ang) * 50]))
			if self.currState == "attack":
				self.angle = math.atan2(self.target.getPos()[1] - self.pos[1], self.target.getPos()[0] - self.pos[0])
			elif self.speed[1] != 0 or self.speed[0] != 0:
				self.angle = math.atan2(self.speed[1], self.speed[0])
		Unit.move(self)
		
	def getMaxSpeed(self):
		toRet = MAXRUNSPEED
		return toRet

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
		self.moveSpeed = 3
		self.team = 2
		self.stunResistance = 0.0
		self.picture = "Archer"
		self.offset = 0
		self.patrolTarget = [self.startPos[0] / TILESIZE[0], self.startPos[1] / TILESIZE[1]]
		self.scanTime = 1
		self.scanDeltaTime = 1
		self.scanDeltaAng = 0
		self.scanType = "Passive"
		self.scanAngle = 0
		
	
	def getStat(self, stat):
		if stat in self.stats and self.stats[stat][0] == self.level:
			return self.stats[stat][1]
		if self.enemyType in Stats.enemyStats and stat in Stats.enemyStats[self.enemyType]:
			s = Stats.enemyStats[self.enemyType][stat]
		else:
			s = Stats.baseEnemyStats[stat]
		self.stats[stat] = [self.level, (s[0] + (s[1]) * self.level) * (1 + random.uniform(-s[2], s[2]))]
		return self.stats[stat][1]
		
	def getPreferredRange(self):
		return self.getStat("preferredRange")
		
	def getListenRange(self):
		return self.getStat("listenRad")
	
	def getSightRange(self):
		return self.getStat("sightRad")
		
	def getSightArc(self):
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
			#pri += random.uniform(0, 0.1)

			if (closest == None or pri > highPri) and pri > 0:
				closest = unit
				highPri = pri
		if closest != None:
			self.target = closest
			
	def activateConditionCheck(self):
		if dist(self.pos, self.target.getPos()) <= self.getStat("activateRange"):
			return True
		return False
		
	def activate(self):
		self.abilList[0].use(self)
		
	def move(self):
		Unit.move(self)
		if (self.target != None):
			self.angle = math.atan2(self.target.pos[1] - self.pos[1], self.target.pos[0] - self.pos[0])
			if self.activateConditionCheck():
				self.activate()
		else:
			if self.target == None:
				if int(self.pos[0] / TILESIZE[0]) == self.patrolTarget[0] and int(self.pos[1] / TILESIZE[1]) == self.patrolTarget[1]:
					self.speed = [0, 0]
					if self.scanTime <= 0:#When we just reached the spot
						self.scanTime = self.getStat("scanTime")
						self.scanAngle = self.angle
						self.startAng = self.angle
						self.targAng = self.angle
						self.scanDeltaTime = 1
						self.scanDeltaAng = 0
						
					self.scanTime -= self.scanTime > 0
					
					#While we're still scanning
					self.scanDeltaTime -= 1
					self.angle += self.scanDeltaAng
					if self.scanDeltaTime <= 0:
						r = random.random()
						self.startAng = self.angle
						if self.scanType == "Stop":
							self.scanDeltaTime = random.randint(10, 15)
							self.targAng = self.angle
							self.scanType = "Passive"
						elif self.scanType == "Passive":
							self.scanType = "Stop"
							self.scanDeltaTime = random.randint(30, 40)
							self.targAng = self.scanAngle + math.pi / 3 * (random.random() - 0.5)
						elif self.scanType == "Active":
							self.scanDeltaTime = random.randint(20, 25)
							self.targAng = self.scanAngle + math.pi / 2 * (random.random() - 0.5)
						self.scanDeltaAng = (self.targAng - self.angle) / (self.scanDeltaTime)
							
					
					if self.scanTime <= 0:#When the counter has run down.
						pos = (self.patrolTarget[0], self.patrolTarget[1])
						if pos in PTRS["TERRAIN"].patrolPaths:
							self.patrolTarget = (PTRS["TERRAIN"].patrolPaths[pos][0], PTRS["TERRAIN"].patrolPaths[pos][1])
						else:
							self.scanTime = 5000
				else:
					rotationSpeed = math.pi / 64.0
					targAng = math.atan2(self.patrolTarget[1] * TILESIZE[1] + TILESIZE[1] / 2 - self.pos[1], self.patrolTarget[0] * TILESIZE[0] + TILESIZE[0] / 2 - self.pos[0]) % (math.pi * 2)
					selfAng = self.angle % (math.pi * 2)
					angDiff = (targAng - selfAng)
					if math.fabs(angDiff) > math.pi:
						angDiff = math.pi * 2 - angDiff
					if math.fabs(angDiff) < rotationSpeed:
						self.angle = targAng
					else:
						self.angle = (self.angle + max(min(angDiff, rotationSpeed), -rotationSpeed)) % (math.pi * 2)
					self.speed = [math.cos(targAng) * self.moveSpeed, math.sin(targAng) * self.moveSpeed]
					
			elif self.speed[1] != 0 or self.speed[0] != 0:
				self.angle = math.atan2(self.speed[1], self.speed[0])
			
	def logicTick(self):
		if self.target != None and (self.target.health <= 0 or not self.canSeeUnit(self.target)):
			self.target = None
		self.nextDistanceCheck -= self.nextDistanceCheck > 0

		if (self.target == None or self.nextDistanceCheck <= 0):
			self.pickTarget()
		
		if (self.target != None):
			if self.currState == "attack" or self.currState == "windup" or dist(self.pos, self.target.pos) <= self.size + self.target.size + self.getPreferredRange() / 2:
				self.speed = [0, 0]
				if len(self.abilList) > 0:
					self.attack(self.abilList[0])
			else:
				self.angle += self.offset
				self.speed = [math.cos(self.angle) * self.moveSpeed, math.sin(self.angle) * self.moveSpeed]
			
	def drawMe(self):
		pos = intOf(self.pos)
		size = int(self.size)
		#pygame.draw.circle(surface, [255, 0, 0], pos, size, 1)
		d = int(self.getSightRange())
		a = self.getSightArc()
		if not self.isDead():
			pygame.draw.line(surface, [255, 0, 0], pos, [pos[0] + math.cos(self.angle + a) * d, pos[1] + math.sin(self.angle + a) * d])
			pygame.draw.line(surface, [255, 0, 0], pos, [pos[0] + math.cos(self.angle - a) * d, pos[1] + math.sin(self.angle - a) * d])
			pygame.draw.circle(surface, [155, 0, 0], pos, int(self.getListenRange()), 1)
		drawCharPic(surface, self.picture, pos, int(self.animationFrames[int(self.frame)]), int(self.angle * 180 / math.pi))
		
def drawUnit(surface, unitStr):
	s = unitStr.split("|")
	pos = [int(s[1]), int(s[2])]
	size = int(s[5])
	healthPct = int(s[6])
	pygame.draw.circle(surface, [255, 0, 0], pos, size, 1)
	pygame.draw.line(surface, [255, 0, 0], [pos[0] - size, pos[1] - size - 2], [pos[0] - size + int(size * 2 * healthPct / 100.0), pos[1] - size - 2])
	drawCharPic(surface, s[0], pos, int(s[4]), int(s[3]))
	
PTRS["UNITS"] = UnitStruct()