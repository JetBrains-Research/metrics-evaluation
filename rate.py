import click
import json
import os
import random

@click.command()
@click.option('--filename', default='./to-grade/baseline.json', help='JSON dataset to be rated')
def loadprint(filename):
	with open(filename) as f:
		dat = json.load(f)
	mylist = list(range(len(dat)))
	random.shuffle(mylist)
	print(mylist)
	for i in mylist:
		if 'grade' not in dat[i]:
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
			click.echo(dat[i]['snippet'])
			click.echo(' ')
			while True:
				c = click.getchar()
				click.echo(c)
				if c == 'f':
					break
				elif c == 's':
					break
				elif c in ['0', '1', '2', '3', '4']:
					#datout[i]['grade'] = c
					dat[i]['grade'] = int(c)
					with open(filename[:-5]+'.tmp.json', 'w') as o:
						json.dump(dat, o)
					break					
				else:
					print("Sorry, the input was invalid")
					continue
			if c == 'f':
				break
	click.echo('Thank you for grading!')
	try:
		os.remove(filename[:-5]+'.tmp.json')
	except:
		pass
	with open(filename, 'w') as o:
		json.dump(dat, o)	

if __name__ == '__main__':
	loadprint()
