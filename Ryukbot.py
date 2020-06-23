#! python3
##importing things (self explanitory)
from datetime import datetime as dt
from pathlib import Path
import re
import json
import sys
import os
import colorama
from termcolor import colored, cprint

# Activates the color in the console without this there would be no colors
colorama.init()

# Color Coding ruleset:
# grey: 
# red: Errors and the messages associated
# green: Ran successfully
# yellow: Warning labels or important notices
# blue: 
# magenta: 
# cyan: Titles/System messages
# white: Normal paragraph messages/descriptions of things

def eprint(message, errorCode):
    cprint(message, 'red')
    cprint('Error Code: %s' % (errorCode))
    input('Press enter to close...')
    os._exit(0)
    
def dprint(message, color, value):
    if ryukbot_settings['console_detail'] > value:
        cprint(message, color)
    
def checkSetting(setting, type, ryukbot_settings):
    if setting in ryukbot_settings:
        if type == 'digit' or type == 'boolean':
            if str(ryukbot_settings[setting]).isdigit():
                if type == 'boolean':
                    if ryukbot_settings[setting] == 1 or ryukbot_settings[setting] == 0:
                        return True
                    else:
                        eprint(setting + ' is incorrectly set up (should be a 1 or 0)', 204)
                else: 
                    return True
                    
            else:
                eprint(setting + ' is incorrectly set up (should be a number)', 205)
        else: 
            if isinstance(ryukbot_settings[setting], str):
                return True
            else:
                eprint(setting + ' is incorrectly set up (should be wrapped in quotes)', 203)
    else:
        eprint(setting + ' is missing from ryukbot_settings.json', 201)
        
def settingRundown(ryukbot_settings):
    checkSetting("commands", 'string', ryukbot_settings)
    checkSetting("framerate", 'digit', ryukbot_settings)
    checkSetting("crosshair", 'boolean', ryukbot_settings)
    checkSetting("HUD", 'boolean', ryukbot_settings)
    checkSetting("text_chat", 'boolean', ryukbot_settings)
    checkSetting("voice_chat", 'boolean', ryukbot_settings)
    checkSetting("method", 'string', ryukbot_settings)
    checkSetting("start_delay", 'digit', ryukbot_settings)
    checkSetting("before_bookmark", 'digit', ryukbot_settings)
    checkSetting("after_bookmark", 'digit', ryukbot_settings)
    checkSetting("before_killstreak_per_kill", 'digit', ryukbot_settings)
    checkSetting("after_killstreak", 'digit', ryukbot_settings)
    checkSetting("interval_for_rewind_double_taps", 'digit', ryukbot_settings)
    checkSetting("rewind_amount", 'digit', ryukbot_settings)
    checkSetting("record_continuous", 'boolean', ryukbot_settings)
    checkSetting("welcome_message", 'boolean', ryukbot_settings)
    checkSetting("console_detail", 'digit', ryukbot_settings)
    checkSetting("clear_events", 'boolean', ryukbot_settings)
        
# Writes the start of a new command and adds one to the vdmCount variable
def newCommand(vdmCount, VDM):
    VDM.write('\t"%s"\n\t{\n\t\t' % (vdmCount))
    return vdmCount + 1

# Prints the body of the vdm for each clip to be recorded
def printVDM(VDM, demoName, startTick, endTick, suffix, lastTick, vdmCount):
    # Starts the new command line
    try:
        vdmCount = newCommand(vdmCount, VDM)
        VDM.write('factory "SkipAhead"\n\t\tname "skip"\n\t\tstarttick "%s"\n\t\tskiptotick "%s"\n\t}\n'
                % (lastTick, startTick - 100))
        
        vdmCount = newCommand(vdmCount, VDM)
    except:
        eprint('Error printing to %s.vdm' % demoName, 372)
    
    # sets the chatTime based on the settings
    if ryukbot_settings["text_chat"] == 0:
        chatTime = 0
    else:
        chatTime = 12
        
    # Creates the commands to later be written in the VDM file.
    try:
        commands = ('%s; hud_saytext_time %s; voice_enable %s; crosshair %s; cl_drawhud %s; host_framerate %s;' 
                    % (ryukbot_settings["commands"], chatTime,
                    ryukbot_settings["voice_chat"], ryukbot_settings["crosshair"],
                    ryukbot_settings["HUD"], ryukbot_settings["framerate"]))
        
        # Writes the bulk of the startmovie command
        VDM.write('factory "PlayCommands"\n\t\tname "record_start"\n\t\tstarttick "%s"\n\t\tcommands "%s startmovie %s_%s-%s_%s %s; clear"\n\t}\n'
                % (startTick, commands, demoName, startTick, endTick, suffix, ryukbot_settings["method"]))
    except: 
        eprint('Error printing to %s.vdm' % demoName, 373)
    
    try:
        vdmCount = newCommand(vdmCount, VDM)
        VDM.write('factory "PlayCommands"\n\t\tname "record_stop"\n\t\tstarttick "%s"\n\t\tcommands "endmovie;host_framerate 0"\n\t}\n'
                % (endTick))
    except: 
        eprint('Error printing to %s.vdm' % demoName, 374)
    
    return vdmCount + 1


def completeVDM(VDM, nextDemo, lastTick, vdmCount, demoName):
    try:
        if nextDemo == 'end' or ryukbot_settings["record_continuous"] == 0:
            commands = 'quit'
        else: 
            commands = 'playdemo ' + nextDemo
        vdmCount = newCommand(vdmCount, VDM)
        VDM.write('factory "PlayCommands"\n\t\tname "VDM end"\n\t\tstarttick "%s"\n\t\tcommands "%s"\n\t}\n}'
                % (lastTick, commands))
    except:
        eprint('Error printing to %s.vdm' % demoName, 379)


# Prints the backups to the folders told to
def writeBackup(backup_location, eventsPerDemo):
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
        eprint('Error while writing backup', 343)
            
# Returns the amount of ticks to put before the clip
def ticksPrior(event):
    if event[1].lower() == 'killstreak':
        return ryukbot_settings['before_killstreak_per_kill'] * int(event[2])
    else:
        return ryukbot_settings['before_bookmark']
      
# Returns the amount of ticks to put after the clip      
def ticksAfter(event):
    if event[1].lower() == 'killstreak':
        return ryukbot_settings['after_killstreak']
    else:
        return ryukbot_settings['after_bookmark']
    
def killstreakCounter(event, currentCount):
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
        eprint('Error counting killstreak amount', 405)
    
# Counts the amount of time bookmark is tapped
def tapCounter(event, nextEvent, tapCount):
    if event[1].lower() == 'bookmark':
        if nextEvent[1].lower() == 'bookmark':
            if int(event[4]) + ryukbot_settings['interval_for_rewind_double_taps'] >= int(nextEvent[4]):
                tapCount += 1
    return tapCount
        
# Read _events.txt or killstreaks.txt file 
def ryukbot(ryukbot_settings):
    try:
        tf_folder = ryukbot_settings["tf_folder"]
        if Path(tf_folder + '\\demos\\_events.txt').is_file():
            tf_folder = tf_folder + '\\demos'
            eventFileName = '_events.txt'
            eventFile = Path(tf_folder + '\\_events.txt')
        elif Path(tf_folder + '\\KillStreaks.txt').is_file():
            eventFileName = 'KillStreaks.txt'
            eventFile = Path(tf_folder + '\\KillStreaks.txt')
        else:
            eprint('Can not find KillStreaks.txt or _event.txt', 331)
        with open(eventFile, 'r') as _events:

            # Saving the file as an array/list variable
            eventLines = _events.readlines()
            
            # REGEX for future use
            lineRegex = re.compile('\[(.*)\] (kill|killstreak|bookmark) (.*) \("(.*)" at (\d*)\)', re.IGNORECASE)
            carrotRegex = re.compile('\n(\>)?\n')
            
            # Combines it into one string and searches it
            eventMarks = lineRegex.findall(''.join(eventLines))
            
            #* The syntax for getting the variables and its information
            # LINE: eventMarks[*]           --- EXAMPLE ('2020/04/27 20:23', 'Killstreak', '3', '2020-04-27_20-16-21', '29017')
            # DATE: eventMarks[*][0]        --- EXAMPLE 2020/04/27 20:23
            # TYPE: eventMarks[*][1]        --- EXAMPLE Killstreak 
        # TYPE: eventMarks[*][1]        --- EXAMPLE Killstreak 
            # TYPE: eventMarks[*][1]        --- EXAMPLE Killstreak 
        # TYPE: eventMarks[*][1]        --- EXAMPLE Killstreak 
            # TYPE: eventMarks[*][1]        --- EXAMPLE Killstreak 
            # CRITERIA: eventMarks[*][2]    --- EXAMPLE 3
            # DEMO: eventMarks[*][3]        --- EXAMPLE 2020-04-27_20-16-21
            # TICK: eventMarks[*][4]        --- EXAMPLE 29017
            
            # Counts the amount of carrots splitting the demos
            carrotCount = len(carrotRegex.findall(''.join(eventLines))) + 1
            
                    # This is used later to check if the demo has changed to the next on the list
            try:
                demoName = eventMarks[0][3]
            except IndexError: 
                eprint(eventFileName + ' is empty', 332)
            
            # Simple message letting the user know the programs progress.
            # More updates to the user are nice but I want to try and limit spam to the user.
            cprint('Scanned ' + str(len(eventLines)) + ' different ticks over the span of ' + str(carrotCount) + ' demos.', 'green')
        
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
            
            # Get current directory path and add the backups folder to the end
            dir_path = Path(tf_folder + '\\ryukbot_backups\\')
            
            # Make the folder if it doesnt exist yet
            if not os.path.exists(dir_path):
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
                
                dprint('\nScanning demo: %s' % (demoName), 'green', 2)
                
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
                with open(vdmPath, 'w+') as VDM:
                    lastTick = ryukbot_settings['start_delay']
                    
                    VDM.write('demoactions\n{\n')
                    
                    while i < len(demoEvents):
                        
                        event = demoEvents[i]
                        killstreakCount = killstreakCounter(event, 0)
                        
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
                        
                        demoTicks.append({
                            "startTick": startTick,
                            "endTick": endTick,
                            "suffix": suffix
                        })
                        
                        dprint('Clip %s: %s_%s-%s_%s' % (clipCount, demoName, startTick, endTick, suffix), 'cyan', 2)
                        i += 1
                    
                    vdmCount = 1
                    clip = 0
                    
                    dprint('Writing file: %s.vdm' % (demoName), 'green', 3)
                    
                    while clip < len(demoTicks):
                        
                        # Sets original tick counts 
                        clipStart = demoTicks[clip]["startTick"]
                        clipEnd = demoTicks[clip]["endTick"]
                        suffix = demoTicks[clip]["suffix"]
                        
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
                                
                        vdmCount = printVDM(VDM, demoName, clipStart, clipEnd, suffix, lastTick, vdmCount)
                        lastTick = clipEnd + 100
                        clip += 1
                        
                    completeVDM(VDM, nextDemo, lastTick, vdmCount, demoName)
                    
                    dprint('Done writing file: %s.vdm' % (demoName), 'green', 0)
                    dprint('Found %s clip(s)' % (clipCount), 'green', 1)
                            
                    demoIndex += 1

        cprint('\nScanning ' + eventFileName + ' is complete', 'green')
        cprint('Clearing ' + eventFileName, 'yellow')
        try:
            open(eventFile, 'w+').close()
            cprint(eventFileName + ' cleared')
        except:
            eprint('Error while clearing %s' % eventFileName, 398)
        input("Press enter to close...")
        os._exit(0)
    except:
        eprint('An Unexpected error occurred while running Ryukbot', 101)
                
if Path('ryukbot_settings.json').is_file():
    # Ensure that ryukbot_settings.json is set correctly
    try:
        ryukbot_settings = json.load(open('ryukbot_settings.json'))
    except:
        eprint('Error loading ryukbot_settings.json', 195)
    if ryukbot_settings['welcome_message'] == 1:
        cprint("ATTENTION LEGITIMATE GAMERS", attrs=["bold", "underline"])
        cprint("""RYUKBOT v2.0.0 HAS BEEN LOADED\n
Developed by Ryuk
Steam: https://steamcommunity.com/id/Ryuktf2/
Patreon: https://www.patreon.com/ryuktf2
Discord: Ryuk#1825\n\n""", attrs=["bold"])
else: 
    # If there is no settings file fill it with the default values
    #TODO: Add in the settings maker/ryukbot installer
    with open(Path('ryukbot_settings.json'), 'w') as ryukbot_settings:
        json.dump({
    "tf_folder": "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Team Fortress 2\\tf",
    "commands": "",
    "framerate": 60,
    "crosshair": 0,
    "HUD": 1,
    "text_chat": 0,
    "voice_chat": 0,
    "method": "h264",
    "start_delay": 500,
    "before_bookmark": 1000,
    "after_bookmark": 200,
    "before_killstreak_per_kill": 500,
    "after_killstreak": 300,
    "minimum_ticks_between_clips": 500,
    "interval_for_rewind_double_taps": 200,
    "rewind_amount": 1000,
    "record_continuous": 1,
    "welcome_message": 1,
    "console_detail": 3,
    "clear_events": 1,
    "mods": []
}, ryukbot_settings, indent=4)
    ryukbot_settings = json.load(open('ryukbot_settings.json'))
    cprint("ATTENTION LEGITIMATE GAMERS", attrs=["bold", "underline"])
    cprint("""RYUKBOT v2.0.0 HAS BEEN LOADED\n
Developed by Ryuk
Steam: https://steamcommunity.com/id/Ryuktf2/
Patreon: https://www.patreon.com/ryuktf2
Discord: Ryuk#1825\n\n""", attrs=["bold"])
    

settingRundown(ryukbot_settings)
        
ryukbot(ryukbot_settings)