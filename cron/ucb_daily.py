#!/usr/bin/env python
import sys
import os.path

from zaplib.api.cloudbuild import CloudBuildAPI
from zaplib.api.github import GitHubAPI

def get_dirty_targets(latest_hash, filter=None):
	result = []

	build_targets = [bt for bt in cb.get_buildtargets() if bt['enabled']]

	if filter:
		build_targets = [bt for bt in build_targets if filter in bt['buildtargetid']]

	for bt in build_targets:
		build_info = bt.get('build', None)

		if build_info and build_info['sha'] == latest_hash:
			continue
		else:
			result.append(bt['buildtargetid'])

	return result

if __name__ == '__main__':

	target_filter = None

	## arguments
	if len(sys.argv) == 2:
		filename, cbox_id = sys.argv
	elif len(sys.argv) == 3:
		filename, cbox_id, target_filter = sys.argv
	else:
		print "error: invalid arguments"
		print "%s [CONFIGBOX_ID] ([TARGET_FILTER])\n" % os.path.basename(__file__)
		sys.exit(-1)

	## setup
	cb = CloudBuildAPI(cbox_id)
	github = GitHubAPI(cbox_id)

	# get targets that need builds
	develop_sha = github.commit("develop").sha
	targets = get_dirty_targets(develop_sha, target_filter)

	for target in targets:
		cb.create_build(target)				
