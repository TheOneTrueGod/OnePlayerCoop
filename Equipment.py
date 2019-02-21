from pygame.locals import *
from Globals import *
from Terrain import *
class Equipment:
	def __init__(self, owner):
		self.owner = owner
		
	def getSpeedMod(self):
		return 1
		
	def handleUpdates(self, pl):
		pass
		
class JumpBoots(Equipment):
	def handleUpdates(self, pl):
		if pl.keyPressed(K_UP):
			if self.owner.onGround:
				self.owner.speed[1] = JUMPSPEED
				self.owner.onGround = False
				
class WallClingBoots(Equipment):
	def handleUpdates(self, pl):
		if pl.keyPressed(K_LEFT) and self.owner.speed[1] >= 0  \
														 and (not canMoveThrough(terrain.getAtPos([self.owner.pos[0] - 11, self.owner.pos[1] + 6])) or \
																  not canMoveThrough(terrain.getAtPos([self.owner.pos[0] - 11, self.owner.pos[1] - 6]))):
			self.owner.speed[1] = 0
		elif pl.keyPressed(K_RIGHT) and self.owner.speed[1] >= 0 \
																and (not canMoveThrough(terrain.getAtPos([self.owner.pos[0] + 11, self.owner.pos[1] + 6])) or \
																		 not canMoveThrough(terrain.getAtPos([self.owner.pos[0] + 11, self.owner.pos[1] - 6]))):
			self.owner.speed[1] = 0
		if pl.keyPressed(K_UP) and self.owner.speed[1] >= 0 and (pl.keyPressed(K_RIGHT) or pl.keyPressed(K_LEFT)) and not self.owner.onGround:
			if (not canMoveThrough(terrain.getAtPos([self.owner.pos[0] + 11, self.owner.pos[1] + 6])) or \
					not canMoveThrough(terrain.getAtPos([self.owner.pos[0] + 11, self.owner.pos[1] - 6]))):
				self.owner.speed[1] = JUMPSPEED
				self.owner.speed[0] = -MAXRUNSPEED
			elif (not canMoveThrough(terrain.getAtPos([self.owner.pos[0] - 11, self.owner.pos[1] + 6])) or \
					  not canMoveThrough(terrain.getAtPos([self.owner.pos[0] - 11, self.owner.pos[1] - 6]))):
				self.owner.speed[1] = JUMPSPEED
				self.owner.speed[0] = MAXRUNSPEED
				
class SpeedBoots(Equipment):
	def getSpeedMod(self):
		return 2