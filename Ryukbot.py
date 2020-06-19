#! python3
##importing things (self explanitory)
from datetime import datetime as dt
from pathlib import Path
import re
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

#TODO: Welcome and thank you message (unimportant)


tickBuffer = 500

# Prints the backups to the folders told to
def writeBackup(backup_location, eventsPerDemo):
    
    if backup_location.is_file():
        openType = 'a'
    else: 
        openType = 'w'
        
    with open(backup_location, openType) as backup_file:
        backup_file.write('>\n')
        for demoEvent in eventsPerDemo:
            backup_file.write('[%s] %s %s ("%s" at %s)\n' % (demoEvent))
            
# Returns the amount of ticks to put before the clip
def ticksPrior(event):
    if event[1].lower() == 'killstreak':
        return 250 * int(event[2])
    else:
        return 1000
      
# Returns the amount of ticks to put after the clip      
def ticksAfter(event):
    if event[1].lower() == 'killstreak':
        return 500
    else:
        return 500
    
def killstreakCounter(event, currentCount):
    if event[1].lower() == 'killstreak':
        if int(event[2]) >= int(currentCount + 1):
            # cprint('%s >= %s' % (event[2], str(currentCount + 1)), 'green')
            return int(event[2])
        else:
            # cprint('%s < %s' % (event[2], str(currentCount + 1)), 'red')
            return currentCount + int(event[2])
    else:
        # cprint('%s != %s' % (event[1].lower(), 'killstreak'), 'red')
        return currentCount
                
# Read _events.txt or killstreaks.txt file 
with open('_events.txt', 'r') as _events:

    # Saving the file as an array/list variable
    eventLines = _events.readlines()
    
    # REGEX for future use
    lineRegex = re.compile('\[(.*)\] (killstreak|bookmark) (.*) \("(.*)" at (\d*)\)', re.IGNORECASE)
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
    
    # Counts the amount of carrots splitting the demos
    carrotCount = len(carrotRegex.findall(''.join(eventLines))) + 1
    
    # Simple message letting the user know the programs progress.
    # More updates to the user are nice but I want to try and limit spam to the user.
    cprint('Scanned ' + str(len(eventLines)) + ' different ticks over the span of ' + str(carrotCount) + ' demos.', 'green')
    
    #TODO: Loop through the eventMarks List and print out the ticks for each demo
    
    # This is used later to check if the demo has changed to the next on the list
    demoName = eventMarks[0][3]
    allEvents = []
    eventsPerDemo = []
    # Loops through the list of events in the eventMarks list
    for event in eventMarks:
        #! This doesnt add the last demo to the list
        
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
    
    # Get current directory path and add the backups folder to the ned
    dir_path = Path(str(os.path.dirname(os.path.realpath(__file__)) + '\\ryukbot_backups\\'))
    
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
        
        # The location of the file we want to make
        backupDemoLocation = Path((str(dir_path) + '\\demos\\' + demoName + '.txt'))
        backupLocation = Path((str(dir_path) + '\\' + (date_time.replace(':', '-')).split('.')[0] + '.txt'))
        
        # Writes the backups to the files
        writeBackup(backupDemoLocation, demoEvents)
        writeBackup(backupLocation, demoEvents)

        i = 0
        clipCount = 0
        bookmark = False
        while i < len(demoEvents):
            
            event = demoEvents[i]
            killstreakCount = killstreakCounter(event, 0)
            
            if event[1].lower() == 'bookmark':
                bookmark = True
            
            startTick = int(event[4]) - ticksPrior(event)
            endTick = int(event[4]) + ticksAfter(event)
            
            checkNext = True
            while checkNext:
                
                # Checks that its less than the length of the list
                if i+1 < len(demoEvents):
                    
                    # Checks if endTick is before the start of the next clip
                    if endTick >= ((int(demoEvents[i+1][4]) - ticksPrior(demoEvents[i+1])) - tickBuffer):
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
                    
            cprint('Clip %s: %s_%s-%s_%s' % (clipCount, demoName, startTick, endTick, suffix), 'cyan')
            i += 1
        
        cprint('Done printing demo: %s\nFound %s clip(s)' % (demoName, clipCount), 'green')
        demoIndex += 1