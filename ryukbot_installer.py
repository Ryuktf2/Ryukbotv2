#python3
import colorama
from termcolor import cprint
import sys
import os

# Activates the color in the console without this there would be no colors
colorama.init()

def installerText(currentSetting, key):
    """The user experience side of the installer

    Args:
        currentSetting (dictionary): The value of the current setting being editted/created
        key (string): The name of the dictionary/the settings name in the json file

    Returns:
        string/int: returns the value input into the installer. Can be string or int based on the actual setting itself
    """
    cprint('Ryukbot Installer\n', 'cyan')
    print(currentSetting["description"])
    print(f'\nDefault: {currentSetting["default"]}\n')
    if (answer := input(f'{key}: ')) == '':
        return currentSetting["default"]
    elif currentSetting["type"] == 'integer' :
        try:
            return int(answer)
        except:
            os.system('cls')
            cprint('Should be a number with no letters', 'red')
            return installerText(currentSetting, key)
    elif currentSetting["type"] == 'boolean' :
        try:
            if int(answer) == 1 or int(answer) == 0:
                return int(answer)
            else: 
                os.system('cls')
                cprint('Should be a 1 for yes or a 0 for no', 'red')
                return installerText(currentSetting, key)
        except:
            os.system('cls')
            cprint('Should be a number with no letters', 'red')
            return installerText(currentSetting, key)
    else:
        return answer

def ryukbotInstaller(setting_descriptions):
    """This runs through the settings and lets the user input what they want for it in a user friendly way

    Returns:
        Object: The settings they input to it
    """
    os.system('cls')
    cprint('Looks like this is your first time using ryukbot!', 'green')
    print('Please take some time to follow this installers instructions\nBy the end of this it\'ll be ready to run right away')
    print('At any point hit enter to pick the default example shown')
    input('\nPress Enter to start the installer...')
    os.system('cls')
    newSettings = {}
    for key in setting_descriptions:
        newSettings[key] = installerText(setting_descriptions[key], key)
        os.system('cls')
    return newSettings