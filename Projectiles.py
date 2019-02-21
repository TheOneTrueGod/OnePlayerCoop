import math, Effects
from Globals import *
class Bullet:
	def __init__(self, pos, endPos):
		self.drawn = False
		self.pos = [pos[0], pos[1]]
		self.endPos = [endPos[0], endPos[1]]
	
	def readyToDelete(self):
		return self.drawn
		
	def update(self):
		PTRS["EFFECTS"].addEffect(Effects.LineEffect(self.pos, self.endPos, 1, 20))
			
	def drawMe(self, surface):
		start = [int(self.pos[0] / gridsize), int(self.pos[1] / gridsize)]
		end = [int(self.endPos[0] / gridsize), int(self.endPos[1] / gridsize)]
		
		#for pos in raytrace(start, end):
		#	g = gridsize
		#	gridPos = [int(pos[0]), int(pos[1])]
		#	pygame.draw.rect(surface, [255, 255, 0], [[gridPos[0] * g, gridPos[1] * g], [g, g]])
		#	pygame.draw.rect(surface, [0, 255, 0], [[gridPos[0] * g, gridPos[1] * g], [g, g]], 1)
		
		#pygame.draw.line(surface, [255, 0, 0], self.pos, self.endPos)
		self.drawn = True

class BulletStruct:
	def __init__(self):
		self.bullets = []
		
	def add(self, newB):
		self.bullets += [newB]
		
	def update(self):
		i = 0
		while i < len(self.bullets):
			self.bullets[i].update()
			if self.bullets[i].readyToDelete():
				del self.bullets[i]
			else:
				i += 1
	def drawMe(self, surface):
		for b in self.bullets:
			b.drawMe(surface)
			
PTRS["BULLETS"] = BulletStruct()