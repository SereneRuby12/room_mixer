from os import mkdir, listdir
from enum import IntEnum
import re
inPath = "./Created/"
reTemplates = re.compile(r"\\\.([^\s\n/]*).*\n\/*\n\n([\s\S]*?)(?:(?:\/\/\/)|$)")
reRooms = re.compile(r"\n*((?:\\!.*\n)*)\n*([\s\S]*?)\n(?:\n|$)")
templates = []
templatesAllStr = {}
filesDict = {}
toChangeTemplates = [
    "entrance",
    "entrance_drop",
    "exit",
    "exit_notop",
    "path_drop",
    "path_drop_notop",
    "path_normal",
    "path_notop",
    "side",
    "machine_bigroom_path",
    "machine_bigroom_side",
    "machine_wideroom_path",
    "machine_wideroom_side",
    "machine_tallroom_path",
    "machine_tallroom_side",
    "machine_keyroom",
    "machine_rewardroom",
    "chunk_ground",
    "chunk_air",
    "chunk_door"
]
sunkenExitsNotop = []

class ROOM_TYPE(IntEnum):
    NORMAL = 0
    DUAL = 1
    LIQUID = 2
    INVERSE_LIQUID = 3

for n in range(4):
    templates.append({})
    for template in toChangeTemplates:
        templates[n][template] = []

templateSeparator = "////////////////////////////////////////////////////////////////////////////////"

def tryMakeDir(str):
    try:
        mkdir(str)
    except OSError as error:
        print(error)

def getTemplateRooms(level, filename):
    liquidRoomType = ROOM_TYPE.INVERSE_LIQUID if "sunken" in filename or filename == "hundun.lvl" else ROOM_TYPE.LIQUID
    templateMatches = reTemplates.finditer(level)
    for templateMatch in templateMatches:
        templateName = templateMatch.group(1)
        templateRooms = templateMatch.group(2)
        if not templateName in toChangeTemplates or (
            filename == "duat.lvl" and templateName == "entrance_drop"):
                continue
        print(templateName)
        if templateRooms[-1] != "\n":
            templateRooms += "\n"
        roomMatches = reRooms.finditer(templateRooms)
        if templateName == "exit_notop" and (filename == "sunkencityarea.lvl" or filename == "hundun.lvl"):
            for roomMatch in roomMatches:
                room = roomMatch.group(1) + roomMatch.group(2)
                sunkenExitsNotop.append(room)
        else:
            for roomMatch in roomMatches:
                #print(roomMatch)
                tags, room = roomMatch.group(1), roomMatch.group(2)
                room = tags + room
                if "!liquid" in tags:
                    templates[liquidRoomType][templateName].append(room)
                elif "!dual" in tags:
                    templates[ROOM_TYPE.DUAL][templateName].append(room)
                else:
                    templates[ROOM_TYPE.NORMAL][templateName].append(room)

files = [f for f in listdir(inPath) if ".lvl" in f]

for filename in files:
    print("FILE ", filename)
    f = open(inPath + filename, "r", encoding="latin-1")
    lvl = f.read()
    getTemplateRooms(lvl, filename)
    filesDict[filename] = lvl
    f.close()

def changeLevelTemplate(level, templateName, roomsStr):
    roomsStr = "\." + templateName + "\n" + templateSeparator + "\n\n" + roomsStr + "\n\n"
    level = re.sub(r"\\\.(" + templateName + r"\b).*\n\/*\n\n([\s\S]*?)(?:(?:\/\/\/)|$)", roomsStr, level)
    return level

tryMakeDir("./mixed")

def fixTemplates():
    templates[ROOM_TYPE.NORMAL]["exit"][:] = [room for room in templates[ROOM_TYPE.NORMAL]["exit"] if "8" in room or "9" in room]
fixTemplates()

for filename, level in filesDict.items():
    if filename == "tiamat.lvl":
        continue
    isSunkenLevel = "sunken" in filename or filename == "hundun.lvl"
    if filename != "generic.lvl":
        if not ("\\.chunk_air" in level):
            level += f"\n{templateSeparator}\n\\.chunk_air\n{templateSeparator}\n\n"
        if not ("\\.chunk_ground" in level):
            level += f"\n{templateSeparator}\n\\.chunk_ground\n{templateSeparator}\n\n"
        if not ("\\.chunk_door" in level):
            level += f"\n{templateSeparator}\n\\.chunk_door\n{templateSeparator}\n\n"
    for templateName in toChangeTemplates:
        templateRooms = []
        if templateName == "exit_notop" and isSunkenLevel:
            templateRooms.extend(sunkenExitsNotop)
        else:
            templateRooms.extend(templates[ROOM_TYPE.NORMAL][templateName])
        if isSunkenLevel:
            templateRooms.extend(templates[ROOM_TYPE.INVERSE_LIQUID][templateName])
        elif filename != "icecavesarea.lvl":
            templateRooms.extend(templates[ROOM_TYPE.LIQUID][templateName])
        
        if not ("cosmicocean" in filename or "duat" in filename):
            templateRooms.extend(templates[ROOM_TYPE.DUAL][templateName])
        level = changeLevelTemplate(level, templateName, "\n\n".join(templateRooms))
    f = open("./mixed/" + filename, "w", encoding="latin-1")
    f.write(level)
    f.close()

import shutil

shutil.copyfile("./Created/tiamat.lvl", "./mixed/tiamat.lvl")
