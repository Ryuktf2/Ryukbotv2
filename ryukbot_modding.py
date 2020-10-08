import re
from sprint import *

# Activates the color in the console without this there would be no colors
colorama.init()

modOptions = {
    "prefix": "modPrefix",
    "suffix": "modSuffix",
    "run": "modCommands",
    "framerate": "modFramerate",
    "fps": "modFramerate",
    "crosshair": "modCrosshair",
    "hud": "modHud",
    "text_chat": "modText_chat",
    "textchat": "modText_chat",
    "voice_chat": "modVoice_chat",
    "voicechat": "modVoice_chat",
    "spectate": "modSpectate",
    "end_commands": "modEndCommands",
    "endcommands": "modEndCommands"
}

def getModOptions():
    return modOptions

def checkMods(ryukbot_settings, event, mod_properties):
    rbcParse = re.compile(r"(.*) \'(.*)\' on \'(killstreak|bookmark|\*)\'( value | unless )?(\'(.*)\')?", re.IGNORECASE)
    if "mods" in ryukbot_settings:
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
            # code.group(4) =>  value   (might not be there)
            # code.group(5) =>  69      (might not be there)
            
            # Sets base values for the comparisons later
            type = False
            valid = False
                
            # If any code was found at all
            if code.group(1).lower() in modOptions if code.group() else False:
                
                # Check if the type matches the type of the clip
                if ((codeLower := code.group(3).lower()) == 'bookmark' and (eventLower := event[1].lower()) == 'bookmark'):
                    type = True
                elif (codeLower == 'killstreak' and (eventLower == 'killstreak' or eventLower == 'kill')):
                    type = True
                elif (codeLower == '*'):
                    type = True
                
                # Only run if the types match
                if type:
                    # if the value section doesnt exist default to any value 
                    if code.group(5) is None:
                        valid = True
                    else:
                        # checks if it should run when it matches or when it doesnt match
                        if code.group(4) == ' value ':
                            if (event[2].lower() == code.group(5).lower().replace("'", "")) or (code.group(5).lower().replace("'", "") == '*'):
                                valid = True
                        elif code.group(4) == ' unless ':
                            if not event[2].lower() == code.group(5).lower().replace("'", ""):
                                valid = True
                    
                    # run if fully valid on all ends
                    if valid:
                        if code.group(2).lower() == '[type]':
                            mod_properties[modOptions[code.group(1).lower()]] = event[1]
                        elif code.group(2).lower() == '[value]':
                            mod_properties[modOptions[code.group(1).lower()]] = event[2]
                        else:
                            mod_properties[modOptions[code.group(1).lower()]] = code.group(2)
                    
                        
    return mod_properties