import click
import json
import os
import random
import sys
from pygments import highlight
from pygments.lexers.python import PythonLexer
from pygments.formatters.terminal import TerminalFormatter


def hl(snippet):
    return highlight(snippet, PythonLexer(), TerminalFormatter())

gauge = (1, 5, 49, 70, 91, 93, 97, 110, 114, 127, 136, 151, 171, 194, 202, 213, 219, 226, 227, 236, 241, 255, 257, 294, 295, 317, 356, 365, 374, 395, 405, 411, 416, 426, 434, 445, 457, 459, 464, 466)
# gauge is the list of 40 intents with 40*5 = 200 snippets to be graded by all our graders. These will allow to compare the graders and yield better estimate for the other grades
names = ('baseline', 'tranx-annot', 'best-tranx', 'best-tranx-rerank', 'snippet', 'codex')

def get_exp():
	while True:
		exp_str = input()
		try:
			experience = int(exp_str)
			if (0 > experience) or (experience > 30): 
				raise ValueError
			else:
				return experience
		except ValueError:
			print('Incorrect input. Please enter, for how long have you been programming in Python (in years, rounded to a nearest integer)')

def get_name():
	while True:
		name = input()
		if (len(name) < 1): 
			print('Incorrect input. Please enter your Slack handle or e-mail address.')
		else:
			return name

def get_consent():
	while (True):
		consent = input().lower()
		if (consent == 'yes'):
			return
		elif (consent == 'no'):
			sys.exit()
		else:
			print('Incorrect input. Please enter "yes", if you wish to participate in the study, and "no", if you want to decline participation')		


def consent():
	print('''Dear participant,\n
this program is a survey on quality of the code snippets conducted by Independent non-profit organization of additional professional education 
“Research and Education Center “JetBrains”, OGRN 1187800000134, located at St. Petersburg, Kantemirovskaya street 2, liter A, office 201. 
You will be presented with code snippets (one at a time) and a problem they are supposed to solve. You are asked to evaluate 
whether the suggested snippet is helpful or not helpful in solving the problem on a scale from 0 to 4, 
where 0 corresponds to a totally irrelevant snippet and 4 corresponds to a snippet which solves the problem 
(more detailed instruction will be present at the snippet grading screen).
In the event of any publication or presentation resulting from the research, no personally identifiable information will be shared.
We plan to include the results of this survey in a scientific publication. If you have any concerns or questions about your rights
as a participant or about the way the study is being conducted, please contact Mikhail Evtikhiev (mikhail.evtikhiev@jetbrains.com).''')
	print(' ')
	print('''Please write, for how long have you been programming in Python (in years), 
rounded to the nearest integer number. This information will be reported in the publication in an aggregated form.''')
	pers_data = dict()
	pers_data["experience"] = get_exp()
	print('''Please write your Slack handle or e-mail address. This information will be kept private and we only ask for it to be able to reach back to you 
to clarify any technical uncertainties with the graded snippets, if such uncertainties shall arise.''')
	pers_data["contact"] = input()
	print('ELECTRONIC CONSENT\n')
	print('''Please enter your choice below. Entering the “yes” option below indicates that:\n
i) you have read and understood the above information,\n
ii) you voluntarily agree to participate, and \n
iii) you are at least 18 years old.\n
If you do not wish to participate in the research study, please decline participation by entering "no"''')
	get_consent()
	pers_data["consent"] = 'yes'
	return pers_data

@click.command()
@click.option('--filename', default='./to-grade/all-singles.json', help='JSON dataset of code snippets to be rated')

def loadprint(filename):
	try:
		with open(filename[:-5]+'.tmp.json') as f:
			dat = json.load(f)
	except:
		with open(filename) as f:
			dat = json.load(f)
	mylist = [(x, y) for x in gauge for y in range(6)]
	testlist = [(x, y) for x in range(len(dat)-1) if x not in gauge for y in range(5)]
	random.shuffle(testlist)
	random.shuffle(mylist)
	mylist.extend(testlist)
	cnt = 0
	pers_data = dat[-1]
	if ((pers_data["contact"] == "") or (pers_data["experience"] == "") or (pers_data["consent"] == "")):
		pers_data = consent()
		for key in dat[-1]:
			dat[-1][key] = pers_data[key]
	for (i, j) in mylist:
		sname = 'grade-' + names[j]
		if sname in dat[i]:
			cnt += 1
	for (i, j) in mylist:
		sname = 'grade-' + names[j]
		if sname not in dat[i]:
			click.clear()
			click.echo('''Is the suggested code snippet helpful or not helpful in solving the problem? 
				Please rate it on a scale from 0 to 4. You can also enter \'f\' to finish rating or \'s\' to skip the snippet 
				4: Snippet is very helpful, it solves the problem
				3: Snippet is helpful, but needs to be slightly changed to solve the problem
				2: Snippet is somewhat helpful, it requires significant changes (compared to the size of the snippet), but is still useful
				1: Snippet is slightly helpful, it contains information relevant to the problem, but it is easier to write the solution from scratch
				0: Snippet is not at all helpful, it is irrelevant to the problem''')
			click.echo(' ')
			click.echo('The problem is:')
			click.echo(dat[i]['intent'])
			click.echo(' ')
			click.echo('The snippet is:')
			click.echo(hl(dat[i][names[j]].replace("`", "'")))
			click.echo(' ')
			click.echo(' ')
			click.echo(' ')
			click.echo('You have graded ' + str(cnt) + ' snippets so far')
			while True:
				c = click.getchar()
				click.echo(c)
				if c == 'f':
					break
				elif c == 's':
					break
				elif c in ['0', '1', '2', '3', '4']:
					dat[i][sname] = int(c)
					cnt += 1
					with open(filename[:-5]+'.tmp.json', 'w') as o:
						json.dump(dat, o)
					break					
				else:
					print("Sorry, the input was invalid")
					continue
			if c == 'f':
				break
	click.echo('Thank you for grading!')
	with open(filename, 'w') as o:
		json.dump(dat, o)	
	try:
		os.remove(filename[:-5]+'.tmp.json')
	except:
		pass

if __name__ == '__main__':
	loadprint()
