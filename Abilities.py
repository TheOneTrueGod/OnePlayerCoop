import Globals, math, Projectiles, random
from Globals import *
class Ability:
	icon = "Test1"
	StatAttack = 0
	StatAttackIncrement = 100
	StatKnockbackAttack = 0
	StatKnockbackAttackIncrement = 100
	StunTime = 4
	KnockbackAmount = 4
	Damage = 1
	Range = 50
	AttackType = "base"
	GoldCost = 100
	UpgradeCost = 50
	UpgradeIncrement = 50
	RageMultiplier = 10
	
	def getDescription(self):
		return "A test description.  Has " + str(self.getAttackVal()) + " attack value"
		
	def getAttackVal(self):
		toRet = self.StatAttack + self.StatAttackIncrement * (self.level)
		if self.user != None:
			toRet += self.user.getAttack(self.AttackType)
		return toRet
		
	def getCooldownPercent(self):
		return 1 - self.cooldown[0] / float(self.cooldown[1])
		
	def getKnockbackVal(self):
		toRet = self.StatKnockbackAttack + self.StatKnockbackAttackIncrement * (self.level)
		if self.user != None:
			toRet += self.user.getStat("knockbackAttack")
		return toRet
	
	def __init__(self):
		self.hitsAllies = False
		self.hitsEnemies = True
		self.hitsUser = False
		self.user = None
		self.range = 20
		self.cooldown = [0, 30]
		self.timeTaken = 25
		self.hitFrames = [1]
		self.level = 0
		
	def getRange(self):
		return self.Range
		
	def getCost(self):
		if self.level == 0:
			return self.GoldCost
		return self.UpgradeCost + (self.level - 1) * self.UpgradeIncrement
		
	def use(self, user):
		if self.cooldown[0] <= 0:
			#user.attackCallback = self.useCallback
			user.hitFrames = self.hitFrames[:]
			user.setState("attack", self.timeTaken)
			self.user = user
			self.cooldown[0] = self.cooldown[1]
		
	def update(self):
		self.cooldown[0] -= (self.cooldown[0] > 0)
		
	def useCallback(self, user):
		pass
		
	def hitTarget(self, target, angle):
		target.addDamage(self.Damage, self.getAttackVal(), self.user, self.RageMultiplier)
		target.addKnockback(self.KnockbackAmount, angle, self.getKnockbackVal(), self.StunTime)
	
class ArcherShotAbil(Ability):
	Range = 130
	def __init__(self):
		Ability.__init__(self)
		self.cooldown = [0, 20]
		self.timeTaken = 20
		
	def useCallback(self, user):
		if user.target and user.canSeeUnit(user.target) and not user.target.isDead():
			user.target.addDamage(self.Damage, self.user)
			a = random.uniform(0, math.pi * 2)
			d = random.uniform(3, self.user.target.size)
			p = [self.user.target.getPos()[0] + math.cos(a) * d, self.user.target.getPos()[1] + math.sin(a) * d]
			PTRS["BULLETS"].add(Projectiles.Bullet(self.user.getPos(), p))
	
class SwordsmanAbil(Ability):
	Range = 30
	def __init__(self):
		Ability.__init__(self)
		self.cooldown = [0, 20]
		self.timeTaken = 20
		self.hitsAllies = False
		self.hitsEnemies = True
	
	def useCallback(self, user):
		if user.target and user.canSeeUnit(user.target) and not user.target.isDead() and dist(user.pos, user.target.pos) <= self.Range:
			user.target.addDamage(self.Damage, self.user)
		"""unitList = PTRS["UNITS"].getTargets(user.team, self.hitsAllies, self.hitsEnemies)
		validTargets = []
		for target in unitList:
			d = Globals.dist(user.pos, target.pos)
			a = math.atan2(target.pos[1] - user.pos[1], target.pos[0] - user.pos[0])
			
			angDiff = (user.angle - a)
			if d < self.Range + user.size + target.size:
				validTargets += [[target, a]]
		random.shuffle(validTargets)
		targ, a = validTargets.pop()"""
	
class ArcAttackAbility(Ability):
	StatAttackIncrement = 100
	MaxUnitsHit = 2
	RageMultiplier = 10
	
	def getDescription(self):
		return "A basic attack.  Deals damage based on your weapon."
		
	def __init__(self):
		Ability.__init__(self)
		self.cooldown = [0, 60]
		self.timeTaken = 30
		self.arcOfEffect = math.pi / 3.0
		
	def useCallback(self, user):
		unitList = Globals.units.getTargets(user.team, self.hitsAllies, self.hitsEnemies)
		validTargets = []
		for target in unitList:
			d = Globals.dist(user.pos, target.pos)
			a = math.atan2(target.pos[1] - user.pos[1], target.pos[0] - user.pos[0])
			
			angDiff = (user.angle - a)
			if d < self.range + user.size + target.size and (math.fabs(angDiff) < self.arcOfEffect or math.fabs(angDiff) > math.pi * 2 - self.arcOfEffect):
				validTargets += [[target, a]]
		random.shuffle(validTargets)
		for i in range(min(len(validTargets), self.MaxUnitsHit)):
			targ, a = validTargets.pop()
			self.hitTarget(targ, a)
		







		
class PlayerArcAttackAbility(ArcAttackAbility):
	StatAttackIncrement = 100
	
	def getDescription(self):
		return "A basic attack.  Deals damage based on your weapon."
			
	def __init__(self):
		ArcAttackAbility.__init__(self)
		self.cooldown = [0, 30]
		self.timeTaken = 25
		self.hitFrames = [3]
		
	def use(self, user):
		if self.cooldown[0] <= 0:
			#user.attackCallback = self.useCallback
			user.hitFrames = self.hitFrames[:]
			user.setState("attack", self.timeTaken, [5, 6, 7, 8, 9, "idle"])
			self.user = user
			self.cooldown[0] = self.cooldown[1]
######################
## Player Abilities ##
######################
class Charge(Ability):
	icon = "Charge"
	StatAttackIncrement = 100
	RageMultiplier = 15
	
	def getDescription(self):
		return "Charge.  After a short prep time, you charge your enemies, ramming into them and knocking them back." + \
					"Has " + str(self.getAttackVal()) + " attack value"
					
	def __init__(self):
		Ability.__init__(self)
		self.cooldown = [0, 60]
		self.timeTaken = 30
		self.hitFrames = [2]
		self.activeTimeLeft = 0
		self.chargeDuration = 20
		self.angle = 0
		self.user = None
		self.strength = 10
		self.radius = 5
		
	def update(self):
		Ability.update(self)
		if self.activeTimeLeft > 0:
			self.activeTimeLeft -= 1
			if self.activeTimeLeft <= 0:
				self.createShockwave()
				#Globals.terrain.setAtPos(self.user.pos, 3)
				return
			self.user.addKnockback(self.strength, self.angle, 100000000000000, 0, True)
			unitList = Globals.units.getTargets(self.user.team, self.hitsAllies, self.hitsEnemies)
			for unit in unitList:
				if Globals.dist(unit.pos, self.user.pos) < self.radius + self.user.size + unit.size:
					self.createShockwave()
					break
	
	def createShockwave(self):
		Globals.projectiles.addProjectile(Projectiles.Shockwave([self.user.pos[0], self.user.pos[1]], 
							self.user.angle, self.user.team, self.hitTarget))
		self.activeTimeLeft = 0
		self.user.knockback = [0, 0]
					
	def hitTarget(self, target, angle):
		target.addDamage(self.Damage, self.getAttackVal(), self.user, self.RageMultiplier)
		target.addKnockback(self.strength, angle, self.getKnockbackVal(), self.StunTime)
		target.stun(self.StunTime)
			
	def useCallback(self, user):
		self.activeTimeLeft = self.chargeDuration
		self.angle = user.angle
		self.user = user
		
	def use(self, user):
		if self.cooldown[0] <= 0:
			#user.attackCallback = self.useCallback
			user.hitFrames = self.hitFrames[:]
			user.setState("attack", self.timeTaken, [10, 11, 11, 11, 11, "idle"])
			self.user = user
			self.cooldown[0] = self.cooldown[1]
		
class ProjectileAbility(Ability):
	icon = "Ki Shot"
	StatAttackIncrement = 100
	RageMultiplier = 5
	
	def getDescription(self):
		return "Ki shot.  Charge up energy and unleash it in a directed burst, launching a small projectile at your enemies." + \
					"\nAttack: " + str(self.getAttackVal()) + \
					"\nCast Time: " + str(self.getTimeTaken())
					
	def __init__(self):
		Ability.__init__(self)
		self.cooldown = [0, 60]
		self.timeTaken = 50
		self.hitFrames = [2]
		
	def getFrames(self):
		if self.level < 5:
			return [10, 11, 10, 11, 10, 11, 12, 13, 14, "idle"]
		elif self.level < 10:
			return [10, 11, 10, 11, 12, 13, 14, "idle"]
		else:
			return [10, 11, 12, 13, 14, "idle"]
			
	def getHitFrames(self):
		if self.level < 5:
			return [6]
		elif self.level < 10:
			return [4]
		elif self.level < 15:
			return [2]
		else:
			return [2, 3]
			
	def getCooldown(self):
		return max(self.cooldown[1] - (self.level - 1) * 2, 15)
		
	def getTimeTaken(self):
		return max(self.timeTaken - (self.level - 1) * 2, 15)
			
	def use(self, user):
		if self.cooldown[0] <= 0:
			#user.attackCallback = self.useCallback
			user.hitFrames = self.getHitFrames()[:]
			user.setState("attack", self.getTimeTaken(), self.getFrames())
			self.user = user
			self.cooldown[0] = self.getCooldown()

	def useCallback(self, user):
		Globals.projectiles.addProjectile(Projectiles.Projectile([user.pos[0], user.pos[1]], user.angle, user.team, self.hitTarget))
		
class ProjectileSprayAbility(Ability):
	icon = "Ki Spray"
	StatAttackIncrement = 100
	KnockbackAmount = 2
	
	def getDescription(self):
		return "Ki Spray.  Launches a spray of shots forward." + \
					"Has " + str(self.getAttackVal()) + " attack value"
					
	def __init__(self):
		Ability.__init__(self)
		self.cooldown = [0, 60]
		self.timeTaken = 50
		self.hitFrames = [6]
		
	def use(self, user):
		if self.cooldown[0] <= 0:
			#user.attackCallback = self.useCallback
			user.hitFrames = self.hitFrames[:]
			user.setState("attack", self.timeTaken, [10, 11, 10, 11, 10, 11, 12, 13, 14, "idle"])
			self.user = user
			self.cooldown[0] = self.cooldown[1]

	def useCallback(self, user):
		for i in [-3, -2, -1, 0, 1, 2, 3]:
			Globals.projectiles.addProjectile(Projectiles.Projectile([user.pos[0], user.pos[1]], user.angle + math.pi / 16.0 * i, user.team, self.hitTarget))
			
class Cleave(ArcAttackAbility):
	StatAttackIncrement = 100
	MaxUnitsHit = 5
	RageMultiplier = 15
	
	def __init__(self):
		ArcAttackAbility.__init__(self)
		self.cooldown = [0, 100]
		self.timeTaken = 30
		self.hitFrames = [3]
	
	def getDescription(self):
		return "A cleaving attack.  Hits up to " + str(self.MaxUnitsHit) + " units in one swing"
		
class AttackBonusAbility(Ability):
	icon = "Test1"
	AttackType="attack"
	UpgradeCost = 50
	UpgradeIncrement = 50
	Amount = 50
	def getCost(self):
		return self.UpgradeCost + (self.level) * self.UpgradeIncrement
	
	def getAttackAmount(self):
		return self.Amount * self.level
class WeaponBonus(AttackBonusAbility):
	AttackType="weapon"
	def getDescription(self):
		return "Attack Bonus With Weapons"
	
class StatAbility(Ability):
	icon = "Test2"
	Stat="attack"
	UpgradeCost = 50
	UpgradeIncrement = 50
	Amount = 50
	def getCost(self):
		return self.UpgradeCost + (self.level) * self.UpgradeIncrement
	
	def getStatAmount(self):
		return self.Amount * self.level
class AttackBonus(StatAbility):
	Stat="attack"
	def getDescription(self):
		return "Attack Bonus"
class DefenseBonus(StatAbility):
	Stat="defense"
	def getDescription(self):
		return "Defense Bonus"
#Enemy Abilities
			
class EnemyArcAttackAbility(ArcAttackAbility):
	StatAttackIncrement = 50
	StunTime = 1
	KnockbackAmount = 4
	def getDescription(self):
		return "Enemy attack ability.  If you can see this, you're doing something wrong."
		
	def __init__(self):
		ArcAttackAbility.__init__(self)
		self.cooldown = [0, 60]
		self.timeTaken = 30
		self.hitFrames = [2]
		
	def use(self, user):
		if self.cooldown[0] <= 0:
			#user.attackCallback = self.useCallback
			user.hitFrames = self.hitFrames[:]
			user.setState("attack", self.timeTaken, [5, 5, 6, 7, 8, 9, "idle"])
			self.user = user
			self.cooldown[0] = self.cooldown[1]
		
class MediumEnemyArcAttackAbility(EnemyArcAttackAbility):
	StatAttackIncrement = 50
	StunTime = 1.5
	Damage = 1.5
	KnockbackAmount = 4
	
abilDict = {1:ProjectileAbility, 3:Charge, 4:Cleave, "weapon":WeaponBonus, "attack":AttackBonus, "defense":DefenseBonus}
attackTypes = ["weapon"]