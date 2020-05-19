# Utility script for Jenkins.  Must be run on a Mac since it runs Apple utilities.
# Takes four arguments:
#   * bundle ID
#	* Apple ID of account used to create the app-specific password (I think--anyhow, an Apple accound ID)
#	* app-specific password
#	* path to compressed app to send for notarization

import subprocess
import sys
import time
import urllib

if len(sys.argv) != 6:
	print "NotarizeAndPollAppleServers.py: need bundle ID, Apple ID, app password, polling time in minutes, and path to zip file."
	exit(-1)

bundleID = sys.argv[1]
appleID = sys.argv[2]
appSpecificPassword = sys.argv[3]
pollMinutes = float(sys.argv[4])
appZipPath = sys.argv[5]

print "NotarizeAndPollAppleServers.py: Starting notarization."
try:
	uploadOutput = subprocess.check_output(['xcrun', '--verbose', '--log', 'altool', '--notarize-app', '--primary-bundle-id', bundleID, '-u', appleID, '-p', appSpecificPassword, '--file', appZipPath], stderr=subprocess.STDOUT)
except Exception, e:
	print "NotarizeAndPollAppleServers.py: Exception in notarization:"
	print str(e)
	exit(-2)
	
print "NotarizeAndPollAppleServers.py: upload output: "
print uploadOutput

requestIDIndex = uploadOutput.find("RequestUUID = ")
if requestIDIndex == -1:
	print "NotarizeAndPollAppleServers.py: Unable to upload for notarization."
	exit(-3)

requestID = uploadOutput[requestIDIndex + len("RequestUUID = "):].strip()
print "Request ID: ", requestID

# Every pollMinutes minutes we poll the Apple servers for a result.
print "NotarizeAndPollAppleServers.py: Upload succeeded.  Will poll for outcome every ", pollMinutes, " minutes."

while True:
	pollOutput = ""
	try:
		pollOutput = subprocess.check_output(['xcrun', '--verbose', '--log', 'altool', '--notarization-info', requestID, '-u', appleID, '-p', appSpecificPassword], stderr=subprocess.STDOUT)
		print "NotarizeAndPollAppleServers.py: poll output: "
		print pollOutput
		
		# check for successful notarization
		pollOutputLower = pollOutput.lower()
		if "package approved" in pollOutputLower:
			print "NotarizeAndPollAppleServers.py: Notarization succeeded."
			notarizationReportURLIndex = pollOutput.find("LogFileURL: ")
			if notarizationReportURLIndex == -1:
				print "NotarizeAndPollAppleServers.py: Unable to find notarization report URL in output from Apple notarization server."
			else:
				notarizationReportURL = pollOutput[notarizationReportURLIndex + len("LogFileURL: "):].splitlines()[0].strip()
				notarizationReportContents = urllib.urlopen(notarizationReportURL).read()
				print "NotarizeAndPollAppleServers.py: notarization report: "
				print notarizationReportContents
			exit(0)
			
		# check for failed notarization
		elif "fail" in pollOutput or "error" in pollOutputLower and not "in progress" in pollOutputLower:
			print "NotarizeAndPollAppleServers.py: Notarization failed."
			exit(-4)
			
	except subprocess.CalledProcessError, cpe:
		print "NotarizeAndPollAppleServers.py: Exception in polling:"
		print str(cpe)
		print "Output of command:"
		print cpe.output
		print "Will try again in ", pollMinutes, " minutes."

	except Exception, e:
		print "NotarizeAndPollAppleServers.py: Exception in polling:"
		print str(e)
		print "Will try again in ", pollMinutes, " minutes."
		
	time.sleep(pollMinutes * 60)
