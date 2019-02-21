import pygame, random
from Globals import *
class EffectStruct:
	def __init__(self):
		self.effects = []
		
	def addEffect(self, effect):
		self.effects += [effect]
		
	def update(self):
		i = 0
		while i < len(self.effects):
			self.effects[i].update()
			if self.effects[i].readyToDelete():
				del self.effects[i]
			else:
				i += 1
		
	def drawMe(self, camera):
		for effect in self.effects:
			effect.drawMe(camera)
		
class Effect:
	def __init__(self):
		self.time = 0
		
	def update(self):
		self.time -= 1
		
	def readyToDelete(self):
		return True
		
	def drawMe(self, camera):
		return
		
class CircleEffect(Effect):
	def __init__(self, pos, radius, time, clr = [255, 255, 122], startAlpha = 255):
		self.pos = pos
		self.radius = radius
		self.time = time
		self.alpha = startAlpha
		self.clr = clr
		
	def readyToDelete(self):
		return self.time <= 0
		
	def update(self):
		self.time -= 1
	
	def drawMe(self, camera):
		pos = (int(self.pos[0] - camera.Left()), int(self.pos[1] - camera.Top()))
		size = int(self.radius)
		alpha = int(self.alpha)
		camera.getSurface().blit(create_transparent_circle(self.clr, alpha, size), [pos[0] - size, pos[1] - size])
		
class DiminishingCircleEffect(CircleEffect):
	def __init__(self, pos, radius, time):
		CircleEffect.__init__(self, pos, radius, time)
		self.deltaRad = (radius / 2.0) / float(time)
		self.alpha = 255
		self.deltaAlpha = 255 / float(time)
		
	def update(self):
		self.time -= 1
		self.radius -= self.deltaRad
		self.alpha -= self.deltaAlpha

class ExclamationEffect(Effect):
	def __init__(self, pos, time):
		self.pos = [pos[0] - 3, pos[1] - 7]
		self.time = time
		self.alpha = 255
		self.deltaAlpha = 255 / float(time)
		self.deltaPos = [random.uniform(-0.1, 0.1), random.uniform(-0.3, -0.5)]
		
	def readyToDelete(self):
		return self.time <= 0
		
	def update(self):
		self.time -= 1
		self.pos = [self.pos[0] + self.deltaPos[0], self.pos[1] + self.deltaPos[1]]
		self.alpha -= self.deltaAlpha
	
	def drawMe(self, camera):
		pos = (int(self.pos[0] - camera.Left()), int(self.pos[1] - camera.Top()))
		alpha = int(self.alpha)
		EFFECTPICS["Exclamation"].set_alpha(int(alpha))
		camera.getSurface().blit(EFFECTPICS["Exclamation"], pos)
		
class LineEffect(Effect):
	def __init__(self, start, end, radius, time):
		self.pos = [intOf(start), intOf(end)]
		self.radius = radius
		self.time = time
		self.alpha = 255
		self.deltaAlpha = 255 / float(time)
		self.deltaRad = 3 / float(time)
		
	def readyToDelete(self):
		return self.time <= 0
		
	def update(self):
		self.time -= 1
		self.radius += self.deltaRad
		self.alpha -= self.deltaAlpha
	
	def drawMe(self, camera):
		start = intOf(self.pos[0])
		end = intOf(self.pos[1])
		size = int(self.radius)
		alpha = int(self.alpha)
		line = create_transparent_line(end[0] - start[0], end[1] - start[1], [255, 255, 122], alpha, size)
		camera.getSurface().blit(line, [min(end[0], start[0]) - camera.Left(), min(end[1], start[1]) - camera.Top()])
	
class TextEffect(Effect):
	def __init__(self, pos, clr, time, text):
		self.pos = pos
		self.type = "Text"
		self.time = time
		self.clr = clr
		self.deltaPos = [0, random.uniform(-3, -6)]
		self.deltaPos += [self.deltaPos[1] * -(random.uniform(1, 4)) / float(time)]
		self.text = text
		self.inc = (clr[0] / float(time),clr[1] / float(time),clr[2] / float(time))
	
	def readyToDelete(self):
		return self.time <= 0
	
	def update(self):
		self.time -= 1
		#self.pos = (self.pos[0], self.pos[1] - 0.9 * self.calcTimeRate())
		self.pos = (self.pos[0] + self.deltaPos[0], self.pos[1] + self.deltaPos[1])
		self.deltaPos[1] += self.deltaPos[2]
		self.clr = (self.clr[0] - self.inc[0], 
					self.clr[1] - self.inc[1], 
					self.clr[2] - self.inc[2])
	
	def drawMe(self, camera):
		pos = [self.pos[0] - camera.Left(), self.pos[1] - camera.Top()]
		camera.getSurface().blit(FONTS["EFFECTFONT"].render(self.text, False, self.clr), pos)
	
def create_transparent_line(width, height, color, alpha, radius=1):
	size = radius * 2
	temp_surf = pygame.Surface((math.fabs(width) + radius, math.fabs(height) + radius))
	temp_surf.set_alpha(int(alpha))
	temp_surf.fill([122, 13, 75])
	temp_surf.set_colorkey([122, 13, 75])
	if signOf(width) != signOf(height):
		start = [0, math.fabs(height)]
		end = [math.fabs(width), 0]
	else:
		start = [0, 0]
		end = [math.fabs(width), math.fabs(height)]
	pygame.draw.line(temp_surf, color, start, end, radius)

	return temp_surf
	
def create_transparent_circle(color, alpha, radius, width=0):
	size = radius * 2
	temp_surf = pygame.Surface((size, size))
	temp_surf.set_alpha(int(alpha))
	temp_surf.fill([122, 13, 75])
	temp_surf.set_colorkey([122, 13, 75])
	pygame.draw.circle(temp_surf, color, (radius, radius), radius, width)
	return temp_surf
	
PTRS["EFFECTS"] = EffectStruct()