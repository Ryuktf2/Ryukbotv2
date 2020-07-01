import colorama
from termcolor import cprint

# Activates the color in the console without this there would be no colors
colorama.init()

def yesNo():
    """A simple prompt for a yes or no question that returns true or false

    Returns:
        boolean: Yes is True, No is False
    """
    print('y for Yes')
    print('n for No')
    answer = input('Answer: ')
    if answer.lower() == 'y' or answer.lower() == 'yes':
        return True
    elif answer.lower() == 'n' or answer.lower() == 'no':
        return False
    else:
        cprint('Please only use y or n', 'red')
        return yesNo()