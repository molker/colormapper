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
    if len(orgcolorlist) != len(newcolorlist):
        print(name + ' is sprite replacement: does not have matching amount of nontransparant pixels org: ' +
                         str(len(orgcolorlist))+' new: '+str(len(newcolorlist)))
        return False
    colormap = {}
    for i in range(len(orgcolorlist)):
        if (orgcolorlist[i] in colormap):
            if (colormap[orgcolorlist[i]] != newcolorlist[i]):
                print(name + " is sprite replacement: "+orgcolorlist[i] + ' is already mapped to ' +
                                 colormap[orgcolorlist[i]] + ' but tried to also map to: ' + newcolorlist[i])
                return False
        else:
            colormap[orgcolorlist[i]] = newcolorlist[i]
    return colormap    

def runColorMapper(orgfolder, inputfolder, backFolder ="", expFolder="",femfolder="",iconsfolder=""):
    
    inputfolder = os.path.join(inputfolder, iconsfolder, expFolder,  backFolder,femfolder)
    if (os.path.exists(inputfolder) != True):
        os.makedirs(inputfolder, exist_ok=True)
        return {}
    newmasterlist = {}

    filesToProcess = {}
    for file in os.listdir(inputfolder):
        filename = os.fsdecode(file)
        if filename.endswith(".png"):
            idvariant = re.findall(r"([0-9]+[^_.]*)", filename)
            id = idvariant[0]
            newmasterlist[id] = [0,0,0]
            variant = idvariant[1]

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
                colormapcollection[int(variant)-1] = tempcolormap
                newmasterlist[id][int(variant)-1] = 1
                outputfolder = inputfolder.replace('input', 'output')
                os.makedirs(outputfolder, exist_ok=True)
                with open(os.path.join(outputfolder, id+".json"), "w") as fp:
                    json.dump(colormapcollection, fp,indent="\t")
            else:
                newmasterlist[id][int(variant)-1] = 2
                outputfolder = inputfolder.replace('input', 'output')
                os.makedirs(outputfolder, exist_ok=True)
                shutil.copyfile(inputimagepath, os.path.join(outputfolder, id+"_"+variant+".png"))
                #shutil.copyfile(os.path.join(orgfolder,id+".json"), os.path.join(outputfolder, id+"_"+variant+".json"))
                with open(os.path.join(orgjsonpath), "r") as fp:
                    atlas = json.load(fp)
                    atlas["textures"][0]["image"] = id+"_"+variant+".png"
                    with open(os.path.join(os.path.join(
                    outputfolder, id+"_"+variant+".json")), "w") as fp:
                        json.dump(atlas,fp,indent="\t")
        
                

    return dict(sorted(newmasterlist.items(), key=findid))

def findid(key):
    numbers = re.findall(r"([0-9]+)",key[0])[0]
    return int(numbers)

def createMasterList(inputfolder):
    outputfolder = inputfolder.replace('input', 'output')
    os.makedirs(outputfolder, exist_ok=True)
    with open(os.path.join(outputfolder, "_masterlist.json"), "w") as fp:
        json.dump(masterlist, fp, indent="\t")




config = configparser.ConfigParser()
config.read('config.ini')
inputfolder = (config['CONFIG']['inputfolder'])
zinputfolder = (config['CONFIG']['inputfolder'])
orgfolder = (config['CONFIG']['originalfolder'])
masterlist = {}
newsprites = {}

#now that we have so many folders.. at this point should rewrite to dynamically get folderstructure
masterlist = runColorMapper(orgfolder, inputfolder)
masterlist["female"] = runColorMapper(orgfolder, inputfolder, femfolder="female")


masterlist["back"] = runColorMapper(orgfolder, inputfolder, backFolder="back")
masterlist["back"]["female"] = runColorMapper(
    orgfolder, inputfolder, femfolder="female", backFolder="back")

masterlist["exp"] = runColorMapper(orgfolder, inputfolder, expFolder="exp")
masterlist["exp"]["female"]=runColorMapper(orgfolder, inputfolder, femfolder="female", expFolder="exp")

masterlist["exp"]["back"]=runColorMapper(orgfolder, inputfolder, expFolder="exp", backFolder="back")


#female back exp images dont exist
#runColorMapper(orgfolder, inputfolder, expFolder="exp",femfolder="female",  backFolder="back")

createMasterList(zinputfolder)







      




      

