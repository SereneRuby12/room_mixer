from os import mkdir, listdir
from os.path import isfile
import re

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
                },
                {
                    "file": "challenge_moon.lvl",
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
                },
                {
                    "file": "challenge_star.lvl",
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
    print("ERROR, NO TILECODES")
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
            return str
        shortTilecodesMap[replaceTilecode] = longTilecode
        longTilecodesMap[longTilecode] = replaceTilecode
    print(replaceTilecode)
    pos, _ = match.span(2)
    str = str[:pos] + replaceTilecode + str[pos+1:]
    str = replaceTilecodeInRooms(str, shortTilecode, replaceTilecode)
    return str

def fixTilecodes(str, inheritedTilecodes, saveTilecodes):
    lastUTilecode = 257
    uTilecodesMap = {}
    matches = reTilecodeDefs.finditer(str)
    shortTilecodes = {}
    for match in matches:
        shortTilecode = match.group(2)
        longTilecode = match.group(1)
        shortTilecodes[shortTilecode] = longTilecode
        if longTilecode in longTilecodesMap:
            if shortTilecode != longTilecodesMap[longTilecode]: #if the short tilecode isn't the same
                print('found longTilecode "' + shortTilecode + '", ' + longTilecode + " | " + "replacing with: ", end="")
                uTilecodesMap[chr(lastUTilecode)] = longTilecodesMap[longTilecode]
                str = replaceTilecodes(str, match, shortTilecode, longTilecode, chr(lastUTilecode))
            else:
                print('found longTilecode with same shortTilecode', shortTilecode, longTilecodesMap[longTilecode])
                pass
        elif shortTilecode in shortTilecodesMap:
            if longTilecode != shortTilecodesMap[shortTilecode]:
                print('tilecode "' + shortTilecode + '", ' + longTilecode + '" used with "' + shortTilecodesMap[shortTilecode] + '"', end=" | " )
                replaceTilecode = getUnusedTilecode()
                shortTilecodesMap[replaceTilecode] = longTilecode
                longTilecodesMap[longTilecode] = replaceTilecode

                uTilecodesMap[chr(lastUTilecode)] = replaceTilecode
                str = replaceTilecodes(str, match, shortTilecode, longTilecode, chr(lastUTilecode))
        else:
            shortTilecodesMap[shortTilecode] = longTilecode
            longTilecodesMap[longTilecode] = shortTilecode
            unusedTilecodes.remove(shortTilecode)
            uTilecodesMap[chr(lastUTilecode)] = shortTilecode
        lastUTilecode += 1
    
    for short, long in inheritedTilecodes.items():
        if not short in shortTilecodes and long in longTilecodesMap and short != longTilecodesMap[long]:
            print("REPLACING INHERIT", short, long, longTilecodesMap[long])
            uTilecodesMap[chr(lastUTilecode)] = longTilecodesMap[long]
            str = replaceTilecodeInRooms(str, short, chr(lastUTilecode))
            lastUTilecode += 1
    
    for uTilecode, shortTilecode in uTilecodesMap.items():
        print("UTILECODE", uTilecode, shortTilecode)
        str = str.replace(uTilecode, shortTilecode)

    if saveTilecodes:
        newTilecodes = {**shortTilecodes, **inheritedTilecodes}
        return str, newTilecodes
    return str, shortTilecodes

def replaceWithAllFoundTilecodes(level, newTilecodesStr):
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

def fixAllInList(levelList, inheritedTilecodes = {}):
    for level in levelList:
        filename = level["file"]
        print("FILENAME", filename)
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
for filename, newText in newFilesText.items():
    newText = replaceWithAllFoundTilecodes(newText, allTileCodesText)
    f = open("./Created/" + filename, "w", encoding="latin-1")
    f.write(newText)
    f.close()