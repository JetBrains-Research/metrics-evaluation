import click
import json
import os.path
import random

@click.command()
@click.option('--filename', default='./to-grade/all-pairs.json', help='JSON dataset of code snippet pairs to be rated')
def loadprint(filename):
	with open(filename) as f:
		dat = json.load(f)
	mylist = [(x, y, z) for x in range(len(dat)) for y in range(5) for z in range(y+1,5)]
	names = ('baseline', 'tranx-annot', 'best-tranx', 'best-tranx-rerank', 'snippet')
	random.shuffle(mylist)
	for (i, j, k) in mylist:
		sname = 'grade-'+names[j]+'-'+names[k]
		if sname not in dat[i]:
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
			if x == 1: click.echo(dat[i][names[j]])
			if x == 2: click.echo(dat[i][names[k]])
			click.echo(' ')
			click.echo('The second snippet is:')
			if x == 1: click.echo(dat[i][names[k]])
			if x == 2: click.echo(dat[i][names[j]])
			click.echo(' ')
			while True:
				c = click.getchar()
				click.echo(c)
				if c == 'f':
					break
				elif c == 's':
					break
				elif c in ['0', '1', '2']:
					if x == 1: dat[i][sname] = int(c)
					if x == 2: dat[i][sname] = (3 - int(c)) % 3
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
