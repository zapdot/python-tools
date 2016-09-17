#!/usr/bin/env python
import sys
import os.path

from zaplib.api.cloudbuild import CloudBuildAPI
from zaplib.api.github import GitHubAPI

def get_dirty_targets(latest_hash):
	result = []

	build_targets = [bt for bt in cb.get_buildtargets() if bt['enabled']]

	for bt in build_targets:
		build_info = bt.get('build', None)

		if build_info and build_info['sha'] == latest_hash:
			continue
		else:
			result.append(bt['buildtargetid'])

	return result

if __name__ == '__main__':

	## arguments
	if len(sys.argv) != 2:
		print "error: invalid arguments"
		print "%s [CONFIGBOX_ID]\n" % os.path.basename(__file__)
		sys.exit(-1)
	else:
		filename, cbox_id = sys.argv

	## setup
	cb = CloudBuildAPI(cbox_id)
	github = GitHubAPI(cbox_id)

	# get targets that need builds
	develop_sha = github.commit("develop").sha
	targets = get_dirty_targets(develop_sha)

	for target in targets:
		cb.create_build(target)