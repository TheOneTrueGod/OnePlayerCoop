import math, pygame, os, pygame, sys
os.environ['SDL_VIDEO_WINDOW_POS'] = str(3) + "," + str(29)
from pygame.locals import *
if not pygame.font.get_init():
	pygame.font.init()
DEBUGMODE = 0
TOOLTIPS = {}
CHARPICTURES = {}
ICONS = {}
SCREENSIZE = [800, 600]
EDITORSCREENSIZE = [1000, 700]
TILESIZE = [20, 20]
NUMABILS = 2
ICONSIZE = 55
MINFPS = 1000 / 30
PTRS = {"FRAME":0}
FOGOFWAR = False
RESPAWNTIME = 50
FULLSCREEN = pygame.FULLSCREEN
if "-w" in sys.argv or "-d" in sys.argv:
	FULLSCREEN = False
	
surface = pygame.display.set_mode(SCREENSIZE, FULLSCREEN)
gridsize = 20

NUMPLAYERS = 1

PTRS["DRAWDEBUG"] = False
PTRS["EDITORMODE"] = False

GRAVITY = 1.0
JUMPSPEED = -10
MAXFALLSPEED = 18
DEFAULTSCANTIME = 100
FRICTION = 0.8
SPEEDTHRESHOLD = 0.01
MAXRUNSPEED = 5#2.5
AIRCONTROL = 0.4
ACCELERATION = 0.7
STARTGOLD = 200
EFFECTPICS = {"Exclamation":pygame.image.load(os.path.join("Data", "Pics", "Effects", "Exclamation.png"))}
EFFECTPICS["Exclamation"].set_colorkey([255, 255, 255])

#units = None
#players = None
#effects = None
#terrain = None
#projectiles = None
#backgroundPic = None

FONTS = {"TEXTBOXFONT":pygame.font.Font(os.path.join("Data", "Fonts", "MainFont.ttf"),12),
				 "EFFECTFONT" :pygame.font.Font(os.path.join("Data", "Fonts", "MainFont.ttf"),12)}

ScanTimeLookup = {0:1, 1:20, 2:40, 3:60, 4:80, 5:100, 6:150, 7:200, 8:400, 9:1000}

def enum(*sequential, **named):
	enums = dict(zip(sequential, range(len(sequential))), **named)
	return type('Enum', (), enums)
	
itemTypes = enum('KEY', 'RKEY', 'BKEY', 'WKEY',  'OKEY', 'COIN', 'DEFEND', 'HEALTH', 'BLANK')

def dist(a, b):
	return math.sqrt((a[0] - b[0]) **2 + (a[1] - b[1])**2)
	
def signOf(i):
	if i >= 0:
		return 1
	return -1;
	
def isInt(s):
	try:
		int(s)
		return True
	except ValueError:
		return False
	
def drawTextBox(surface, pos, size, text, drawBorder, bckClr = [0, 0, 0], txtClr = [255, 255, 255]):
	textSpacing = 5
	if drawBorder:
		pygame.draw.rect(surface, bckClr, (pos,size))
		pygame.draw.rect(surface, txtClr, (pos[0], pos[1],size[0], size[1]),2)
	currPos = [pos[0] + 6,pos[1] + 6]
	for lines in text.split("\n"):
		currText = lines.split(" ")
		for i in currText:
			if currPos[1] < pos[1] + size[1]:
				if i.find('\n') != -1:
					toDraw = FONTS["TEXTBOXFONT"].render(i[:i.find('\n')], False, txtClr)
				else:
					toDraw = FONTS["TEXTBOXFONT"].render(i, False, txtClr)
				if currPos[0] + toDraw.get_width() - pos[0] + textSpacing > size[0]:
					currPos[0] = pos[0] + 6
					currPos[1] = currPos[1] + 12
				surface.blit(toDraw,(currPos))
				currPos[0] += toDraw.get_width() + textSpacing
		currPos[0] = pos[0] + 6
		currPos[1] = currPos[1] + 12
		
def raytrace(start, end):
	g = gridsize
	dx = abs(end[0] - start[0])
	dy = abs(end[1] - start[1])
	x = start[0]
	y = start[1]
	n = 1 + int(dx) + int(dy)
	if end[0] > start[0]:
		x_inc = 1
	else:
		x_inc = -1
	if (end[1] > start[1]):
		y_inc = 1
	else:
		y_inc = -1
	error = dx - dy
	dx *= 2
	dy *= 2

	toRet = []
	while n > 0:
		n -= 1
		toRet += [[x, y]]

		if (error > 0):
			x += x_inc
			error -= dy
		else:
			y += y_inc
			error += dx
	return toRet

def signOf(i):
	if i >= 0:
		return 1
	elif i < 0:
		return -1

def intOf(list):
	return [int(k) for k in list]
	
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
		if ev.type == KEYDOWN:
			self.pressed[ev.key] = True
		elif ev.type == KEYUP:
			if ev.key in self.pressed:
				del self.pressed[ev.key]
		elif ev.type == MOUSEMOTION:
			self.mousePos = ev.pos
		elif ev.type == MOUSEBUTTONDOWN:
			self.mousePos = ev.pos
			self.mouseButtons += [ev.button]
		elif ev.type == MOUSEBUTTONUP:
			self.mousePos = ev.pos
			if ev.button in self.mouseButtons:
				self.mouseButtons.remove(ev.button)
PTRS["KEYS"] = Keys()

def getPlayerControls(playerNum, keyString):
	if keyString.upper() in ["BACKUP", "RESTORE", "RESTART", "QUIT", "SWITCH", "START"]:
		return {"BACKUP":K_b, "RESTORE":K_n, "RESTART":K_TAB, "QUIT":K_ESCAPE, "SWITCH":K_v, "START":K_SPACE}[keyString.upper()]
	elif playerNum == 1:
		return {"UP":K_UP, "DOWN":K_DOWN, "LEFT":K_LEFT, "RIGHT":K_RIGHT, "ACTIVATE":K_SPACE}[keyString.upper()]
		return {"UP":K_w, "DOWN":K_s, "LEFT":K_a, "RIGHT":K_d, "ACTIVATE":K_SPACE}[keyString.upper()]
	elif playerNum == 2:
		return {"UP":K_UP, "DOWN":K_DOWN, "LEFT":K_LEFT, "RIGHT":K_RIGHT, "ACTIVATE":K_l}[keyString.upper()]
	return 0
	
PTRS["FOGOFWAR"] = pygame.Surface(SCREENSIZE)
PTRS["FOGOFWAR"].set_colorkey([255, 0, 255])
	
def getAngDiff(selfAng, targAng):
	angDiff = (targAng - selfAng)
	if angDiff < -math.pi:
		angDiff = math.pi * 2 - angDiff
	elif angDiff > math.pi:
		angDiff = angDiff - math.pi * 2
	return angDiff
	
def posToCoords(pos):
	return (int(pos[0] / TILESIZE[0]), int(pos[1] / TILESIZE[1]))