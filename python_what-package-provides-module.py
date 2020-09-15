#!/usr/bin/python3

import sys
import os.path
import importlib.util
import importlib_metadata
import pathlib
import subprocess
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-m", "--module", help="Find matching package for the specified Python module",
							type=str)
#parser.add_argument("-u", "--username", help="Database username",
#                           type=str)
#parser.add_argument("-p", "--password", help="Database password",
#                           type=str)
parser.add_argument("-d", "--debug", help="Debug messages are enabled",
							action="store_true")
args = parser.parse_args()

TESTMODULE='serial'

def debugPrint (message="Nothing"):
	if args.debug:
		print ("[DEBUG] %s" % str(message))

class application ():
	def __init__(self, argsPassed):
		self.argsPassed = argsPassed
		debugPrint("Got these arguments:\n%s" % (argsPassed))
		self.location = ""
		self.packageStr = ""

	def run (self):
		#debugPrint("Running with args:\n%s" % (self.argsPassed))
		try:
			if self.argsPassed.module is not None:
				self.moduleName = self.argsPassed.module  #i.e. the module that you're trying to match with a package.
			else:
				self.moduleName = TESTMODULE
				print("[WARN] No module name supplied - defaulting to %s!" % (TESTMODULE))
			try:
				self.location = importlib.util.find_spec(self.moduleName).origin
				debugPrint("self.location: %s" % self.location)
			except:
				print("[ERROR] No module with that name found!")
				raise
			if len(self.location) > 0:
				try:
					self.locationStr = self.location.split("site-packages/",1)[1]
					debugPrint("self.locationStr: %s" % self.locationStr)
					#serial/__init__.py
				except:
					print("[ERROR] location does not contain \"site-packages/\" substring!\nFound location: %s" % self.location)
					raise
			else:
				print("[ERROR] Zero length location string! Exiting.")
				exit(2)
		except:
			print("[ERROR] Parsing module \"%s\"!\nlocation: %s\nExiting." % (self.moduleName, self.location))
			exit(1)

		try:
			self.getPackage()
		except Exception as e:
			print ("[ERROR] getPackage failed: %s" % str(e))
			pass

		try:
			distResult = self.getDistribution(self.location)
			self.packageStrDist = distResult.metadata['Name']
			print(self.packageStrDist)
		except Exception as e:
			print ("[ERROR] getDistribution failed: %s" % str(e))
			pass

		debugPrint("Parent package for \"%s\" is: \"%s\"" % (self.moduleName, self.packageStr))
		return self.packageStr

	def getPackage (self):
		locationDir = self.location.split(self.locationStr,1)[0]
		debugPrint("locationDir: %s" % locationDir)
		#/usr/lib/python3.6/site-packages
		cmd='find \"' + locationDir + '\" -type f -iname \'RECORD\' -printf \'\"%p\"\\n\' | xargs grep \"' + self.locationStr + '\" -l -Z'
		debugPrint("Find command: " + cmd)
		#find "/usr/lib/python3.6/site-packages" -type f -iname 'RECORD' -printf '"%p"\n' | xargs grep "serial/__init__.py" -l -Z

		#return_code = os.system(cmd)
		#return_code = subprocess.run([cmd], stdout=subprocess.PIPE, universal_newlines=True, shell=False)
		#findResultAll = return_code.stdout
		findResultAll = b''
		try:
			findResultAll = subprocess.check_output(cmd, shell=True)    # Returns stdout as byte array, null terminated.
		except Exception as e:
			print ("[ERROR] find failed: %s" % str(e))
			pass
		if findResultAll:
			findResult = str(findResultAll.decode('ascii').strip().strip('\x00'))
			debugPrint("findResult: %s" % findResult)
			#/usr/lib/python3.6/site-packages/pyserial-3.4.dist-info/RECORD
		else:
			print("[ERROR] Cannot find a RECORD file for this module in %s!\nFound location: %s\nExiting." % (locationDir, self.location))
			exit(1)

		findDir = os.path.split(findResult)
		self.packageStr = findDir[0].replace(locationDir,"")
		debugPrint("self.packageStr: %s" % self.packageStr)

	def getDistribution(self, fileName=TESTMODULE):
		result = None
		for distribution in importlib_metadata.distributions():
			try:
				relative = (pathlib.Path(fileName).relative_to(distribution.locate_file('')))
			#except ValueError:
			#except AttributeError:
			except:
				pass
			else:
				if relative in distribution.files:
					result = distribution
		return result

if __name__ == '__main__':
	result=1
	try:
		prog = application(args)
		result = prog.run()
	except Exception as E:
		print ("[ERROR] Prog Exception: %s" % str(E))
	finally:
		sys.exit(result)

# exit the program if we haven't already
print ("Shouldn't get here.")
sys.exit(result)
