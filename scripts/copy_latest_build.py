# Utility script for Jenkins.
# Takes two arguments:
#   * source root directory
#   * destination directory.
# Identifies the newest subdirectory under the source root directory and copies its
# contenst into the destination directory.
# This is used in assembling the latest version of our app for codesigning/notarization.

import os
import sys
from distutils.dir_util import copy_tree

if len(sys.argv) != 3:
	print "CopyLatestBuild.py: need source path and dest path."
	exit(-1)

sourceRootDirectory = sys.argv[1]
destDirectory = sys.argv[2]

# find the subdirectory of sourceRootDirectory with the newest timestamp
newestSubdirectoryPath = None
newestSubdirectoryModifyTime = 0

for subdirectory in os.listdir(sourceRootDirectory):
	if subdirectory.startswith("."):
		continue;
	subdirectoryPath = os.path.join(sourceRootDirectory, subdirectory)
	subdirectoryModifyTime = os.path.getmtime(subdirectoryPath)
	if subdirectoryModifyTime > newestSubdirectoryModifyTime:
		newestSubdirectoryModifyTime = subdirectoryModifyTime
		newestSubdirectoryPath = subdirectoryPath
		
if newestSubdirectoryPath == None:
	print "CopyLatestBuild.py: Could not find newest subdirectory."
	exit(-2)

print "Copying latest build ", newestSubdirectoryPath, " to ", destDirectory
copy_tree(newestSubdirectoryPath, destDirectory)
