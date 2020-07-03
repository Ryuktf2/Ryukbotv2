import re
from sprint import *

# Activates the color in the console without this there would be no colors
colorama.init()

modOptions = {
    "prefix": "modPrefix",
    "suffix": "modSuffix",
    "run": "modCommands"
}

def getModOptions():
    return modOptions

def checkMods(ryukbot_settings, event, mod_properties):
    rbcParse = re.compile(r"(run|prefix|suffix) \'(.*)\' on \'(killstreak|bookmark)\' value \'(.*)\'", re.IGNORECASE)
    if ryukbot_settings["mods"]:
        for mod in ryukbot_settings["mods"]:
            try: 
                code = rbcParse.search(mod["code"])
            except: 
                eprint('Mod lacking code or it is incorrectly coded', 431)
            
            #* These are the results of the regex
            # code.group()  =>  suffix 'LOL' on 'killstreak' value '69'
            # code.group(1) =>  suffix
            # code.group(2) =>  LOL
            # code.group(3) =>  killstreak
            # code.group(4) =>  69
            
            type = False
            
            if (code.group(3).lower() == 'bookmark' and event[1].lower() == 'bookmark'):
                type = True
            elif (code.group(3).lower() == 'killstreak' and (event[1].lower() == 'killstreak' or event[1].lower() == 'kill')):
                type = True

            if type and event[2].lower() == code.group(4).lower():
                for key in modOptions.keys():
                    if code.group(1).lower() == key.lower():
                        mod_properties[modOptions[key]] = code.group(2)
                    
                        
    return mod_properties