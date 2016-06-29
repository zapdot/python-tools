#!/usr/bin/env python
import sys
import os
import fnmatch
import json
import argparse
import copy

from zaplib.version import GameVersion

def find_file(search_file, parents=[]):
	for root, dirnames, filenames in os.walk('.'):
	    for filename in fnmatch.filter(filenames, search_file):
	    	abspath = os.path.abspath(os.path.join(root, filename))

	    	if not all(p in abspath for p in parents):
	    		continue

	    	return abspath

	return None

def load_file(search_file, parents=[]):
	result = None
	path = find_file(search_file, parents)

	if path:
		with open(path) as version_json:
			result = json.load(version_json)

	return path, result

def update_file(path, ver):
	ver.saveToFile(path)	

	print "> successfully updated to version {}".format(ver)


def main():
	# parse the arguments
	parser = argparse.ArgumentParser(description='Increment the project version.')
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('--major', action='store_true', help='bump the major version.')
	group.add_argument('--minor', action='store_true', help='bump the minor version.')
	group.add_argument('--patch', action='store_true', help='bump the patch version.')
	group.add_argument('--set', metavar='version', help='set the version to a higher number')

	args = parser.parse_args()

	# first, ensure that we can find version_data below this directory
	path, data = load_file('version_data.json', ['Resources', 'AppInfo'])

	if not data:
		print "error: could not find {}".format(search_file)
		sys.exit(-1)

	curver = Version.from_data(data)

	if args.set:
		newver = Version.from_data(args.set)

		if newver <= curver:
			print "error: ({}) does not increment the current version ({})".format(newver, curver)
			sys.exit(-1)
		else:
			update_file(path, newver)

	else:
		newver = copy.copy(curver)

		if args.major:
			newver.bumpMajor()
		elif args.minor:
			newver.bumpMinor()
		elif args.patch:
			newver.bumpPatch()

		update_file(path, newver)


if __name__ == '__main__':
	main()
	