# Written by JJC aka ScegfOd, no license here...
# Disclaimer: by using this script you agree not to sue me or hold me accountable in anyway for anything bad that happens.

# this file is for turning .feature files with (cucumber in them) into .py test files (with stubs inside)

# you can either run it in a directory with a bunch of .feature files for it to find by itself
# or you can supply paths to feature files in the terminal

import pathlib
import re
import sys

# if no args given, just run it on every .feature in the same dir
if len(sys.argv) > 1:
	file_list = []
	for arg in sys.argv[1:]:
		if arg.find('.feature') != -1:
			file_list.append(arg)
else:
	this_dir = pathlib.Path().resolve()
	file_list = this_dir.glob("*.feature")

for feature_file in file_list:
	if pathlib.Path(feature_file).is_file():
		ff = open(feature_file, 'r')
	else:
		print(f"Error: couldn't read {feature_file}!\n")
		continue

	#first clean out comments
	steps = list()
	for line in ff:
		line = line.strip() + ' ' # for the find function to remove
		line = line[:line.find("#")]
		if len(line): # it's not a comment!
			steps.append(line)

	#then turn them into steps
	scenario_count = 0
	this_file = open(feature_file) # so we don't have to check before closing
	for step in steps:

		# each feature gets its own testing file
		if step.find('Feature:') == 0:
			this_file.close()
			filename = './steps/'
			filename += re.sub(' ', '_', step[8:].strip()).lower() + '.py'
			if pathlib.Path(filename).is_file():
				print("welp, a test file has the auto-generated name, "+\
					f"appending to '{filename}'")
			this_file = open(filename, 'a')
			this_file.write('\n###################################'+\
				'###################################\n')
			this_file.write('#these tests auto generated with svw.py'+\
				' (salt, vinegar, & water) -JJC#')
			this_file.write('\n###################################'+\
				'###################################\n')
			this_file.write('\nfrom behave import*\n')

		# TODO figure out if we do anything special for multiple scenarios...
		elif step.find('Scenario:') == 0:
			scenario_count += 1
			this_file.write(f'\n#Scenario #{scenario_count}: ')
			this_file.write(step[9:].strip() + '\n')

		# if it's actually a 'step' and needs a test stub:
		elif re.match('^(given|then|when|and|but)', step.lower()):
			description = ""
			if re.match('^given',step.lower()):
				description = step[5:].strip()
				this_file.write(f"\n@given('{description}')")
			elif re.match('^then',step.lower()):
				description = step[4:].strip()
				this_file.write(f"\n@then('{description}')")
			else:
				#'but' and 'and' are 3 characters, but there'll need to be a
				# space between the keyword and the description anyway
				description = step[4:].strip()
				this_file.write(f"\n@when('{description}')")
			description = re.sub(' ', '_', description).lower()
			this_file.write(f"\ndef {description}_S{scenario_count}(context):")
			this_file.write(f"\n\tpass\n\n")
		else: #TODO any keywords I don't know....
			print()
			print("I don't know how to handle")
			print("'" + step + "'")
			print("ignoring it and moving on with everything else...")
	this_file.close() # 'cause we didn't close the final open file in the loop
