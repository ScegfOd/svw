# Written by JJC aka ScegfOd, no license here...
# Disclaimer: by using this script you agree not to sue me or hold me accountable in anyway for anything bad that happens.

# this file is for turning .feature files with (cucumber in them) into .py test files (with stubs inside)

# you can either run it in a directory with a bunch of .feature files for it to find by itself
# or you can supply paths to feature files in the terminal

import pathlib
import re
import sys
import os

def get_steps(feature_file):
	if pathlib.Path(feature_file).is_file():
		with ff as open(feature_file, 'r'):
			#first clean out comments
			steps = list()
			for line in ff:
				line = line.strip()
				if len(line) == 0 or line[0] == '#' or line[0] == '@':
					continue # skip comments, tags, and whitespace
				prev_match = 'given'
				if re.match('^[Gg]iven', line):
					prev_match = 'given'
				elif re.match('^[Tt]hen', line):
					prev_match = 'then'
				elif re.match('^[Ww]hen', line):
					prev_match = 'when'
				line = line[0].lower() + line[1:]
				line = re.sub('^([Bb]ut|[Aa]nd|\*)', prev_match, line)
				steps.append(line)
			return steps
	print(f"Error: couldn't read {feature_file}!\n")
	return None

# generate steps folder if it isn't there
os.makedirs(os.path.dirname('./steps/'), exist_ok=True)

# make a stup environment file if it isn't there
env_file = './environment.py'
if not pathlib.Path(env_file).is_file():
	with env_stub as open(env_file, 'r'):
		env_stub.write("""from selenium import webdriver
#from path_to_poms import pom_name_here

# before_all, as you might expect, runs before all of our Cucumber features
def before_all(context):
	context.driver = webdriver.FireFox() # the one true browser
    #context.my_pom_abbreviation = pom_name_here(context.driver)

def before_step(context, step):
    pass

def before_scenario(context, scenario):
    pass

def before_feature(context, feature):
    pass

def before_tag(context, tag):
    pass

def after_tag(context, tag):
    pass

def after_feature(context, feature):
    pass

def after_scenario(context, scenario):
    pass

def after_step(context, step):
    pass

def after_all(context):
    context.driver.quit()""")

# if args given, they're the feature files to get
if len(sys.argv) > 1:
	file_list = []
	for arg in sys.argv[1:]:
		if arg.find('.feature') != -1: # tab complete or else
			file_list.append(arg)
# if no args given, just run it on every .feature in the same dir
else:
	this_dir = pathlib.Path().resolve()
	file_list = this_dir.glob("*.feature")

for feature_file in file_list:
	steps = get_steps(feature_file)
	if not steps:
		continue

	#then turn them into steps
	scenario_count = 0
	this_file = open(feature_file) # so we don't have to check before closing
	for step in steps:
		# each feature gets its own testing file
		if step.find('feature:') == 0:
			this_file.close()
			filename = './steps/'
			filename += re.sub(' ', '_', step[8:].strip()).lower() + '.py'
			if pathlib.Path(filename).is_file():
				print("\nWELP, a test file has the auto-generated name, "+\
					f"appending to '{filename}'\n")
			else:
				print(f"Creating '{filename}'")
			this_file = open(filename, 'a')
			this_file.write('\n###################################'+\
				'###################################\n')
			this_file.write('#these tests auto generated with svw.py'+\
				' (salt, vinegar, & water) -JJC#')
			this_file.write('\n###################################'+\
				'###################################\n')
			this_file.write('\nfrom behave import *\n')

		elif step.find('background:') == 0:
			this_file.write(f'\n#Background: ')
			this_file.write(step[9:].strip() + '\n')

		elif step.find('scenario:') == 0:
			scenario_count += 1
			this_file.write(f'\n#Scenario #{scenario_count}: ')
			this_file.write(step[9:].strip() + '\n')

		# if it's actually a 'step' and needs a test stub:
		elif re.match('^(given|then|when)', step):
			description = ""
			if re.match('^given',step):
				description = step[5:].strip()
				this_file.write(f"\n@given('{description}')")
			elif re.match('^then',step):
				description = step[4:].strip()
				this_file.write(f"\n@then('{description}')")
			else: #when
				description = step[4:].strip()
				this_file.write(f"\n@when('{description}')")
			description = re.sub(' ', '_', description).lower()
			this_file.write(f"\ndef step_{description}(context):")
			this_file.write(f"\n\tpass\n\n")
		else: #TODO any keywords I don't know....
			print()
			print("I don't know how to handle")
			print("'" + step + "'")
			print("ignoring it and moving on with everything else...")
	this_file.close() # close the final open file in the loop
