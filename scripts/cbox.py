#!/usr/bin/env python
import sys
import os
import argparse
import json
from shutil import copyfile

from pprint import pprint

'''
	cbox.py <id> 
		<key> <key> <key> 
		--value <val> 
		--list <val> <val> <val> <val>
		--template <id>
		--setup
'''

##### Helper Methods

def setup_configbox():
	from zaplib import configbox

	global CONFIGBOX_PATH 
	CONFIGBOX_PATH = configbox.PATH

def error_exit(msg):
	print "> error: {}".format(msg)
	sys.exit(-1)

def config_load(id, is_template=False):

	cfg_dir = os.path.join(CONFIGBOX_PATH, "template" if is_template else "config")
	path_file = os.path.abspath(os.path.join(cfg_dir, "{}.json".format(id)))

	result = {}

	if os.path.exists(path_file):
		with open(path_file, 'r') as file:
			result = json.load(file)
	else:
		error_exit("config '{}' not found.".format(id))

	return result

def config_save(id, data):
	path_file = os.path.abspath(os.path.join(CONFIGBOX_PATH, "config", "{}.json".format(id)))

	updated = os.path.exists(path_file)

	with open(path_file, 'w+') as config:
		json.dump(data, config, indent=4)

	print "> {} {}.".format(id, "updated" if updated else "created")

def print_vals(val, indent=0):

	if isinstance(val, dict):
		for key in val:
			if isinstance(val[key], dict):
				print "{}{}:".format(' '*indent, key)
				print_vals(val[key], indent+2)
			elif isinstance(val[key], list):
				print "{}{}: {}".format(' '*indent, key, ", ".join(val[key]) if val[key] else "** NOT SET **")
			else:
				print"{}{}: {}".format(' '*indent, key, val[key] if val[key] else "** NOT SET **")

	elif isinstance(val, list):
		print "{}{}".format(' '*indent, ", ".join(val) if val else "** NOT SET **")
	else:
		print"{}{}".format(' '*indent, val if val else "** NOT SET **")

def get_val(keys, data):
	result = {}

	try:
		result = reduce(lambda d,k: d[k], keys, data)
	except KeyError as e:
		key = e.args[0]
		error_exit("key '{}' not found.".format(key))

	return result

def merge_dicts(data, template):

	# report unique keys from data to alert obsolete information
	if isinstance(data, dict) and isinstance(template, dict):
		unique_keys = list(set(data.keys()) - set(template.keys()))
		if unique_keys:
			print "> warning: keys don't exist in template: {}".format(", ".join(unique_keys))

	# merge in any missing keys from the template, warn of type mismatches.
	for k in template:
		if k in data:
			if type(data[k]) != type(template[k]):
				print "> warning: type mismatch for key '{}', skipping.".format(k)
			elif isinstance(template[k], dict):
				data[k] = merge_dicts(data[k], template[k])
		else:
			data[k] = template[k]

	return data


##### Argument Methods

def setup(path):
	if not path:
		path = '.'

	path = os.path.abspath(path)

	cfg_dir = os.path.join(path, "config")
	tmpl_dir = os.path.join(path, "template")

	if not os.path.exists(cfg_dir):
		os.makedirs(cfg_dir)

	if not os.path.exists(tmpl_dir):
		os.makedirs(tmpl_dir)

	print "* place templates in: {}".format(tmpl_dir)
	print "* set envvar CONFIGBOX_PATH to: {}".format(path)
	print "> setup complete."

def show_value(id, keys):

	# print the api/keys info
	if keys:
		print "{}[{}]:".format(id, "][".join(keys))
	else:
		print "{}:".format(id)

	# get the value of referencing into the api by the keys
	result = get_val(keys, config_load(id))

	# show the result
	print_vals(result, indent = 2)
	print ""

def set_value(id, keys, val):

	data = config_load(id)
	key = keys[-1]

	# get the parent data of the value we want to set
	if len(keys) > 1:
		subdata = get_val(keys[:-1], data)
	else: 
		subdata = data

	# set the data if the values have the same types
	if type(subdata[key]) == type(val):
		subdata[key] = val
	else:
		error_exit("input type '{}' doesn't match config type '{}'".format(type(val).__name__, type(subdata[key]).__name__))

	config_save(id, data)


def update_from_template(id, template):

	cfg_file = os.path.join(CONFIGBOX_PATH, "config", "{}.json".format(id))
	tmpl_file = os.path.join(CONFIGBOX_PATH, "template", "{}.json".format(template))

	if not os.path.exists(tmpl_file):
		error_exit("could not find file '{}'".format(tmpl_file))

	if os.path.exists(cfg_file):
		cfg_data = config_load(id)
		tmpl_data = config_load(template, is_template = True)

		cfg_data = merge_dicts(cfg_data, tmpl_data)
		config_save(id, cfg_data)

	else:
		data = config_load(template, is_template = True)
		config_save(id, data)

######## Main Application

def main():
	
	# setup configbox path.
	setup_configbox()

	# parse the arguments
	parser = argparse.ArgumentParser(description='Manage configurations for the local user.')
	parser.add_argument('id', nargs='?', help='alphanumeric id for your config.')
	parser.add_argument('key', nargs='*', help='key(s) to traverse the data')

	group = parser.add_mutually_exclusive_group()
	group.add_argument('--value', metavar='val', 
						type=lambda s: unicode(s, 'utf8'), 
					   	help='set the path to a value')

	group.add_argument('--list', metavar='val', nargs='+', 
						type=lambda s: unicode(s, 'utf8'),
					   	help='set the path to a list of values')

	group.add_argument('--template', metavar='name', 
						help='merges in any new keys from template, warns of obsolete keys.')

	group.add_argument('--setup', metavar='path',
						help='setup the given path for ConfigBox.')

	args = parser.parse_args()

	action = any([args.value, args.list, args.template, args.setup])

	if not CONFIGBOX_PATH:
		parser.error("CONFIGBOX_PATH is missing. Did you run --setup?")
	elif not args.id and not args.setup:
		parser.error("<id> required.")

	if args.setup:
		setup(args.setup)
	elif args.id and not action:
		show_value(args.id, args.key)
	elif args.id and args.key and (args.value or args.list):
		set_value(args.id, args.key, args.value or args.list)
	elif args.id and args.template:
		update_from_template(args.id, args.template)

if __name__ == '__main__':	
	main()