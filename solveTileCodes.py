from os import mkdir, listdir
from os.path import isfile
import re
import sys
sys.stdout = open("log.txt", "w", encoding="latin-1")

levels = [
    {
    "file": "generic.lvl",
    "contents": [
        {
            "file": "abzu.lvl",
        },
        {
            "file": "babylonarea.lvl",
            "contents":
            [
                {
                    "file": "babylonarea_1-1.lvl",
                },
                {
                    "file": "hallofushabti.lvl",
                },
                {
                    "file": "palaceofpleasure.lvl",
                }
            ]
        },
        {
            "file": "beehive.lvl",
        },
        {
            "file": "cavebossarea.lvl",
        },
        {
            "file": "challenge_moon.lvl",
        },
        {
            "file": "challenge_star.lvl",
        },
        {
            "file": "cityofgold.lvl",
        },
        {
            "file": "cosmicocean_babylon.lvl",
        },
        {
            "file": "cosmicocean_dwelling.lvl",
        },
        {
            "file": "cosmicocean_icecavesarea.lvl",
        },
        {
            "file": "cosmicocean_jungle.lvl",
        },
        {
            "file": "cosmicocean_sunkencity.lvl",
        },
        {
            "file": "cosmicocean_temple.lvl",
        },
        {
            "file": "cosmicocean_tidepool.lvl",
        },
        {
            "file": "cosmicocean_volcano.lvl",
        },
        {
            "file": "duat.lvl",
        },
        {
            "file": "dwellingarea.lvl",
        },
        {
            "file": "eggplantarea.lvl",
        },
        {
            "file": "ending.lvl",
            "contents":
            [
                {
                    "file": "ending_hard.lvl",
                }
            ]
        },
        {
            "file": "generic.lvl",
        },
        {
            "file": "hundun.lvl",
        },
        {
            "file": "icecavesarea.lvl",
        },
        {
            "file": "junglearea.lvl",
            "contents":
            [
                {
                    "file": "blackmarket.lvl",
                }
            ]
        },
        {
            "file": "olmecarea.lvl",
        },
        {
            "file": "sunkencityarea.lvl",
            "contents":
            [
                {
                    "file": "challenge_sun.lvl",
                }
            ]
        },
        {
            "file": "templearea.lvl",
        },
        {
            "file": "testingarea.lvl",
        },
        {
            "file": "tiamat.lvl",
        },
        {
            "file": "tidepoolarea.lvl",
            "contents":
            [
                {
                    "file": "lake.lvl",
                },
                {
                    "file": "lakeoffire.lvl",
                }
            ]
        },
        {
            "file": "volcanoarea.lvl",
            "contents":
            [
                {
                    "file": "vladscastle.lvl",
                }
            ]
        }
    ]
    }
]

reRooms = re.compile(r"^(?!(?:\\[-?%+!.])|\/\/)(.+?)(?:(?:\/\/)|$)", flags=re.M) # \/\/ room(?:\n\\!.*)?\n*([\s\S]*?)\n(?:\n|$)
reTilecodeDefs = re.compile(r"^\\\?(\S*)[ \t]*?(\S)", flags=re.M)
reReplaceAllTilecodeDefs = re.compile(r"\\\?[\s\S]*\\\?.*") #find all, to replace with all tilecodes

#UNUSED
class Tilecode:
    def __init__(shortTilecode, longTilecode):   
        self.short = shortTilecode
        self.long = longTilecode

def getTilecodesOnDependencies(lvlFilename):
    levelTilecodes = []
    if lvlFilename in cachedLevelTilecodes:
        return cachedLevelTilecodes[lvlFilename]
        pass
    else:
        f = open(mypath + lvlFilename, "r", encoding="latin-1")
        text = f.read()
        f.close()
        matches = reTilecodeDefs.finditer(str)
        for match in matches:
            longTilecode = match.group(1)
            shortTilecode = match.group(2)
            tilecode = Tilecode(shortTilecode, longTilecode)
            levelTilecodes.append(tilecode)
        cachedLevelTilecodes[lvlFilename] = levelTilecodes
        return levelTilecodes

def get_uTilecode(): #unique (or unicode) tilecodes, made so this doesn't do for example, change tilecode 'a' with 'A', but then the tilecode 'A' also has to be changed and it results in wrong tilecodes
    global lastUTilecode
    lastUTilecode += 1
    return chr(lastUTilecode)
#/UNUSED

mypath = "./Original/"
#excluded_shorts = [""]
cachedLevelTilecodes = {}
shortTilecodesMap = {}
longTilecodesMap = {}
unusedTilecodes = []
lastUTilecode = 256

def define_unusedTilecodes():
    for i in range(33, 256):
        unusedTilecodes.append(chr(i))
define_unusedTilecodes()
unusedTilecodes.remove("")

def getUnusedTilecode():
    if len(unusedTilecodes) != 0:
        return unusedTilecodes.pop()
    return False

def replaceTilecodeInRooms(levelStr, shortTilecode, replaceTilecode):
    room_matches = reRooms.finditer(levelStr)
    for room in room_matches:
        start, end = room.span(1)
        roomtiles = room.group(1)
        #print(roomtiles)
        roomtiles = roomtiles.replace(shortTilecode, replaceTilecode)
        #print(roomtiles)
        levelStr = levelStr[:start] + roomtiles + levelStr[end:]
    return levelStr

def replaceTilecodes(str, match, shortTilecode, longTilecode, replaceTilecode=None):
    if replaceTilecode is None:
        replaceTilecode = getUnusedTilecode()
        if not replaceTilecode:
            print("ERROR, NO TILECODES")
            return str
        shortTilecodesMap[replaceTilecode] = longTilecode
        longTilecodesMap[longTilecode] = replaceTilecode
    print(shortTilecode, replaceTilecode)
    pos, _ = match.span(2)
    #print(pos)
    str = str[:pos] + replaceTilecode + str[pos+1:]
    #roomsget = "\/\/ room(?:\n\\!.*)?\n*([\s\S]*?)\n(?:\n|$)"
    str = replaceTilecodeInRooms(str, shortTilecode, replaceTilecode)
    return str

def fixTilecodes(str, inheritedTilecodes, saveTilecodes):
    matches = reTilecodeDefs.finditer(str)
    shortTilecodes = {}
    for match in matches:
        shortTilecode = match.group(2)
        longTilecode = match.group(1)
        shortTilecodes[shortTilecode] = longTilecode
        if longTilecode in longTilecodesMap:
            if shortTilecode != longTilecodesMap[longTilecode]: #if the short tilecode isn't the same
                print('found longTilecode "' + shortTilecode + '", ' + longTilecode + " | " + "replacing with: ", end="")
                str = replaceTilecodes(str, match, shortTilecode, longTilecode, longTilecodesMap[longTilecode])
            else:
                pass
                print('found longTilecode with same shortTilecode', shortTilecode, longTilecodesMap[longTilecode])
        elif shortTilecode in shortTilecodesMap:
            if longTilecode != shortTilecodesMap[shortTilecode]:
                print('tilecode "' + shortTilecode + '", ' + longTilecode + '" used with "' + shortTilecodesMap[shortTilecode] + '"', end=" | " )
                str = replaceTilecodes(str, match, shortTilecode, longTilecode)
        else:
            shortTilecodesMap[shortTilecode] = longTilecode
            longTilecodesMap[longTilecode] = shortTilecode
            unusedTilecodes.remove(shortTilecode)
    
    for short, long in inheritedTilecodes.items():
        if not short in shortTilecodes and long in longTilecodesMap and short != longTilecodesMap[long]:
            print("REPLACING INHERIT", short, long, longTilecodesMap[long])
            str = replaceTilecodeInRooms(str, short, longTilecodesMap[long])
    if saveTilecodes:
        newTilecodes = {**shortTilecodes, **inheritedTilecodes}
        return str, newTilecodes
    return str, shortTilecodes

def replaceWithAllFoundTilecodes(level, newTilecodesStr):
    print("\n\n\n", level, newTilecodesStr)
    return reReplaceAllTilecodeDefs.sub(newTilecodesStr, level)

def readFile(filePath):
    f = open(filePath, "r", encoding="latin-1")
    text = f.read()
    f.close()
    return text

try:
    mkdir("./Created")
except OSError as error:
    print(error)

newFilesText = {}
#print(listdir(mypath))

#not used
def fixAllFiles():
    files = [f for f in listdir(mypath) if ".lvl" in f]
    for filename in files:
        print("FILE ", filename)
        text = readFile(mypath + filename)
        newFilesText[filename] = fixTilecodes(text)
        #f = open(mypath + filename, "r", encoding="latin-1")
        #text = f.read()
        #newFilesText[filename] = fixTilecodes(text)
        #f.close()
#fixAllFiles()

def fixAllInList(levelList, inheritedTilecodes = {}):
    for level in levelList:
        filename = level["file"]
        print("FILENAME", filename, level)
        text = readFile(mypath + filename)
        if "contents" in level:
            newFilesText[filename], newTilecodes = fixTilecodes(text, inheritedTilecodes, True)
            fixAllInList(level["contents"], newTilecodes)
        else:
            newFilesText[filename], _ = fixTilecodes(text, inheritedTilecodes, False)
fixAllInList(levels)

def getShortTilecodesStr():
    text = ""
    for shortTilecode, longTilecode in shortTilecodesMap.items():
        text += "\?" + longTilecode + " " + shortTilecode + "\n"
    return text

allTileCodesText = getShortTilecodesStr()
print(allTileCodesText)#shortTilecodesMap)
#print("newFilesText", newFilesText)
for filename, newText in newFilesText.items():
    newText = replaceWithAllFoundTilecodes(newText, allTileCodesText)
    f = open("./Created/" + filename, "w", encoding="latin-1")
    f.write(newText)
    f.close()
