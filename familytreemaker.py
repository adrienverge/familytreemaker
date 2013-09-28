#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2013 Adrien Vergé

"""familytreemaker

This program creates family tree graphs from simple text files.

The input file format is very simple, you describe persons of your family line
by line, children just have to follow parents in the file. Persons can be
repeated as long as they keep the same name or id. An example is given in the
file LouisXIVfamily.txt.

This script outputs a graph descriptor in DOT format. To make the image
containing the graph, you will need a graph drawer such as GraphViz.

For instance:

$ ./familytreemaker.py -a 'Louis XIV' LouisXIVfamily.txt | \
	dot -Tpng -o LouisXIVfamily.png

will generate the tree from the infos in LouisXIVfamily.txt, starting from
Louis XIV and saving the image in LouisXIVfamily.png.

"""

__author__ = "Adrien Vergé"
__copyright__ = "Copyright 2013, Adrien Vergé"
__license__ = "GPL"
__version__ = "1.0"

import argparse
import random
import re
import sys

class Person:
	"""This class represents a person.

	Characteristics:
	- name			real name of the person
	- id			unique ID to be distinguished in a dictionnary
	- attr			attributes (e.g. gender, birth date...)
	- households	list of households this person belongs to
	- follow_kids	boolean to tell the algorithm to display this person's
					descendent or not

	"""

	def __init__(self, desc):
		self.attr = {}
		self.parents = []
		self.households = []

		desc = desc.strip()
		if '(' in desc and ')' in desc:
			self.name, attr = desc[0:-1].split('(')
			self.name = self.name.strip()
			attr = map(lambda x: x.strip(), attr.split(','))
			for a in attr:
				if '=' in a:
					k, v = a.split('=')
					self.attr[k] = v
				else:
					self.attr[a] = True
		else:
			self.name = desc

		if 'id' in self.attr:
			  self.id = self.attr['id']
		else:
			self.id = re.sub('[^0-9A-Za-z]', '', self.name)
			if 'unique' in self.attr:
				  self.id += str(random.randint(100, 999))

		self.follow_kids = True

	def __str__(self):
		return self.name

	def dump(self):
		return	'Person: %s (%s)\n' % (self.name, str(self.attr)) + \
				'  %d households' % len(self.households)

	def graphviz(self):
		label = self.name
		if 'surname' in self.attr:
			label += '\\n« ' + str(self.attr['surname']) + '»'
		if 'birthday' in self.attr:
			label += '\\n' + str(self.attr['birthday'])
			if 'deathday' in self.attr:
				label += ' † ' + str(self.attr['deathday'])
		elif 'deathday' in self.attr:
			label += '\\n† ' + str(self.attr['deathday'])
		if 'notes' in self.attr:
			label += '\\n' + str(self.attr['notes'])
		opts = ['label="' + label + '"']
		opts.append('style=filled')
		opts.append('fillcolor=' + ('F' in self.attr and 'bisque' or
					('M' in self.attr and 'azure2' or 'white')))
		return self.id + '[' + ','.join(opts) + ']'

class Household:
	"""This class represents a household, i.e. a union of two person.

	Those two persons are listed in 'parents'. If they have children, they are
	listed in 'kids'.

	"""

	def __init__(self):
		self.parents = []
		self.kids = []
		self.id = 0
	
	def __str__(self):
		return	'Family:\n' + \
				'\tparents  = ' + ', '.join(map(str, self.parents)) + '\n' \
				'\tchildren = ' + ', '.join(map(str, self.kids))

	def isempty(self):
		if len(self.parents) == 0 and len(self.kids) == 0:
			return True
		return False

class Family:
	"""Represents the whole family.

	'everybody' contains all persons, indexed by their unique id
	'households' is the list of all unions (with or without children)

	"""

	everybody = {}
	households = []

	invisible = '[shape=circle,label="",height=0.01,width=0.01]';

	def add_person(self, string):
		"""Adds a person to self.everybody, or update his/her info if this
		person already exists.

		"""
		p = Person(string)
		key = p.id

		if key in self.everybody:
			self.everybody[key].attr.update(p.attr)
		else:
			self.everybody[key] = p

		return self.everybody[key]

	def add_household(self, h):
		"""Adds a union (household) to self.households, and updates the
		family members infos about this union.

		"""
		if len(h.parents) != 2:
			print('error: number of parents != 2')
			return

		h.id = len(self.households)
		self.households.append(h)

		for p in h.parents:
			if not h in p.households:
				p.households.append(h)

	def find_person(self, name):
		"""Tries to find a person matching the 'name' argument.

		"""
		# First, search in ids
		if name in self.everybody:
			return self.everybody[name]
		# Ancestor not found in 'id', maybe it's in the 'name' field?
		for p in self.everybody.values():
			if p.name == name:
				return p
		return None
		
	def populate(self, f):
		"""Reads the input file line by line, to find persons and unions.

		"""
		h = Household()
		while True:
			line = f.readline()
			if line == '': # end of file
				if not h.isempty():
					self.add_household(h)
				break
			line = line.rstrip()
			if line == '':
				if not h.isempty():
					self.add_household(h)
				h = Household()
			elif line[0] == '#':
				continue
			else:
				if line[0] == '\t':
					p = self.add_person(line[1:])
					p.parents = h.parents
					h.kids.append(p)
				else:
					p = self.add_person(line)
					h.parents.append(p)

	def find_first_ancestor(self):
		"""Returns the first ancestor found.

		A person is considered an ancestor if he/she has no parents.

		This function is not very good, because we can have many persons with
		no parents, it will always return the first found. A better practice
		would be to return the one with the highest number of descendant.
		
		"""
		for p in self.everybody.values():
			if len(p.parents) == 0:
				return p

	def next_generation(self, gen):
		"""Takes the generation N in argument, returns the generation N+1.

		Generations are represented as a list of persons.

		"""
		next_gen = []

		for p in gen:
			if not p.follow_kids:
				continue
			for h in p.households:
				next_gen.extend(h.kids)
				# append mari/femme

		return next_gen

	def get_spouse(household, person):
		"""Returns the spouse or husband of a person in a union.

		"""
		return	household.parents[0] == person \
				and household.parents[1] or household.parents[0]

	def display_generation(self, gen):
		"""Outputs an entire generation in DOT format.

		"""
		# Display persons
		print('\t{ rank=same;')

		prev = None
		for p in gen:
			l = len(p.households)

			if prev:
				if l <= 1:
					print('\t\t%s -> %s [style=invis];' % (prev, p.id))
				else:
					print('\t\t%s -> %s [style=invis];'
						  % (prev, Family.get_spouse(p.households[0], p).id))

			if l == 0:
				prev = p.id
				continue
			elif len(p.households) > 2:
				raise Exception('Person "' + p.name + '" has more than 2 ' +
								'spouses/husbands: drawing this is not ' +
								'implemented')

			# Display those on the left (if any)
			for i in range(0, int(l/2)):
				h = p.households[i]
				spouse = Family.get_spouse(h, p)
				print('\t\t%s -> h%d -> %s;' % (spouse.id, h.id, p.id))
				print('\t\th%d%s;' % (h.id, Family.invisible))

			# Display those on the right (at least one)
			for i in range(int(l/2), l):
				h = p.households[i]
				spouse = Family.get_spouse(h, p)
				print('\t\t%s -> h%d -> %s;' % (p.id, h.id, spouse.id))
				print('\t\th%d%s;' % (h.id, Family.invisible))
				prev = spouse.id
		print('\t}')

		# Display lines below households
		print('\t{ rank=same;')
		prev = None
		for p in gen:
			for h in p.households:
				if len(h.kids) == 0:
					continue
				if prev:
					print('\t\t%s -> h%d_0 [style=invis];' % (prev, h.id))
				l = len(h.kids)
				if l % 2 == 0:
					# We need to add a node to keep symmetry
					l += 1
				print('\t\t' + ' -> '.join(map(lambda x: 'h%d_%d' % (h.id, x), range(l))) + ';')
				for i in range(l):
					print('\t\th%d_%d%s;' % (h.id, i, Family.invisible))
					prev = 'h%d_%d' % (h.id, i)
		print('\t}')

		for p in gen:
			for h in p.households:
				if len(h.kids) > 0:
					print('\t\th%d -> h%d_%d;'
					      % (h.id, h.id, int(len(h.kids)/2)))
					i = 0
					for c in h.kids:
						print('\t\th%d_%d -> %s;'
						      % (h.id, i, c.id))
						i += 1
						if i == len(h.kids)/2:
							i += 1

	def output_descending_tree(self, ancestor):
		"""Outputs the whole descending family tree from a given ancestor,
		in DOT format.

		"""
		# Find the first households
		gen = [ancestor]

		print('digraph {\n' + \
		      '\tnode [shape=box];\n' + \
		      '\tedge [dir=none];\n')

		for p in self.everybody.values():
			print('\t' + p.graphviz() + ';')
		print('')

		while gen:
			self.display_generation(gen)
			gen = self.next_generation(gen)

		print('}')

def main():
	"""Entry point of the program when called as a script.

	"""
	# Parse command line options
	parser = argparse.ArgumentParser(description=
			 'Generates a family tree graph from a simple text file')
	parser.add_argument('-a', dest='ancestor',
						help='make the family tree from an ancestor (if '+
						'omitted, the program will try to find an ancestor)')
	parser.add_argument('input', metavar='INPUTFILE',
						help='the formatted text file representing the family')
	args = parser.parse_args()

	# Create the family
	family = Family()

	# Populate the family
	f = open(args.input, 'r', encoding='utf-8')
	family.populate(f)
	f.close()

	# Find the ancestor from whom the tree is built
	if args.ancestor:
		ancestor = family.find_person(args.ancestor)
		if not ancestor:
			raise Exception('Cannot find person "' + args.ancestor + '"')
	else:
		ancestor = family.find_first_ancestor()

	# Output the graph descriptor, in DOT format
	family.output_descending_tree(ancestor)

if __name__ == '__main__':
	main()
