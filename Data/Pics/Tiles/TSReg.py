import os, sys
def registerTilesets():
	curMap = {}
	filePath = os.path.join("Data", "Pics", "Tiles", "Tilesets.txt")
	dirPath = os.path.join("Data", "Pics", "Tiles")
	dirList = os.listdir(dirPath)
	on = 0
	if os.path.isfile(filePath):
		fileIn = open(filePath)
		line = fileIn.readline()
		while line:
			line = line.split()
			if len(line) == 2 and len(line[1]) < 3 and line[1].isdigit() and len(line[0]) < 30 and line[0] not in curMap and line[0] in dirList:
				curMap[line[0]] = line[1]
				on = max(int(line[1]) + 1, int(on))
			line = fileIn.readline()
		fileIn.close()
	
	for file in os.listdir(dirPath):
		file = os.path.splitext(file)
		if file[1].upper() == ".PNG" and file[0].upper() != "TRAPS":
			curMap[file[0]] = str(on)
			on = 1
			
	fileOut = open(filePath, "w")
	for key in curMap:
		fileOut.write(key + " " + curMap[key] + "\n")
	fileOut.close()
	
registerTilesets()