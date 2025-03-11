# This script download installation packages according to user systems.

import curses
import platform

from PIserver.constants import ENGINE_CHOICES

def display(stdscr, choices, selected, current_row):
    stdscr.clear()
    stdscr.addstr(0, 0, "Choose the installation packages (You can do it later using `powerinfer install` command):")
    stdscr.addstr(2, 0, "Press SPACE to select and ENTER to submit.")
    begin = 4
    for i, choice in enumerate(choices):
        prefix = "* " if i in selected else "  "
        if i == current_row:
            stdscr.addstr(i + begin, 0, prefix + choice, curses.A_REVERSE)
        else:
            stdscr.addstr(i + begin, 0, prefix + choice)
    stdscr.refresh()
    
def choosing(stdscr):
    choices = ENGINE_CHOICES[platform.system()]
    choice_names = list(choices.keys())
    
    curses.curs_set(0)
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    
    selected = set()
    current_row = 0
    while True:
        display(stdscr, choice_names, selected, current_row)
        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(choices) - 1:
            current_row += 1
        elif key == ord(' '):
            if current_row in selected:
                selected.remove(current_row)
            else:
                selected.add(current_row)
        elif key == 10:
            for pkg in selected:
                single_install(choices[choice_names[pkg]])
            break
    return selected

def single_install(pkg_path):
    print(pkg_path)

def interactive_install():
    print("Installing the backend engine...")
    curses.wrapper(choosing)