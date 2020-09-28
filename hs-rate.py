import PySimpleGUI as sg
#import os.path
import json
import os
import random
import tkinter as tk

filename='./to-grade/hs.json'
try:
    with open(filename[:-5]+'.tmp.json') as f:
        dat = json.load(f)
except:
    with open(filename) as f:
        dat = json.load(f)
mylist = [(x, y) for x in range(len(dat)) for y in range(3)]
random.shuffle(mylist)
names = ('gcnn', 'nl2code', 'snippet')


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

    [sg.Radio('4', "RADIO1", enable_events=True, font=("Helvetica", 12), key='4', size=(10,10)),
    sg.Radio('3', "RADIO1", enable_events=True, font=("Helvetica", 12), key='3', size=(10,10)),
    sg.Radio('2', "RADIO1", enable_events=True, font=("Helvetica", 12), key='2', size=(10,10)),
    sg.Radio('1', "RADIO1", enable_events=True, font=("Helvetica", 12), key='1', size=(10,10)),
    sg.Radio('0', "RADIO1", enable_events=True, font=("Helvetica", 12), key='0', size=(10,10))],

    [sg.Cancel(button_text="Skip"), sg.Exit()],
    [sg.Text(''), sg.Text(size=(150, 40), key='-OUTPUT-', font=("Helvetica", 12))]
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
layout1 = [[sg.Text('')]]
root = tk.Tk()
screen_width = root.winfo_screenwidth()
scaling_window = sg.Window('Window Title', layout1, no_titlebar=True, auto_close=False, alpha_channel=0).Finalize()
scaling_window.TKroot.tk.call('tk', 'scaling', max(screen_width/1920,1))
scaling_window.close()
window = sg.Window("Hearthstone dataset grader", layout, finalize=True, location=(0,0), return_keyboard_events=True)


# Run the Event Loop
for (i, j) in mylist:
    sname = 'grade-' + names[j]
    if sname not in dat[i]:
        window['-OUTPUT-'].update(dat[i][names[j]])
        window["-IMAGE-"].update(filename='./hs_cards/'+str(i)+'.png')
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            with open(filename, 'w') as o:
                json.dump(dat, o)   
            try:
                os.remove(filename[:-5]+'.tmp.json')
            except:
                pass
            break

        if event in ['0', '1', '2', '3', '4']:
            dat[i][sname] = int(event)
            with open(filename[:-5]+'.tmp.json', 'w') as o:
                json.dump(dat, o)


        elif event == "Cancel":  
            pass

with open(filename, 'w') as o:
    json.dump(dat, o)   
    try:
        os.remove(filename[:-5]+'.tmp.json')
    except:
        pass

window.close()