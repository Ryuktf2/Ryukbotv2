#! python3
##importing things (self explanitory)
from datetime import datetime as dt
from pathlib import Path
import re
import json
import sys
import os
import colorama
from random import randint
from termcolor import cprint
from ryukbot_installer import *
import ryukbot_settings
from ryukbot_maker import _eventMaker
from yesNo import yesNo
from sprint import *
from ryukbot_modding import checkMods, getModOptions

# Activates the color in the console without this there would be no colors
colorama.init()

ryukbot_version = 'v2.0.7'

# Color Coding ruleset:
# grey: 
# red:      Errors and the messages associated
# green:    Ran successfully
# yellow:   Warning labels or important notices
# blue:     
# magenta:  Important but not an error or title
# cyan:     Titles/System messages
# white:    Normal paragraph messages/descriptions of things

setting_descriptions = ryukbot_settings.descriptions()
modOptions = getModOptions()
    

def checkSetting(setting, setting_descriptions):
    """Checks the settings file and makes sure its all valid

    Args:
        setting (string):               The key name of the specific setting being checked
        setting_descriptions (object):  The settings information

    Returns:
        Boolean: returns the value of the setting
    """
    
    if setting in ryukbot_settings:
        if (type := setting_descriptions['type']) == 'integer' or type == 'boolean':
            if str(ryukbot_settings[setting]).isdigit():
                if type == 'boolean':
                    if ryukbot_settings[setting] == 1 or ryukbot_settings[setting] == 0:
                        ryukbot_settings[setting] = True if ryukbot_settings[setting] == 1 else False
                        return ryukbot_settings[setting]
                    else:
                        eprint(ryukbot_settings, f'{setting} is incorrectly set up (should be a 1 or 0)', 204)
                else: 
                    return ryukbot_settings[setting]
                    
            else:
                eprint(ryukbot_settings, f'{setting} is incorrectly set up (should be a number)', 205)
        else: 
            if isinstance(ryukbot_settings[setting], str):
                return ryukbot_settings[setting]
            else:
                eprint(ryukbot_settings, f'{setting} is incorrectly set up (should be wrapped in quotes)', 203)
    else:
        cprint(f'{setting} is missing from ryukbot_settings.json', 'red')
        # eprint(ryukbot_settings, f'{setting} is missing from ryukbot_settings.json\nDefault value is: {setting_descriptions["default"]}', 201)
        return missingSettingText(setting_descriptions, setting)
        
def settingRundown():
    """
        Runs all of the settings in one place
    """
    changed = False
    for key in setting_descriptions:
        ryukbot_settings[key] = checkSetting(key, setting_descriptions[key])
        
    printSettings = ryukbot_settings
    for key in ryukbot_settings:
        if ryukbot_settings[key] == True or ryukbot_settings[key] == False:
            printSettings[key] = 1 if ryukbot_settings[key] else 0
        
    with open(Path('ryukbot_settings.json'), 'w+') as f:
        json.dump(ryukbot_settings, f, indent=4)
        
# Writes the start of a new command and adds one to the vdmCount variable
def newCommand(vdmCount, VDM):
    """Starts the initial command writing that is the same with all vdm commands

    Args:
        vdmCount (int):     The amount of vdm commands there are
        VDM (file):         The VDM file being written to

    Returns:
        int: The count with one more to account for the one just added
    """
    VDM.write('\t"%s"\n\t{\n\t\t' % (vdmCount))
    return vdmCount + 1

# Prints the body of the vdm for each clip to be recorded
def printVDM(VDM, demoName, startTick, endTick, suffix, lastTick, vdmCount, mod_effects):
    """Prints the body of the vdm for each clip to be recorded

    Args:
        VDM (file):         The file being written to
        demoName (string):  The name of the demo file minus the extension
        startTick (int):    The tick the recording itself starts at
        endTick (int):      The tick the recording ends at
        suffix (string):    A string to add to the end of the clips filename
        lastTick (int):     The previous endTick
        vdmCount (int):     A count of how many vdm commands have been written

    Returns:
        int:    It returns the vdmCount at the end of the function so everything
                remains  consistent in that area throughout the entire 
                vdm printing process.
    """
    
    
    framerate = mod_effects["modFramerate"] if "modFramerate" in mod_effects else ryukbot_settings["framerate"]
    crosshair = mod_effects["modCrosshair"] if "modCrosshair" in mod_effects else ryukbot_settings["crosshair"]
    hud = mod_effects["modHud"] if "modHud" in mod_effects else ryukbot_settings["HUD"]
    text_chat = mod_effects["modText_chat"] if "modText_chat" in mod_effects else ryukbot_settings["text_chat"]
    voice_chat = mod_effects["modVoice_chat"] if "modVoice_chat" in mod_effects else ryukbot_settings["voice_chat"]
    endCommands = mod_effects["modEndCommands"] if "modEndCommands" in mod_effects else ryukbot_settings["end_commands"]
    
    
    # Starts the new command line
    try:
        vdmCount = newCommand(vdmCount, VDM)
        VDM.write('factory "SkipAhead"\n\t\tname "skip"\n\t\tstarttick "%s"\n\t\tskiptotick "%s"\n\t}\n'
                % (lastTick, startTick - 100))
        
        vdmCount = newCommand(vdmCount, VDM)
    except:
        eprint(ryukbot_settings, f'Error printing to {demoName}.vdm', 372)
    
    # sets the chatTime based on the settings
    if text_chat:
        chatTime = 0
    else:
        chatTime = 12
        
    # Creates the commands to later be written in the VDM file.
    try:
        preCommands = f' {mod_effects["modCommands"]}; {ryukbot_settings["commands"]}; ' if 'modCommands' in mod_effects else f' {ryukbot_settings["commands"]}; '
        commands = f'hud_saytext_time {chatTime}; voice_enable {1 if voice_chat else 0}; crosshair {1 if crosshair else 0}; cl_drawhud {1 if hud else 0}; host_framerate {framerate};{preCommands}'
        
        
        if 'modPrefix' in mod_effects:
            demoName = f'{mod_effects["modPrefix"]}_{demoName}'
            
        if 'modSuffix' in mod_effects:
            suffix = f'{suffix}_{mod_effects["modSuffix"]}'
            
        if 'modSpectate' in mod_effects:
            commands = f'{commands} spec_player {mod_effects["modSpectate"]}; spec_mode;'
            endCommands = f'{endCommands}; spec_mode; spec_mode'
            
        # Writes the bulk of the startmovie command
        VDM.write('factory "PlayCommands"\n\t\tname "record_start"\n\t\tstarttick "%s"\n\t\tcommands "%s startmovie %s_%s-%s_%s %s; clear"\n\t}\n'
                % (startTick, commands, demoName, startTick, endTick, suffix, ryukbot_settings["method"]))
    except: 
        eprint(ryukbot_settings, f'Error printing to {demoName}.vdm', 373)
    
    try:
        vdmCount = newCommand(vdmCount, VDM)
        VDM.write('factory "PlayCommands"\n\t\tname "record_stop"\n\t\tstarttick "%s"\n\t\tcommands "%s; endmovie; host_framerate 0"\n\t}\n'
                % (endTick, endCommands))
    except: 
        eprint(ryukbot_settings, f'Error printing to {demoName}.vdm', 374)
    
    return vdmCount + 1


def completeVDM(VDM, nextDemo, lastTick, vdmCount, demoName):
    """Ends the VDM file and optionally leads to the next demo if possible or toggled.

    Args:
        VDM (file):             The VDM to be written to
        nextDemo (string):      The name of the demo that happens after the current one.
        lastTick (int):         The last tick used by the VDM in the printing process
        vdmCount (int):         The count of vdm commands so far in the vdm
        demoName (string):      The name of the current demo
    """
    try:
        if nextDemo == 'end' or not ryukbot_settings["record_continuous"]:
            commands = 'quit'
        else: 
            commands = f'playdemo {nextDemo}'
        vdmCount = newCommand(vdmCount, VDM)
        VDM.write('factory "PlayCommands"\n\t\tname "VDM end"\n\t\tstarttick "%s"\n\t\tcommands "%s"\n\t}\n}'
                % (lastTick, commands))
    except:
        eprint(ryukbot_settings, f'Error printing to {demoName}.vdm', 379)


# Prints the backups to the folders told to
def writeBackup(backup_location, eventsPerDemo):
    """Prints the backups to the folders its told to

    Args:
        backup_location (Path):         The path to the backup .txt file
        eventsPerDemo (Array/List):     The list of events in each demo
    """
    try: 
        if backup_location.is_file():
            writeMethod = 'a'
        else: 
            writeMethod = 'w'
            
        with open(backup_location, writeMethod) as backup_file:
            backup_file.write('>\n')
            for demoEvent in eventsPerDemo:
                # Write the line to the backup
                backup_file.write('[%s] %s %s ("%s" at %s)\n' % (demoEvent))
    except:
        eprint(ryukbot_settings, 'Error while writing backup', 343)
            
# Returns the amount of ticks to put before the clip
def ticksPrior(event):
    """Finds the amount of ticks to put before the clip being analysed

    Args:
        event (Array/List):     A list returned from REGEX showing all the pieces of the event being parsed

    Returns:
        int: The amount of ticks to put before the current clip
    """
    if event[1].lower() == 'killstreak':
        return ryukbot_settings['before_killstreak_per_kill'] * int(event[2])
    else:
        return ryukbot_settings['before_bookmark']
      
# Returns the amount of ticks to put after the clip      
def ticksAfter(event):
    """Finds the amount of ticks to put after the clip being analysed

    Args:
        event (Array/List):     A list returned from REGEX showing all the pieces of the event being parsed

    Returns:
        int: The amount of ticks to put after the current clip
    """
    if event[1].lower() == 'killstreak':
        return ryukbot_settings['after_killstreak']
    else:
        return ryukbot_settings['after_bookmark']
    
def killstreakCounter(event, currentCount):
    """Counts the amount of kills in each killstreak

    Args:
        event (Array/List): A list returned from REGEX showing all the pieces of the event being parsed
        currentCount (int): The amount of kills in the killstreak already

    Returns:
        int: The amount of kills in the killstreak
    """
    try:
        if event[1].lower() == 'killstreak':
            if int(event[2]) >= int(currentCount + 1):
                return int(event[2])
            else:
                return currentCount + int(event[2])
        elif event[1].lower() == 'kill':
            if int(event[2].split(':')[1]) >= int(currentCount + 1):
                return int(event[2].split(':')[1])
            else:
                return currentCount + int(event[2].split(':')[1])
        else:
            return currentCount
    except:
        eprint(ryukbot_settings, 'Error counting killstreak amount', 405)
    
# Counts the amount of time bookmark is tapped
def tapCounter(event, nextEvent, tapCount):
    """Counts the amount of time bookmark is "tapped"

    Args:
        event (Array/List): A list returned from REGEX showing all the pieces of the event being parsed
        nextEvent (Array/List): The event after the current one
        tapCount (int): The amount of taps already

    Returns:
        int: The amount of times the bookmark button has been hit
    """
    if event[1].lower() == 'bookmark':
        if nextEvent[1].lower() == 'bookmark':
            if int(event[4]) + ryukbot_settings['interval_for_rewind_double_taps'] >= int(nextEvent[4]):
                tapCount += 1
    return tapCount
        
# Read _events.txt or killstreaks.txt file 
def ryukbot():
    """
        The base of the entire program
    """
    try:
        tf_folder = ryukbot_settings["tf_folder"]
        
        if Path(tf_folder + '\\demos\\_events.txt').is_file():
            tf_folder = tf_folder + '\\demos'
            eventFileName = '_events.txt'
        elif Path(tf_folder + '\\demos\\KillStreaks.txt').is_file():
            tf_folder = tf_folder + '\\demos'
            eventFileName = 'KillStreaks.txt'
        elif Path(tf_folder + '\\_events.txt').is_file():
            eventFileName = '_events.txt'
        elif Path(tf_folder + '\\KillStreaks.txt').is_file():
            eventFileName = 'KillStreaks.txt'
        else:
            eprint(ryukbot_settings, 'Can not find KillStreaks.txt or _event.txt', 331)
        
        eventFile = Path(f'{tf_folder}\\{eventFileName}')
            
        with open(eventFile, 'r') as _events:

            # Saving the file as an array/list variable
            eventLines = _events.readlines()
            
            # REGEX for future use
            lineRegex = re.compile('\[(.*)\] (kill|killstreak|bookmark|player) (.*) \("(.*)" at (\d*)\)', re.IGNORECASE)
            carrotRegex = re.compile('\n(\>)?\n')
            
            # Combines it into one string and searches it
            eventMarks = lineRegex.findall(''.join(eventLines))
            
            #* The syntax for getting the variables and its information
            # LINE: eventMarks[*]           --- EXAMPLE ('2020/04/27 20:23', 'Killstreak', '3', '2020-04-27_20-16-21', '29017')
            # DATE: eventMarks[*][0]        --- EXAMPLE 2020/04/27 20:23
            # TYPE: eventMarks[*][1]        --- EXAMPLE Killstreak 
            # CRITERIA: eventMarks[*][2]    --- EXAMPLE 3
            # DEMO: eventMarks[*][3]        --- EXAMPLE 2020-04-27_20-16-21
            # TICK: eventMarks[*][4]        --- EXAMPLE 29017
            
            # This is used later to check if the demo has changed to the next on the list
            try:
                demoName = eventMarks[0][3]
            except IndexError:
                cprint((f"{eventFileName} is empty"), 'red')
                print(f'Would you like to run the {eventFileName} maker?')
                if yesNo():
                    if _eventMaker(eventFile, eventFileName, ryukbot_settings['advanced_event_maker']):
                        os.system('cls')
                        cprint('Run Ryukbot now?\n', 'cyan')
                        if yesNo():
                            ryukbot()
                        else:
                            input("Press enter to close...")
                            os._exit(0)
                else:
                    input("Press enter to close...")
                    os._exit(0)
            
            # Simple message letting the user know the programs progress.
            # More updates to the user are nice but I want to try and limit spam to the user.
            cprint(f'Scanned {len(eventLines)} different events over the span of {len(carrotRegex.findall("".join(eventLines))) + 1} demos.', 'green')
            dprint(ryukbot_settings, f'Wow! You don\'t get many kills do you?', 'magenta', 68)
        
            allEvents = []
            eventsPerDemo = []
            # Loops through the list of events in the eventMarks list
            for event in eventMarks:
                # Checks if part of the same demo
                if demoName != event[3]:
                    # Appends to the allEvents list for later use
                    allEvents.append(eventsPerDemo)
                    
                    # resets the demoName
                    demoName = event[3]
                    
                    # resets the events
                    eventsPerDemo = []
                
                # Appends the current event to the end of the eventsPerDemo list
                eventsPerDemo.append(event)
                
            # Pushes the last demo to the allEvents list as the for loop above doesn't do it
            allEvents.append(eventsPerDemo)
            
            
            # Get current directory path and add the backups folder to the end as well as
            # Make the folder if it doesnt exist yet
            if not os.path.exists(dir_path := Path(tf_folder + '\\ryukbot_backups\\')):
                os.makedirs(dir_path)
                os.makedirs(Path((str(dir_path) + '\\demos\\')))
            elif not os.path.exists(Path((str(dir_path) + '\\demos\\'))):
                os.makedirs(Path((str(dir_path) + '\\demos\\')))
                
            # Saves the date time locally for naming purposes
            date_time = str(dt.now().date()) + '_' + str(dt.now().time()) + '.txt'
            
            
            demoIndex = 0
            while demoIndex < len(allEvents):
                demoEvents = allEvents[demoIndex]
                demoName = demoEvents[0][3]
                
                if (demoIndex + 1 < len(allEvents)):
                    nextDemo = allEvents[demoIndex + 1][0][3]
                else:
                    nextDemo = 'end'
                
                dprint(ryukbot_settings, f'\nScanning demo: {demoName}', 'green', 2)
                
                # The location of the file we want to make
                backupDemoLocation = Path((str(dir_path) + '\\demos\\' + demoName + '.txt'))
                backupLocation = Path((str(dir_path) + '\\' + (date_time.replace(':', '-')).split('.')[0] + '.txt'))
                
                # Writes the backups to the files
                writeBackup(backupDemoLocation, demoEvents)
                writeBackup(backupLocation, demoEvents)

                i = 0
                clipCount = 0
                bookmark = False
                vdmPath = Path(tf_folder + '\\' + demoName + '.vdm')
                
                demoTicks = []
                
                if not (vdmPath.exists() and (ryukbot_settings["safe_mode"])):
                    with open(vdmPath, 'w+') as VDM:
                        lastTick = ryukbot_settings['start_delay']
                        
                        VDM.write('demoactions\n{\n')
                        
                        while i < len(demoEvents):
                            mod_effects = {}
                            
                            event = demoEvents[i]
                            killstreakCount = killstreakCounter(event, 0)

                            mod_effects = checkMods(ryukbot_settings, event, mod_effects)
                            
                            if event[1].lower() == 'bookmark':
                                bookmark = True
                            
                            startTick = int(event[4]) - ticksPrior(event)
                            endTick = int(event[4]) + ticksAfter(event)
                            
                            checkNext = True
                            tapCount = 0
                            while checkNext:
                                
                                # Checks that its less than the length of the list
                                if i+1 < len(demoEvents):
                                    # Confirms rewind double taps
                                    tapCount = tapCounter(event, demoEvents[i+1], tapCount)
                                    
                                    # Checks if endTick is before the start of the next clip
                                    if endTick >= ((int(demoEvents[i+1][4]) - ticksPrior(demoEvents[i+1])) - ryukbot_settings['minimum_ticks_between_clips']):
                                        killstreakCount =  killstreakCounter(demoEvents[i+1], killstreakCount)
                                        # Sets a new end tick
                                        endTick = int(demoEvents[i+1][4]) + ticksAfter(demoEvents[i+1])
                                        mod_effects = checkMods(ryukbot_settings, demoEvents[i+1], mod_effects)
                                        # Incriments i to show that line has been parsed already
                                        i += 1
                                    else:
                                        checkNext = False
                                else:
                                    checkNext = False
                            
                            clipCount += 1
                            suffix = ''
                            if killstreakCount == 0:
                                suffix = 'BM'
                            else: 
                                if bookmark:
                                    suffix = ('BM%s+' % (killstreakCount))
                                else:
                                    suffix = ('KS%s' % (killstreakCount))
                                    
                            startTick -= tapCount * ryukbot_settings['rewind_amount']
                            
                            if startTick < ryukbot_settings["start_delay"]:
                                startTick = ryukbot_settings["start_delay"]
                                
                            if endTick < ryukbot_settings["start_delay"]:
                                endTick = ryukbot_settings["start_delay"] + 500
                            
                            demoTicks.append({
                                "startTick": startTick,
                                "endTick": endTick,
                                "suffix": suffix,
                                "mod_effects": mod_effects
                            })
                            
                            displayDemoName = f'{mod_effects["modPrefix"]}_{demoName}' if 'modPrefix' in mod_effects else demoName
                            
                            displaySuffix = f'{suffix}_{mod_effects["modSuffix"]}' if 'modSuffix' in mod_effects else suffix
                                
                            dprint(ryukbot_settings, f'Clip {clipCount}: {displayDemoName}_{startTick}-{endTick}_{displaySuffix}', 'cyan', 2)
                            
                            # IGNORE THIS
                            if ((rand := randint(1, 100)) <= 5):
                                dprint(ryukbot_settings, f'Oh god this one is BAD', 'magenta', 68)
                            elif (5 < rand <= 10):
                                dprint(ryukbot_settings, f'Don\'t even record this one', 'magenta', 68)
                            elif (10 < rand <= 15):
                                dprint(ryukbot_settings, f'I don\'t know why this was even marked', 'magenta', 68)
                            elif (15 < rand <= 20):
                                dprint(ryukbot_settings, f'I have learned what pain feels like from that clip', 'magenta', 68)
                            elif (20 < rand <= 25):
                                dprint(ryukbot_settings, f'This is why robots will eventually take over', 'magenta', 68)
                            elif (25 < rand <= 30):
                                dprint(ryukbot_settings, f'Imagine spending all this time playing to only get a clip like that', 'magenta', 68)
                                
                                
                            # Increment i
                            i += 1
                        
                        vdmCount = 1
                        clip = 0
                        
                        dprint(ryukbot_settings, f'Writing file: {demoName}.vdm', 'green', 3)
                        
                        while clip < len(demoTicks):
                            
                            # Sets original tick counts 
                            clipStart = demoTicks[clip]["startTick"]
                            clipEnd = demoTicks[clip]["endTick"]
                            suffix = demoTicks[clip]["suffix"]
                            demo_mods = demoTicks[clip]["mod_effects"]
                            
                            doubleCheck = True
                            while doubleCheck:
                                
                                # Checks that its less than the length of the list
                                if i+1 < len(demoTicks):
                                    # Checks if endTick is before the start of the next clip
                                    if clipEnd >= ((demoTicks[clip+1]["startTick"]) - ryukbot_settings['minimum_ticks_between_clips']):
                                        # Sets a new end tick
                                        clipEnd = int(demoTicks[clip+1]["endTick"])
                                        
                                        # Combines the suffixes to show it was multiple seperated clips combined
                                        suffix = suffix + '_' + demoTicks[clip+1]["suffix"]
                                        # Incriments i to show that line has been parsed already
                                        clip += 1
                                    else:
                                        doubleCheck = False
                                else:
                                    doubleCheck = False
                                    
                            vdmCount = printVDM(VDM, demoName, clipStart, clipEnd, suffix, lastTick, vdmCount, demo_mods)
                            lastTick = clipEnd + 100
                            clip += 1
                            
                        completeVDM(VDM, nextDemo, lastTick, vdmCount, demoName)
                        
                        dprint(ryukbot_settings, f'Done writing file: {demoName}.vdm', 'green', 0)
                        dprint(ryukbot_settings, f'Found {clipCount} clip(s)', 'green', 1)
                                
                        demoIndex += 1
                else: 
                    demoIndex += 1
                    dprint(ryukbot_settings, f'{demoName}.vdm already exists', 'yellow', 0)  
                    dprint(ryukbot_settings, f'Disable "safe_mode" in the settings to overwrite anyway', 'yellow', 0)  
                    dprint(ryukbot_settings, f'I didn\'t think anyone would ever actually use that awful setting', 'magenta', 68)
                

        cprint(f'\nScanning {eventFileName} is complete', 'green')
        if ryukbot_settings["clear_events"]:
            cprint(f'Clearing {eventFileName}', 'yellow')
            try:
                open(eventFile, 'w+').close()
                cprint(f'{eventFileName} cleared')
            except:
                eprint(ryukbot_settings, f'Error while clearing {eventFileName}', 398)
        input("Press enter to close...")
        os._exit(0)
    except IndexError:
        eprint(ryukbot_settings, 'An Unexpected error occurred while running Ryukbot', 101)
                
if Path('ryukbot_settings.json').is_file():
    # Ensure that ryukbot_settings.json is set correctly
    try:
        ryukbot_settings = json.load(open('ryukbot_settings.json'))
    except:
        eprint(ryukbot_settings, 'Error loading ryukbot_settings.json\nYou might\'ve failed the install process.\nPlease delete ryukbot_settings.json and restart it', 195)

    ## Ignore this
    dprint(ryukbot_settings, f'FUNNY HAHA ENABLED', 'magenta', 68)
    
    ## and all of this
    if (today := dt.today().strftime("%m/%d")) == '12/25':
        cprint(""".      *    *           *.       *   .                      *     .
               .   .                   __   *    .     * .     *
    *       *         *   .     .    _|__|_        *    __   .       *
  .  *  /\       /\          *        ('')    *       _|__|_     .
       /  \   * /  \  *          .  <( . )> *  .       ('')   *   *
  *    /  \     /  \   .   *       _(__.__)_  _   ,--<(  . )>  .    .
      /    \   /    \          *   |       |  )),`   (   .  )     *
   *   `||` ..  `||`   . *.   ... ==========='`   ... '--`-` ... * """, 'cyan')
    elif today == '10/31':
        cprint(""".___,_______,_____Happy_Halloween____.
| ./(       )\.        |             |
| )  \/\_/\/  (        |             |
| `)  (^Y^)  (`      \(|)/           |
|  `),-(~)-,(`      --(")--          |
|      '"'      \\\\    /`\            |
|          .-'```^```'-.    ,     ,  |
|         /   (\ __ /)  \   )\___/(  |
|         |    ` \/ `   |  {(@)v(@)} |
|         \    \____/   /   {|~~~|}  |
|          `'-.......-'`    {/^^^\}  |
.____________________________`m-m`___.""", 'cyan')
    elif today == '06/20':
        cprint("""   __       _   _                         _             
  / _| __ _| |_| |__   ___ _ __ ___    __| | __ _ _   _ 
 | |_ / _` | __| '_ \ / _ \ '__/ __|  / _` |/ _` | | | |
 |  _| (_| | |_| | | |  __/ |  \__ \ | (_| | (_| | |_| |
 |_|  \__,_|\__|_| |_|\___|_|  |___/  \__,_|\__,_|\__, |
                                                  |___/ """, 'cyan') 
        
    elif today == '12/10':
        cprint("""ooooooooooooooooooooooooo
o    Happy Hanukkah     o
o          ! !          o
o        ! | | !        o
o      ! | H H | !      o
o    ! | H H!H H | !    o
o    | H H H|H H H |    o
o    (_H_H_H|H_H_H_)    o
o     (___________)     o
o           H           o
o           H           o
o           H           o
o        ___H___        o
ooooooooooooooooooooooooo""", 'cyan')
    elif today == '05/09':
        cprint("""    __     Happy Mother's Day     \_/
   ((6}     Relax and smell     --(_)--
    )(        some roses.         / \\
   \(\)
    \.'-b____q            <@l> <@l><@l>
    ;;---------;;          \)/ \(/ \(/""", 'cyan')
    elif today == '01/01':
        cprint("""  _ __   _____      __  _   _  ___  __ _ _ __ 
 | '_ \ / _ \ \ /\ / / | | | |/ _ \/ _` | '__|
 | | | |  __/\ V  V /  | |_| |  __/ (_| | |   
 |_| |_|\___| \_/\_/    \__, |\___|\__,_|_|   
                        |___/                 """, 'cyan')
    elif (today == '07/01') or (today == '07/04'):
        cprint("""                                   .''.
       .''.      .        *''*    :_\/_:     .
      :_\/_:   _\(/_  .:.*_\/_*   : /\ :  .'.:.'.
  .''.: /\ :    /)\   ':'* /\ *  : '..'.  -=:o:=-
 :_\/_:'.:::.  | ' *''*    * '.\\'/.'_\(/_ '.':'.'
 : /\ : :::::  =  *_\/_*     -= o =- /)\     '  *
  '..'  ':::' === * /\ *     .'/.\\'.  ' ._____
      *        |   *..*         :       |.   |' .---"|
        *      |     _           .--'|  ||   | _|    |
        *      |  .-'|       __  |   |  |    ||      |
     .-----.   |  |' |  ||  |  | |   |  |    ||      |
 ___'       ' /"\ |  '-."".    '-'   '-.'    '`      |____
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                       ~-~-~-~-~-~-~-~-~-~   /|
          )      ~-~-~-~-~-~-~-~  /|~       /_|\\
        _-H-__  -~-~-~-~-~-~     /_|\    -~======-~
~-\XXXXXXXXXX/~     ~-~-~-~     /__|_\ ~-~-~-~
~-~-~-~-~-~    ~-~~-~-~-~-~    ========  ~-~-~-~
      ~-~~-~-~-~-~-~-~-~-~-~-~-~ ~-~~-~-~-~-~
                        ~-~~-~-~-~-~""", 'cyan')
    elif today == '05/17':
        cprint("""                 .##@@&&&@@##.
              ,##@&::%&&%%::&@##.
             #@&:%%000000000%\%:&@#
           #@&:%00'         '00%:&@#
          #@&:%0'             '0%:&@#
         #@&:%0                 0%:&@#
        #@&:%0                   0%:&@#
        #@&:%0                   0%:&@#
        "" ' "                   " ' ""
      _oOoOoOo_                   .-.-.
     (oOoOoOoOo)                 (  :  )
      )`*****`(                .-.`. .'.-.
     /         \              (_  '.Y.'  _)
    | #         |             (   .'|'.   )
    \           /              '-'  |  '-'
     `=========`""", 'cyan')
    elif today == '02/14':
        cprint("""         (\/)
          \/
  (\/)   .-.  .-.
   \/   ((`-)(-`))
         \\\\    //   (\/)
          \\\\  //     \/
   .=***=._))((_.=***=.
  /  .,   .'  '.   ,.  \\
 /__(,_.-'      '-._,)__\\
`    /|             |\   `
    /_|__         __|_\\
      | `))     ((` |
      |             |
     -"==         =="-""", 'cyan')
        
    if ryukbot_settings['welcome_message']:
        cprint("ATTENTION LEGITIMATE GAMERS", attrs=["bold", "underline"])
        cprint(f"""RYUKBOT {ryukbot_version} HAS BEEN LOADED\n
Developed by Ryuk
Steam: https://steamcommunity.com/id/Ryuktf2/
Patreon: https://www.patreon.com/ryuktf2
Discord: Ryuk#1825\n\n""", attrs=["bold"])
else: 
    with open(Path('ryukbot_settings.json'), 'w') as ryukbot_settings:
        json.dump(ryukbotInstaller(setting_descriptions), ryukbot_settings, indent=4)
    ryukbot_settings = json.load(open('ryukbot_settings.json'))
    cprint("ATTENTION LEGITIMATE GAMERS", attrs=["bold", "underline"])
    cprint(f"""RYUKBOT {ryukbot_version} HAS BEEN LOADED\n
Developed by Ryuk
Steam: https://steamcommunity.com/id/Ryuktf2/
Patreon: https://www.patreon.com/ryuktf2
Discord: Ryuk#1825\n\n""", attrs=["bold"])
    

settingRundown()
        
ryukbot()