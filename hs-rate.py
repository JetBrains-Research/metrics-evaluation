import sys

import PySimpleGUI as sg
# import os.path
import json
import os
import random
import tkinter as tk


def check_experience(s):
    if (s.isdigit() == False):
        return False
    exp = int(s)
    if (exp > 30):
        return False
    return True


filename = './to-grade/hs.json'
try:
    with open(filename[:-5] + '.tmp.json') as f:
        dat = json.load(f)
except:
    with open(filename) as f:
        dat = json.load(f)
mylist = [(x, y) for x in range(len(dat) - 1) for y in range(3)]
random.shuffle(mylist)
names = ('gcnn', 'nl2code', 'snippet')

file_list_column = [

    [

        sg.Text('''Is the code snippet below relevant or not relevant description of the card on the right? 
                Please rate it on a scale from 0 to 4. You can either press on the radio button or press the corresponding key (\'4\' for 4 etc.) 
                You can also press \'Exit\' to finish grading or \'Skip\' to skip the snippet 
                4: Snippet is very relevant, it describes the card exactly
                3: Snippet is relevant, but needs to be slightly changed to describe the card exactly
                2: Snippet is somewhat relevant, it requires significant changes (compared to the size of the snippet), but is still useful to describe the card
                1: Snippet is slightly relevant, it contains information relevant to the card, but it is easier to write the description from scratch
                0: Snippet is not at all relevant to the card''', font=("Helvetica", 12)),

    ],

    [sg.Radio('4', "RADIO1", enable_events=True, font=("Helvetica", 12), key='4', size=(10, 10)),
     sg.Radio('3', "RADIO1", enable_events=True, font=("Helvetica", 12), key='3', size=(10, 10)),
     sg.Radio('2', "RADIO1", enable_events=True, font=("Helvetica", 12), key='2', size=(10, 10)),
     sg.Radio('1', "RADIO1", enable_events=True, font=("Helvetica", 12), key='1', size=(10, 10)),
     sg.Radio('0', "RADIO1", enable_events=True, font=("Helvetica", 12), key='0', size=(10, 10))],

    [sg.Cancel(button_text="Skip"), sg.Exit()],
    [sg.Text(''), sg.Text(size=(150, 40), key='-OUTPUT-', font=("Helvetica", 12))]
]

# For now will only show the name of the file that was chosen

image_viewer_column = [

    [sg.Image(key="-IMAGE-")],

]

# ----- Full layout -----

layout_form = [[sg.Text('''Dear participant,\n
this program is a survey on quality of the code snippets conducted by Independent non-profit organization of additional professional education 
“Research and Education Center “JetBrains”, OGRN 1187800000134, located at St. Petersburg, Kantemirovskaya street 2, liter A, office 201. 
You will be presented with code snippets (one at a time) and a problem they are supposed to solve. You are asked to evaluate whether 
the suggested snippet is helpful or not helpful in solving the problem on a scale from 0 to 4, where 0 corresponds to a totally irrelevant snippet 
and 4 corresponds to a snippet which solves the problem (more detailed instruction will be present at the snippet grading screen).\n
In the event of any publication or presentation resulting from the research, no personally identifiable information will be shared.
We plan to include the results of this survey in a scientific publication. If you have any concerns or questions about your rights as a participant 
or about the way the study is being conducted, please contact Mikhail Evtikhiev (mikhail.evtikhiev@jetbrains.com).''',
                        font=("Helvetica", 12))],

               [sg.Text('''In the text box below please write, for how long have you been programming in Python (in years), 
rounded to the nearest integer number. This information will be reported in the publication in an aggregated form.''',
                        font=("Helvetica", 12))],

               [sg.Text('Python experience: ', key='_text1_',
                        font=("Helvetica", 12)), sg.InputText(key='_python_', size=(10, 1))],

               [sg.Text('''In the text box below please write your Slack handle or e-mail address. This information will be kept private and we only ask for it 
to be able to reach back to you to clarify any technical uncertainties with the graded snippets, if such uncertainties shall arise.''')],

               [sg.Text('Contact information: ', key='_text2_',
                        font=("Helvetica", 12)), sg.InputText(key='_contact_', size=(30, 1))],

               [sg.Text('''ELECTRONIC CONSENT\n
Please select your choice below. Selecting the “yes” option below indicates that: 
i) you have read and understood the above information, 
ii) you voluntarily agree to participate, and 
iii) you are at least 18 years old. 
If you do not wish to participate in the research study, please decline participation by selecting “No”.''',
                        font=("Helvetica", 12))],

               [sg.Ok(button_text="Yes"), sg.Exit(button_text="No")],

               ]

layout_grade = [[

    sg.Column(file_list_column),

    sg.VSeperator(),

    sg.Column(image_viewer_column),

]
]

#layout1 = [[sg.Text('')]]
#root = tk.Tk()
#screen_width = root.winfo_screenwidth()
#scaling_window = sg.Window('Window Title', layout1, no_titlebar=True, auto_close=False, alpha_channel=0).Finalize()
#scaling_window.TKroot.tk.call('tk', 'scaling', max(screen_width / 1920, 1))
#scaling_window.close()

pers_data = dat[-1]
no_consent = False
if ((pers_data["contact"] == "") or (pers_data["experience"] == "") or (pers_data["consent"] == "")):
    window = sg.Window("Hearthstone dataset grader form", layout_form, finalize=True, location=(0, 0),
                       return_keyboard_events=True)
    no_consent = True
    while (no_consent):
        event, values = window.read()
        if event == "No" or event == sg.WIN_CLOSED:
            window.close()
            sys.exit()
        elif event == "Yes":
            error_text = ""
            if (check_experience(values['_python_']) == False):
                error_text += "Incorrect input. Please enter, for how long have you been programming in Python (in " \
                              "years, rounded to a nearest integer)\n"
            if (len(values['_contact_']) < 1):
                error_text += 'Incorrect input. Please enter your Slack handle or e-mail address.\n'
            if len(error_text) > 0:
                sg.popup(error_text)
            else:
                pers_data["contact"] = values['_contact_']
                pers_data["experience"] = int(values['_python_'])
                pers_data["consent"] = 'yes'
                no_consent = False
                for key in dat[-1]:
                    dat[-1][key] = pers_data[key]
                window.close()
        else:
            pass

window = sg.Window("Hearthstone dataset grader", layout_grade, finalize=True, location=(0, 0),
                   return_keyboard_events=True)
if no_consent: window.close()
# Run the Event Loop
for (i, j) in mylist:
    successful = False
    finished = False
    sname = 'grade-' + names[j]
    if sname not in dat[i]:
        window['-OUTPUT-'].update(dat[i][names[j]])
        window["-IMAGE-"].update(filename='./hs_cards/' + str(i) + '.png')
        while not successful:
            event, values = window.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                with open(filename, 'w') as o:
                    json.dump(dat, o)
                try:
                    os.remove(filename[:-5] + '.tmp.json')
                except:
                    pass
                finished = True
                successful = True

            elif event[0] in ['0', '1', '2', '3', '4']:
                successful = True
                dat[i][sname] = int(event)
                with open(filename[:-5] + '.tmp.json', 'w') as o:
                    json.dump(dat, o)


            elif event == "Skip":
                successful = True
                pass
            else:
                sg.popup(event)
    if finished:
        break

with open(filename, 'w') as o:
    json.dump(dat, o)
    try:
        os.remove(filename[:-5] + '.tmp.json')
    except:
        pass

window.close()
