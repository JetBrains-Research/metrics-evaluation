import click
import json
import os.path
import random

@click.command()
@click.option('--filename', default='dataset.json', help='JSON dataset to be rated')
def loadprint(filename):
	with open(filename) as f:
		dat = json.load(f)
	for i in range(len(dat)):
		if 'grade' not in dat[i]:
			click.clear()
			click.echo('''Which of the two following snippets is more relevant to the posed problem? 
				Please enter a number from 0 to 2. You can also enter \'f\' to finish rating or \'s\' to skip the problem 
				1: The first snippet is more relevant
				2: The second snippet is more relevant
				0: I cannot decide, which snippet is more relevant''')
			click.echo(' ')
			click.echo('The problem is:')
			click.echo(dat[i]['intent'])
			click.echo(' ')
			x = random.randint(1,2)
			click.echo('The first snippet is:')
			if x == 1: click.echo(dat[i]['snippet1'])
			if x == 2: click.echo(dat[i]['snippet2'])
			click.echo(' ')
			click.echo('The second snippet is:')
			if x == 1: click.echo(dat[i]['snippet2'])
			if x == 2: click.echo(dat[i]['snippet1'])
			click.echo(' ')
			while True:
				c = click.getchar()
				click.echo(c)
				if c == 'f':
					break
				elif c == 's':
					break
				elif c in ['0', '1', '2']:
					#datout[i]['grade'] = c
					if x == 1: dat[i]['grade'] = int(c)
					if x == 2: dat[i]['grade'] = (3 - int(c)) % 3
					break					
				else:
					print("Sorry, the input was invalid")
					continue
			if c == 'f':
				break

	click.echo('Thank you for grading!')
	with open(filename, 'w') as o:
		json.dump(dat, o)	

if __name__ == '__main__':
	loadprint()
