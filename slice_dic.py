#!/usr/bin/env python

import sys

warning = '''
usage:
	slice_dict.py dict.txt size
'''
if len(sys.argv) <= 1: 
	print warning
	sys.exit(-1)

class Fileholder():
	def __init__(self, filename=None, mode='wb'):
		if filename:
			self.fd = open(filename, mode)
		else:
			self.fd = None
	
	def change(self, filename=None, mode='wb'):
		if self.fd:
			self.fd.close()
		self.fd = open(filename, mode)
		print 'change to: ', filename
	
	def write(self, content):
		if self.fd:
			self.fd.write(content) 

f = Fileholder()
source = sys.argv[1]
if sys.argv[2]:
	size = int(sys.argv[2])
else:
	print warning
	sys.exit(-1)
cnt = 0 
count = 0

for line in open(source):
	if count % size == 0:
		cnt += 1
		f.change(source.split('.')[-2]+str(cnt)+'.txt')	
	f.write(line)
	count += 1
else:
	print 'finished'

