from os import mkdir, listdir
from os.path import isfile
import re
mypath = "./Created/"
reTemplates = re.compile(r"\\\.([^\s\n/]*).*\n\/*\n\n([\s\S]*?)(?:(?:\/\/\/)|$)")#(r"\\\.([^\s\n/]*).*\n\/*\n[\s\S]*?(?:(?:\/\/\/)|$)")
reRooms = re.compile(r"((?:\\!.*\n)*)\n*([\s\S]*?)\n(?:\n|$)")#(r"(\\!.*\n)*\n*([\s\S]*?)\n(?:\n|$)")#(r"\/\/ room(?:\n\\!.*)*\n*([\s\S]*?)\n(?:\n|$)")
templates = {}
templatesAllStr = {}
levels = {}
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
templateSeparator = "////////////////////////////////////////////////////////////////////////////////"

def tryMakeDir(str):
    try:
        mkdir(str)
    except OSError as error:
        print(error)

def getTemplateRooms(level):
    templateMatches = reTemplates.finditer(level)
    for templateMatch in templateMatches:
        templateName = templateMatch.group(1)
        templateRooms = templateMatch.group(2)
        print(templateName)
        if templateRooms[-1] != "\n":
            templateRooms += "\n"
        roomMatches = reRooms.finditer(templateRooms)
        for roomMatch in roomMatches:
            #print(roomMatch)
            if roomMatch.group(1):
                roomStr = roomMatch.group(1) + roomMatch.group(2)
            else:
                roomStr = roomMatch.group(2)
            if templateName in templates:
                templates[templateName].append(roomStr)
            else:
                templates[templateName] = [roomStr]

#files = [f for f in listdir('.') if isfile(f) and ".lvl" in f]
files = [f for f in listdir(mypath) if ".lvl" in f]

for filename in files:
    print("FILE ", filename)
    f = open(mypath + filename, "r", encoding="latin-1")
    lvl = f.read()
    getTemplateRooms(lvl)
    levels[filename] = lvl
    f.close()

tryMakeDir("./Templates")

##print(templates)

#start1 = ""
#start2 = ""
#roomStart = "\n"
#roomEnd = "\n"
#end = ""
file_ext = "lua"

def exportMixedTemplate():
    text = ""
    start1 =  "local rooms_"
    start2 =  " = {"
    roomStart = "\n[["
    roomEnd = "]],"
    end = "\n}\nreturn rooms_"
    for template_name, rooms in templates.items():
        #print(template_name)
        template_name = template_name.upper()
        template_text = ""
        #text += "\n" + template_name + " = {"
        template_text += start1 + template_name + start2
        for room in rooms:
            #print(room)
            #text += "\n[[" + room + "]],"
            template_text += roomStart + room + roomEnd
        template_text += end + template_name
        f = open("./Templates/TEMPLATES_" + template_name + "." + file_ext, "w", encoding="latin-1")
        f.write(template_text)
        text += template_text
    #print(text, templates)
    f = open("./TEMPLATES_GENERATED.txt", "w", encoding="latin-1")
    #writing = f"{templates}"
    f.write(text)
    f.close()
#exportMixedTemplate()

def changeLevelTemplate(level, templateName, roomsStr):
    roomsStr = "\." + templateName + "\n" + templateSeparator + "\n\n" + roomsStr + "\n\n"
    level = re.sub(r"\\\.(" + templateName + r"\b).*\n\/*\n\n([\s\S]*?)(?:(?:\/\/\/)|$)", roomsStr, level)
    #print(level)
    return level

tryMakeDir("./mixed")

for index, value in templates.items():
    print(index)

def fixTemplates():
    templates["exit"][:] = [room for room in templates["exit"] if "8" in room or "9" in room]
fixTemplates()

for levelName, level in levels.items():
    if levelName == "tiamat.lvl":
        continue
    if not ("\\.chunk_air" in level):
        level += f"\n{templateSeparator}\n\\.chunk_air\n{templateSeparator}\n\n"
    if not ("\\.chunk_ground" in level):
        level += f"\n{templateSeparator}\n\\.chunk_ground\n{templateSeparator}\n\n"
    if not ("\\.chunk_door" in level):
        level += f"\n{templateSeparator}\n\\.chunk_door\n{templateSeparator}\n\n"
    for templateName in toChangeTemplates:
        level = changeLevelTemplate(level, templateName, "\n\n".join(templates[templateName]))
    f = open("./mixed/" + levelName, "w", encoding="latin-1")
    f.write(level)
    f.close()

import shutil

shutil.copyfile("./Created/tiamat.lvl", "./mixed/tiamat.lvl")
