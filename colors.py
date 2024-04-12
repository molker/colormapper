from PIL import Image
import json
import configparser
import os
import re

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


def createColorMap(orgcolorlist, newcolorlist):
    if len(orgcolorlist) != len(newcolorlist):
        raise ValueError('images for #'+name+' do not have matching amount of nontransparant pixels org: ' +
                         str(len(orgcolorlist))+' new: '+str(len(newcolorlist)))
    colormap = {}
    for i in range(len(orgcolorlist)):
        if (orgcolorlist[i] in colormap):
            if (colormap[orgcolorlist[i]] != newcolorlist[i]):
                raise ValueError(orgcolorlist[i] + ' is already mapped to ' +
                                 colormap[orgcolorlist[i]] + ' but tried to also map to: ' + newcolorlist[i])
        else:
            colormap[orgcolorlist[i]] = newcolorlist[i]
    return colormap    

def runColorMapper(orgfolder, inputfolder, backFolder ="", expFolder=""):
    
    inputfolder = os.path.join(inputfolder,expFolder, backFolder)

    filesToProcess = {}
    for file in os.listdir(inputfolder):
        filename = os.fsdecode(file)
        if filename.endswith(".png"):
            idvariant = re.findall(r"([0-9]+[^_.]*)", filename)
            id = idvariant[0]
            variant = idvariant[1]

            if (id in filesToProcess):
                filesToProcess[id].append(variant)
            else:
                filesToProcess[id] = [variant]


    for id, variants in filesToProcess.items():
        colormapcollection = {}
        # use exp folder for mega/gigantamax
        orgimagepath = (os.path.join(orgfolder, expFolder ,backFolder, (id+".png")))
        

        orgcolorlist = getColoredPixels(Image.open(orgimagepath))

        for variant in variants:
            inputimagepath = (os.path.join(inputfolder, (id+"_"+variant+".png")))
            newcolorlist = getColoredPixels(Image.open(inputimagepath))
            colormapcollection[int(
                variant)-1] = createColorMap(orgcolorlist, newcolorlist)

        with open(os.path.join(inputfolder, id+".json"), "w") as fp:
            json.dump(colormapcollection, fp)



config = configparser.ConfigParser()
config.read('config.ini')
inputfolder = (config['CONFIG']['inputfolder'])
orgfolder = (config['CONFIG']['originalfolder'])

runColorMapper(orgfolder,inputfolder)
runColorMapper(orgfolder, inputfolder,backFolder="back")
runColorMapper(orgfolder, inputfolder,expFolder="exp")
runColorMapper(orgfolder, inputfolder,expFolder="exp", backFolder="back")



      




      

