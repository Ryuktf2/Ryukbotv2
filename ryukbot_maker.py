from datetime import datetime as dt
from pathlib import Path
import colorama
import os
from termcolor import cprint

# Activates the color in the console without this there would be no colors
colorama.init()


def printEvents(eventFile, demo):
    """Prints the events to the _events.txt file

    Args:
        eventFile (Path): The path to the file itself that will be added too
        demo (List): The list of ticks in the demo
    """
    _event = open(eventFile, 'a')
    
    # Seperates the demos in the file
    _event.write('>\n')
    
    # Loops through and prints each one individually
    for event in demo:
        _event.write(f'[{event["Date"]}] Bookmark {event["Type"]} ("{event["Name"]}" at {event["Number"]})\n')
    
    # Closes to finish the printing
    _event.close()
    

def tickInput(eventFileName, demoName, ticks, advancedOptions):
    """Gets the inputs for the specific ticks in each demo with possible advanced options

    Args:
        eventFileName (String): The name of the file for the header
        demoName (String): The name of the demo
        ticks (List): List of ticks already made
        advancedOptions (Int): If the advanced options setting is enabled

    Returns:
        List: The list of ticks listed for recording
    """
    ##TODO: improve user interface
    cprint(f'{eventFileName} Maker\n', 'cyan')
    tick = {
        "Name": demoName,
        "Date": (f'{str(dt.now().date()).replace("-", "/")} {str(dt.now().time()).split(".")[0]}')
    }
    try:
        print('The tick of the event you want recorded')
        print('1000 ticks is about 15 seconds\n')
        tickNum = input(f'tick #{len(ticks) + 1}: ')
        if tickNum == '':
            return ticks
        else:
            tick['Number'] = int(tickNum)
            if advancedOptions == 1:
                os.system('cls')
                cprint(f'{eventFileName} Maker\n', 'cyan')
                print('The name you want to give the clip')
                print('Default: General\n')
                tick['Type'] = input(f'Type: ').replace(" ", "_")
                if tick['Type'] == '':
                    tick['Type'] = 'General'
            else:
                tick['Type'] = 'General'
            
            ticks.append(tick)
            os.system('cls')
            return tickInput(eventFileName, demoName, ticks, advancedOptions)
    except:
        os.system('cls')
        cprint('Please only use numbers')
        return tickInput(eventFileName, demoName, ticks, advancedOptions)

def _eventMaker(eventFile, eventFileName, advancedOptions):
    """Gives the user the ability to make thier own events easily

    Args:
        eventFile (Path): The events file itself
        eventFileName (String): The name of the file
        advancedOptions (Int): The option to disable or enable the advanced option

    Returns:
        Boolean: Returns true if printing went through with no issues
    """
    ##TODO: improve user interface
    os.system('cls')
    repeat = True
    demos = []
    while repeat:
        cprint(f'{eventFileName} Maker', 'cyan')
        demoName = input('Demoname: ')
        if demoName == '':
            repeat = False
        else:
            os.system('cls')
            demos.append(tickInput(eventFileName, demoName, [], advancedOptions))
            
    for demo in demos:
        sortedDemo = sorted(demo, key=lambda k: k['Number']) 
        printEvents(eventFile, sortedDemo)
        
        
    return True