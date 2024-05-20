from PIL import Image
import json
import configparser
import os
import re
import shutil

def rgb2hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def getColoredPixels(img):
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        pixels = list(img.convert('RGBA').getdata())
        tempcolorlist = []
        for r, g, b, a in pixels:
            if (a != 0):  #ignore alpha pixels
                newhex = rgb2hex(r, g, b)
                newhex = newhex[1:]
                tempcolorlist.append(newhex)
        img.close()
        return tempcolorlist
    else:
        img.close()
        raise ValueError('This image does not have transparancy')


def createColorMap(orgcolorlist, newcolorlist,name):
    global spritereplacements
    if len(orgcolorlist) != len(newcolorlist):
        spritereplacements += 1
        print(name + ' is sprite replacement: does not have matching amount of nontransparant pixels org: ' +
                         str(len(orgcolorlist))+' new: '+str(len(newcolorlist)))
        return False
    colormap = {}
    for i in range(len(orgcolorlist)):
        if (orgcolorlist[i] in colormap):
            if (colormap[orgcolorlist[i]] != newcolorlist[i]):
                spritereplacements +=1
                print(name + " is sprite replacement: "+orgcolorlist[i] + ' is already mapped to ' +
                                 colormap[orgcolorlist[i]] + ' but tried to also map to: ' + newcolorlist[i])
                return False
        else:
            colormap[orgcolorlist[i]] = newcolorlist[i]
    return colormap    

def runColorMapper(masterlist, orgfolder, inputfolder, backFolder ="", expFolder="",femfolder="",iconsfolder=""):
    global highest
    highest = 0
    inputfolder = os.path.join(inputfolder, iconsfolder, expFolder, backFolder, femfolder)
    variantfolder = os.path.join(variantpath, iconsfolder, expFolder, backFolder, femfolder)
    if (os.path.exists(inputfolder) != True):
        os.makedirs(inputfolder, exist_ok=True)
        return {}
    newmasterlist = masterlist

    filesToProcess = {}
    for file in os.listdir(inputfolder):
        filename = os.fsdecode(file)
        if filename.endswith(".png"):
            idvariant = re.findall(r"([0-9]+[^_.]*)", filename)
            id = idvariant[0]
            newmasterlist[id] = masterlist[id] if id in masterlist else [0,0,0]
            try:
                variant = idvariant[1]
            except:
                wrongfiles.append(os.path.join(inputfolder,file))
                break

            if (id in filesToProcess):
                filesToProcess[id].append(variant)
            else:
                filesToProcess[id] = [variant]


    for id, variants in filesToProcess.items():
        colormapcollection = {}
        # use exp folder for mega/gigantamax
        orgimagepath = (os.path.join(orgfolder,iconsfolder, expFolder, backFolder, femfolder,(id+".png")))
        orgjsonpath = (os.path.join(orgfolder, iconsfolder,
                        expFolder, backFolder, femfolder, (id+".json")))

        orgcolorlist = getColoredPixels(Image.open(orgimagepath))

        for variant in variants:
            inputimagepath = (os.path.join(inputfolder, (id+"_"+variant+".png")))
            newcolorlist = getColoredPixels(Image.open(inputimagepath))
            tempcolormap = createColorMap(orgcolorlist, newcolorlist,inputimagepath.replace(zinputfolder+'\\',''))
            if tempcolormap:
                variantfilepath = os.path.join(variantfolder, id+".json")
                variantjsonexists = os.path.isfile(variantfilepath)
                if variantjsonexists:
                    variantfile = open(variantfilepath)
                    variantjson = json.load(variantfile)
                    colormapcollection = variantjson
                    variantfile.close()
                colormapcollection[str(int(variant)-1)] = tempcolormap
                newmasterlist[id][int(variant)-1] = 1
                outputfolder = inputfolder.replace('input', 'output')
                os.makedirs(outputfolder, exist_ok=True)
                with open(variantfilepath, "w") as fp:
                    json.dump(dict(sorted(colormapcollection.items())), fp,indent="\t")
            else:
                newmasterlist[id][int(variant)-1] = 2
                outputfolder = inputfolder.replace('input', 'output')
                os.makedirs(outputfolder, exist_ok=True)
                shutil.copyfile(inputimagepath, os.path.join(variantfolder, id+"_"+variant+".png"))

                with open(os.path.join(orgjsonpath), "r") as fp:
                    atlas = json.load(fp)
                    atlas["textures"][0]["image"] = id+"_"+variant+".png"
                    with open(os.path.join(os.path.join(
                    variantfolder, id+"_"+variant+".json")), "w") as fp:
                        json.dump(atlas,fp,indent="\t")
        
    
    return dict(sorted(newmasterlist.items(), key=findid))

def findid(key):
    global highest
    try:
        numbers = re.findall(r"([0-9]+)",key[0])[0]
    except IndexError:
        numbers = str(highest + 1)
    # specifically for making sure sub-objects (i.e. female, back) stay last where they have been
    highest = int(numbers) if int(numbers) > highest else highest
    return int(numbers)

def createMasterList(path):
    with open(path, "w") as fp:
        json.dump(newMasterList, fp, indent="\t")




config = configparser.ConfigParser()
config.read('config.ini')
inputfolder = (config['CONFIG']['inputfolder'])
zinputfolder = (config['CONFIG']['inputfolder'])
orgfolder = (config['CONFIG']['originalfolder'])
masterListPath = orgfolder + "/variant/_masterlist.json"
variantpath = orgfolder + "/variant"
masterListFile = open(masterListPath)
masterlist = json.load(masterListFile)
newMasterList = {}
newsprites = {}
spritereplacements = 0
highest = 0
# not a variant
wrongfiles = []

#now that we have so many folders.. at this point should rewrite to dynamically get folderstructure
newMasterList = runColorMapper(masterlist, orgfolder, inputfolder)
newMasterList["female"] = runColorMapper(masterlist["female"], orgfolder, inputfolder, femfolder="female")


newMasterList["back"] = runColorMapper(masterlist["back"], orgfolder, inputfolder, backFolder="back")
newMasterList["back"]["female"] = runColorMapper(masterlist["back"]["female"], orgfolder, inputfolder, femfolder="female", backFolder="back")

newMasterList["exp"] = runColorMapper(masterlist["exp"], orgfolder, inputfolder, expFolder="exp")
newMasterList["exp"]["female"]=runColorMapper(masterlist["exp"]["female"], orgfolder, inputfolder, femfolder="female", expFolder="exp")

newMasterList["exp"]["back"]=runColorMapper(masterlist["exp"]["back"], orgfolder, inputfolder, expFolder="exp", backFolder="back")


#female back exp images dont exist
#runColorMapper(orgfolder, inputfolder, expFolder="exp",femfolder="female",  backFolder="back")

createMasterList(masterListPath)

print("Finished \nSprite replacements: "+str(spritereplacements)+"\nWrong files:")
for i in wrongfiles:
    print(i)







      




      

