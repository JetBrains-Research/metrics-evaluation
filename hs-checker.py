import PySimpleGUI as sg
#import os.path
import json
import os
import random
from pygments import highlight
from pygments.lexers.python import PythonLexer
from pygments.formatters.terminal import TerminalFormatter

filename='./to-grade/hs.json'
try:
    with open(filename[:-5]+'.tmp.json') as f:
        dat = json.load(f)
except:
    with open(filename) as f:
        dat = json.load(f)
mylist = [x for x in range(len(dat))]

file_list_column = [

    [

        sg.Text('''Is the code snippet below relevant or not relevant description of the card on the right? 
                Please rate it on a scale from 0 to 4. You can also press \'Exit\' to finish rating or \'Skip\' to skip the snippet 
                4: Snippet is very relevant, it describes the card exactly
                3: Snippet is relevant, but needs to be slightly changed to describe the card exactly
                2: Snippet is somewhat relevant, it requires significant changes (compared to the size of the snippet), but is still useful to describe the card
                1: Snippet is slightly relevant, it contains information relevant to the card, but it is easier to write the description from scratch
                0: Snippet is not at all relevant to the card''', font=("Helvetica", 12)),

    ],

    [sg.Radio('4', "RADIO1", enable_events=True, font=("Helvetica", 12)),
    sg.Radio('3', "RADIO1", enable_events=True, font=("Helvetica", 12)),
    sg.Radio('2', "RADIO1", enable_events=True, font=("Helvetica", 12)),
    sg.Radio('1', "RADIO1", enable_events=True, font=("Helvetica", 12)),
    sg.Radio('0', "RADIO1", enable_events=True, font=("Helvetica", 12))],

    [sg.Cancel(button_text="Skip"), sg.Exit()],
    [sg.Text(''), sg.Text(size=(150, 20), key='-OUTPUT-', font=("Helvetica", 12))],
    [sg.Text(''), sg.Text(size=(3, 1), key='-NUMBER-', font=("Helvetica", 24))],
]


# For now will only show the name of the file that was chosen

image_viewer_column = [

    [sg.Image(key="-IMAGE-")],

]


# ----- Full layout -----

layout = [

    [

        sg.Column(file_list_column),

        sg.VSeperator(),

        sg.Column(image_viewer_column),

    ]

]


window = sg.Window("Hearthstone dataset grader", layout, finalize=True, location=(0,0))

# Run the Event Loop
for i in mylist:
    window['-OUTPUT-'].update(dat[i]['snippet'])
    window['-NUMBER-'].update(str(i))
    window["-IMAGE-"].update(filename='./hs_cards/'+str(i)+'.png')
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    if event in ['0', '1', '2', '3', '4']:
        pass

    elif event == "Cancel":  
        pass

window.close()