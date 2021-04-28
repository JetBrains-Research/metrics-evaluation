import click
import json
import os
import random
from pygments import highlight
from pygments.lexers.python import PythonLexer
from pygments.formatters.terminal import TerminalFormatter


def hl(snippet):
    return highlight(snippet, PythonLexer(), TerminalFormatter())

gauge = (1, 5, 49, 70, 91, 93, 97, 110, 114, 127, 136, 151, 171, 194, 202, 213, 219, 226, 227, 236, 241, 255, 257, 294, 295, 317, 356, 365, 374, 395, 405, 411, 416, 426, 434, 445, 457, 459, 464, 466)
# gauge is the list of 40 intents with 40*5 = 200 snippets to be graded by all our graders. These will allow to compare the graders and yield better estimate for the other grades
names = ('baseline', 'tranx-annot', 'best-tranx', 'best-tranx-rerank', 'snippet')

@click.command()
@click.option('--filename', default='./to-grade/all-singles.json', help='JSON dataset of code snippets to be rated')
def loadprint(filename):
	try:
		with open(filename[:-5]+'.tmp.json') as f:
			dat = json.load(f)
	except:
		with open(filename) as f:
			dat = json.load(f)
	mylist = [(x, y) for x in gauge for y in range(5)]
	testlist = [(x, y) for x in range(len(dat)) if x not in gauge for y in range(5)]
	random.shuffle(testlist)
	random.shuffle(mylist)
	mylist.extend(testlist)
	cnt = 0
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
