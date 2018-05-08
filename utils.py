import os
import re
import sys
import cv2
import imageio
import argparse
import numpy as np

import warnings
warnings.filterwarnings('ignore')

parser = argparse.ArgumentParser()
parser.add_argument('--selection', nargs='+')
parser.add_argument('--path', default='.', type=str)
parser.add_argument('--maketx', default='.', type=str)
parser.add_argument('--threshold', default='0.1', type=str)
parser.add_argument('--logname', default='txManLog', type=str)
parser.add_argument('--pattern', default='.*', type=str)
parser.add_argument('--csfrom', default='sRGB', type=str)
parser.add_argument('--csto', default='linear', type=str)
parser.add_argument('--list', action='store_true')
parser.add_argument('--log', action='store_true')
parser.add_argument('--create', action='store_true')
parser.add_argument('--remove', action='store_true')
parser.add_argument('--select', action='store_true')
parser.add_argument('--here', action='store_true')
parser.add_argument('--tree', action='store_true')
parser.add_argument('--all', action='store_true')
parser.add_argument('--grey', action='store_true')
parser.add_argument('--color', action='store_true')
parser.add_argument('--regex', action='store_true')
parser.add_argument('--colorconvert', action='store_true')

args = parser.parse_args()

PATH = args.path
MAKETX = args.maketx

listfile, listdir = [], []
if args.here:
	listfile, listdir = zip(*[[f, PATH] for f in os.listdir(PATH) if os.path.isfile(os.path.join(PATH, f))])
else:
	listfile, listdir = zip(*[[f, r] for r, d, fs in os.walk(PATH) for f in fs])
	if args.select:
		selection = []
		for filename in args.selection:
			if filename[-1] in ['\\', '/']:
				path = '{0}\\{1}'.format(PATH, filename[:-1])
				temp_file, temp_dir = zip(*[[f, r] for r, d, fs in os.walk(path) for f in fs])
				selection += ['{0}\\{1}'.format(i, j) for i, j in zip(temp_dir, temp_file)]
			else:
				*path, fname = filename.split('\\')
				selection.append('\\'.join([PATH] + path + [fname]))
		match = []
		for i, (f, d) in enumerate(zip(listfile, listdir)):
			if '{0}\\{1}'.format(d, f) not in selection:
				match.append(i)
		listfile = [f for i, f in enumerate(listfile) if i not in match]
		listdir = [f for i, f in enumerate(listdir) if i not in match]

listfile = list(listfile)
listdir = list(listdir)

lenfile = len(listfile)

if args.regex:
	match = []
	for i in range(lenfile):
		r = re.compile(args.pattern)
		m = r.match(listdir[i] + '\\' + listfile[i])
		if m is None:
			match.append(i)
	listfile = [f for i, f in enumerate(listfile) if i not in match]
	listdir = [f for i, f in enumerate(listdir) if i not in match]

class verbose(object):
	def __init__(self):
		self.progbar = ''
		self.sel = [0]*lenfile
		self.sel_tx = [0]*lenfile

	def _progbar(self, i):
		self.progbar = '{0:0>6.1%} | '.format(i/lenfile)
		self.progbar += '#'*int(33*i/lenfile)
		print(self.progbar, end='\r', flush=True)

	def _result(self):
		count = 0
		directory = ''
		log = ['txMan Log\n']
		for i in range(lenfile):
			if self.sel[i]:
				if listdir[i] != directory:
					directory = listdir[i]
					dir_out = '\n@ {}'.format(directory.replace(PATH, '.'))
					if not args.log:
						print(dir_out)
					log.append(dir_out + '\n')
				count += 1
				file_out = '* [tx]' if self.sel_tx[i] else '* [  ]'
				file_out += listfile[i]
				if not args.log:
					print(file_out)
				log.append(file_out + '\n')
		selected = 'total selected: {}'.format(count)
		analyzed = 'total analyzed: {}'.format(lenfile)
		if args.log:
			log.append('\n' + selected + '\n' + analyzed)
			f = open('{}.log'.format(args.logname), 'w')
			f.writelines(log)
			f.close()
		else:
			print('\n')
			print(selected)
			print(analyzed)

class iterator(verbose):
	def __init__(self):
		super(iterator, self).__init__()
		self.filename = ''
		self.i = 0

class is_files(iterator):
	def __init__(self):
		super(is_files, self).__init__()
		self.img = 0

	def exist(self):
		*fn, ext = self.filename.split('.')
		return os.path.isfile(self.filename.replace(ext, 'tx'))

	def is_tx(self):
		*fn, ext = self.filename.split('.')
		return ext == 'tx'
	
	def is_image(self):
		try:
			self.img = imageio.imread(self.filename)
			return True
		except:
			return False
	
	def is_grey(self):
		if self.is_image():
			shape = self.img.shape
			if len(shape) < 3:
				return True
			m, n, c = shape
			try:
				r, g, b = cv2.split(self.img)
			except:
				r, g, b, _ = cv2.split(self.img)
			result = abs(r - g) + abs(r - b) + abs(g - b)
			result = result.sum()/(m*n*c)
			try:
				threshold = float(args.threshold)
			except ValueError:
				print('\ninvalid threshold value..\n')
				exit()
			return result < threshold
		return False

	def is_color(self):
		if self.is_image():
			return not self.is_grey()
		return False

class List(is_files):
	def __init__(self):
		super(List, self).__init__()
	
	def show(self):
		for i, filename in enumerate(listdir):
			self.i = i
			self.filename = '{0}\\{1}'.format(listdir[i], listfile[i])
			self._progbar(i)
			self.sel_tx[i] = self.exist()
			self.sel[i] = self.is_image() if args.all else self.sel[i]
			self.sel[i] = self.is_grey() if args.grey else self.sel[i]
			self.sel[i] = self.is_color() if args.color else self.sel[i]
		print('{0:.1%} | {1:#>33}\n'.format(1, '#'))
		self._result()

class Create(is_files):
	def __init__(self):
		super(Create, self).__init__()

	def create(self):
		for i, filename in enumerate(listdir):
			self.i = i
			self.filename = '{0}\\{1}'.format(listdir[i], listfile[i])
			self._progbar(i)
			if self.is_image():
				self.sel[i] = 1
				self.sel[i] = self.is_grey() if args.grey else self.sel[i]
				self.sel[i] = self.is_color() if args.color else self.sel[i]
				if self.sel[i]:
					maketx = args.maketx + ' --oiio'
					if args.colorconvert:
						maketx += ' --colorconvert'
						maketx += ' {}'.format(args.csfrom)
						maketx += ' {}'.format(args.csto)
					maketx += ' "{}"'.format(self.filename)
					os.system(maketx)
		print('{0:.1%} | {1:#>33}\n'.format(1, '#'))

class Remove(is_files):
	def __init__(self):
		super(Remove, self).__init__()

	def remove(self):
		for i, filename in enumerate(listdir):
			self.i = i
			self.filename = '{0}\\{1}'.format(listdir[i], listfile[i])
			self._progbar(i)
			if self.is_image():
				self.sel[i] = self.exist()
				self.sel[i] = self.is_grey() if args.grey else self.sel[i]
				self.sel[i] = self.is_color() if args.color else self.sel[i]
				if self.sel[i]:
					*fname, ext = self.filename.split('.')
					fname = self.filename.replace(ext, 'tx')
					os.remove(fname)
		print('{0:.1%} | {1:#>33}\n'.format(1, '#'))

def main():
	if args.list:
		L = List()
		L.show()
	if args.create:
		M = Create()
		M.create()
	if args.remove:
		M = Remove()
		M.remove()

if __name__ == '__main__':
	main()