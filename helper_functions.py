#/usr/bin/python

# helper_functions.py
# Caleb Matthew Radens
# 2016_1_26

### A bunch of helper functions I think I'll use a lot

import os
from subprocess import call
import gzip


def remove_all(array, element):
	""" Remove all instances of element from array.

		Arguments:
			array 	= array type object.
			element = object that you wish to remove all of from array.
	"""
	if type(array) != type([]):
		raise Exception("Please only give arrays to this function.")
	n = array.count(element)
	while n > 0:
		array.remove(element)
		n = array.count(element)

def index_all(array, element):
	"""Return all indeces of array that point to an element.

		Arguments:
			array 	= array type object.
			element = object that you wish to get indeces for from array.
	"""
	if type(array) != type([]):
		raise Exception("Please only give arrays to this function.")

	matched_indices = [i for i, x in enumerate(array)if x == element]
	return matched_indices

def make_scisub_job_command(
	Script,
	ScriptDir,
	Queue = "voight_normal",
	ErrOut=True,
	ErrOutDir = "",
	Extra=""):
	"""Generate an appropriately formatted string for submitting a *python* job on pmacs.
	
	Arguments:
		Script: 		"script_to_execute.py"
		ScriptDir: 		"/directory_with_script/"
		Queue:			Scisub -q command. Should be: "voight_normal" (default),
							"voight_long", or "voight_priority"
		ErrOut:			Boolean. Should the job save log files?
		ErrOutDir:		"/directory_for_log_files/"
		Extra:			Optional string. If the script takes command line arguments,
							add them here.

	Depends on: os

	Returns a string formatted for scisub job submission.

		Example usage:
		make_scisub_job_command(
			Script="my_script.py",
			ScriptDir="/project/voight_subrate/.../scripts/",
			Queue = "voight_normal",
			ErrOut=True,
			ErrOutDir = "/project/voight_subrate/.../logs/",
			Extra="cowabung baby")

		Example output :
		(note, output is a list of 2 strings with no line breaks/newlines, I just broke them here
			to ease visualization)

		['bsub -e /project/voight_subrate/.../logs/my_script.err
			   -o /project/voight_subrate/.../logs/my_script.out
			   -q voight_normal
			   python /project/voight_subrate/.../scripts/my_script.py cowabunga baby',
		'IS_COMMAND']
	"""
	if (type(Script) is not str 
		or type(ScriptDir) is not str 
		or type(Queue) is not str 
		or type(ErrOutDir) is not str 
		or type(Extra) is not str):
		raise ValueError("All arguments (except ErrOut) need to be strings.")
	if type(ErrOut) is not bool:
		raise ValueError("ErrOut needs to be a boolean.")

	if Script[-2:] != "py":
		raise ValueError("Expected a .py python script, instead got: "+Script)

	if not (os.path.isdir(ScriptDir)):
		raise ValueError(ScriptDir+" not found.")
	if ScriptDir[-1] != "/":
		raise ValueError("ScriptDir needs to end with a forward slash.")

	if not os.path.isfile(ScriptDir+Script):
		raise ValueError(Script+" not found in "+ScriptDir)

	if (Queue != "voight_normal" 
		and Queue != "voight_long"
		and Queue != "voight_priority"):
		raise ValueError(
			"Expected voight_normal, voight_long, or voight_priority, instead got: "+Queue)

	if len(ErrOutDir) > 0:	
		if not (os.path.isdir(ErrOutDir)):
			raise ValueError(ErrOutDir+" not found.")
		if ErrOutDir[-1] != "/":
			raise ValueError("ErrOutDir needs to end with a forward slash.")

	if len(Extra) > 0:
		# Add space before the extra commands
		if Extra[0] == " ":
			raise ValueError("No space in the beginning of Extra, please.")
		Extra = " "+Extra

	if ErrOut:
		command = "bsub -e "+ErrOutDir+Script[0:-2]+"err "
		command = command + "-o "+ErrOutDir+Script[0:-2:]+"out "
		command = command + "-q "+Queue
		command = command + " python "+ScriptDir+Script+Extra
	else:
		command = "bsub "
		command = command + "-q "+Queue
		command = command + " python "+ScriptDir+Script+Extra

	return [command, "IS_SCISUB_COMMAND"]

def submit_scisub_job(Command):
	""" Given the output from make_scisub_job_command, submit a job.
	"""
	if type(Command) is not list:
		raise ValueError("Command isn't from make_scisub_job_command...(not a list)")
	if Command[1] != "IS_SCISUB_COMMAND":
		raise ValueError("Command isn't from make_scisub_job_command...(where is 'IS_SCISUB_COMMAND'?)")

	# Submit a system command
	call([Command[0]],shell=True)

def make_consign_job_command(
	Script,
	ScriptDir,
	ErrOut=True,
	ErrOutDir = "",
	Extra=""):
	"""Generate an appropriately formatted string for submitting a *python* job on consign.pmacs
	
	Arguments:
		Script: 		"script_to_execute.py"
		ScriptDir: 		"/directory_with_script/"
		ErrOut:			Boolean. Should the job save log files?
		ErrOutDir:		"/directory_for_log_files/"
		Extra:			Optional string. If the script takes command line arguments,
							add them here.

	Depends on: os

	Returns a string formatted for consign job submission.

		Example usage:
		make_consign_job_command(
			Script="my_script.py",
			ScriptDir="/project/chrbrolab/.../scripts/",
			ErrOut=True,
			ErrOutDir = "/project/chrbrolab/.../logs/",
			Extra="cowabung baby")

		Example output :
		(note, output is a list of 2 strings with no line breaks/newlines,
			 I just broke them here	to ease visualization)

		['bsub 	-e /project/chrbrolab/.../logs/my_script.err
			-o /project/chrbrolab/.../logs/my_script.out
			python /project/chrbrolab/.../scripts/my_script.py cowabunga baby',
		'IS_CONSIGN_COMMAND']
	"""
	if (type(Script) is not str 
		or type(ScriptDir) is not str 
		or type(ErrOutDir) is not str 
		or type(Extra) is not str):
		raise ValueError("All arguments (except ErrOut) need to be strings.")
	if type(ErrOut) is not bool:
		raise ValueError("ErrOut needs to be a boolean.")

	if Script[-2:] != "py":
		raise ValueError("Expected a .py python script, instead got: "+Script)

	if not (os.path.isdir(ScriptDir)):
		raise ValueError(ScriptDir+" not found.")
	if ScriptDir[-1] != "/":
		raise ValueError("ScriptDir needs to end with a forward slash.")

	if not os.path.isfile(ScriptDir+Script):
		raise ValueError(Script+" not found in "+ScriptDir)

	if len(ErrOutDir) > 0:	
		if not (os.path.isdir(ErrOutDir)):
			raise ValueError(ErrOutDir+" not found.")
		if ErrOutDir[-1] != "/":
			raise ValueError("ErrOutDir needs to end with a forward slash.")

	if len(Extra) > 0:
		# Add space before the extra commands
		if Extra[0] == " ":
			raise ValueError("No space in the beginning of Extra, please.")
		Extra = " "+Extra

	if ErrOut:
		command = "bsub -e "+ErrOutDir+Script[0:-2]+"err "
		command = command + "-o "+ErrOutDir+Script[0:-2:]+"out "
		command = command + " python "+ScriptDir+Script+Extra
	else:
		command = "bsub "
		command = command + " python "+ScriptDir+Script+Extra

	return [command, "IS_CONSIGN_COMMAND"]

def submit_consign_job(Command):
	""" Given the output from make_consign_job_command, submit a job.
	"""
	if type(Command) is not list:
		raise ValueError("Command isn't from make_consign_job_command...(not a list)")
	if Command[1] != "IS_CONSIGN_COMMAND":
		raise ValueError("Command isn't from make_consign_job_command...(where is 'IS_CONSIGN_COMMAND'?)")

	# Submit a system command
	call([Command[0]],shell=True)

def gz_head(File, Dir="", Lines=10):
	""" Preview top Lines of a file.gz

		Arguments:
			File: 	"my_fav_file.txt.gz" [needs to be a .gz file]
			Dir: 	"/my_directory/" [optional, you may make File a the full filepath instead.]
			Lines:	Integer greater than 0.
			Split:	Optional string. If 
	"""
	if type(File) is not str or type(Dir) is not str:
		raise ValueError("All arguments need to be strings.")
	if type(Lines) is not int or Lines < 1:
		raise ValueError("Lines needs to be an integer > 0.")
	if len(Dir) > 0:	
		if not (os.path.isdir(Dir)):
			raise ValueError(Dir+" not found.")
		if Dir[-1] != "/":
			raise ValueError("Dir needs to end with a forward slash.")
	if File[-2:] != "gz":
		raise ValueError("File needs to ba a .gz file.")
	if not os.path.isfile(Dir+File):
		raise ValueError(File+" not found in directory\n"+Dir)

	path = Dir+File
	# 'rb' means read
	f_IN = gzip.open(path, 'rb')
	for line in f_IN:
		if Lines == 0:
			break
		# Remove newline chars and split by tab
		split_line = line.rstrip('\r\n').split('\t')
		print split_line
		print '\n'
		Lines = Lines-1
	f_IN.close()

def my_head(File, Dir="", Lines=10):
	""" Preview top Lines of a (non gz) file

		Arguments:
			File: 	"my_fav_file.txt"
			Dir: 	"/my_directory/" [optional, you may make File a the full filepath instead.]
			Lines:	Integer greater than 0.
	"""
	if type(File) is not str or type(Dir) is not str:
		raise ValueError("All arguments need to be strings.")
	if type(Lines) is not int or Lines < 1:
		raise ValueError("Lines needs to be an integer > 0.")
	if len(Dir) > 0:	
		if not (os.path.isdir(Dir)):
			raise ValueError(Dir+" not found.")
		if Dir[-1] != "/":
			raise ValueError("Dir needs to end with a forward slash.")
	if File[-2:] == "gz":
		raise ValueError("Please do not use this function on .gz files.")
	if not os.path.isfile(Dir+File):
		raise ValueError(File+" not found in directory\n"+Dir)

	path = Dir+File
	with open(path, 'rb') as the_file:
		content = the_file.readlines()
		for line in content:
			if Lines == 0:
				break
			# Remove newline chars and split by tab
			# split_line = line.rstrip('\r\n').split('\t')
			print line
			Lines = Lines-1

def bash_sort(File, In_dir, Out_dir, Col, Header = True):
	""" Bash sort a file, return location of sorted file.

		Arguments:
			File: 	"my_fav_file.txt"
			In_dir: "/my_directory/" [optional, you may make File a the full filepath instead
			Out_dir:"/some_dir" where sorted file is saved
			Col:	integer. Which column to sort by? [1 = first column]
			Header: boolean. Does the file have a header?

		Assumptions:
			File is not gz-zipped (or compressed at all)
			File ends in '.'txt'
			File has a single lined header, or no header

		Returns: filepath of the sorted file
	"""
	if type(File) is not str or type(In_dir) is not str or type(Out_dir) is not str:
		raise ValueError("File, In_dir, and Out_dir need to be strings.")
	if type(Col) is not int or Col < 0:
		raise ValueError("Col needs to be an integer > 0.")
	if len(In_dir) > 0:	
		if not (os.path.isdir(In_dir)):
			raise ValueError(In_dir+" not found.")
		if In_dir[-1] != "/":
			raise ValueError("In_dir needs to end with a forward slash.")
	if len(Out_dir) > 0:	
		if not (os.path.isdir(Out_dir)):
			raise ValueError(Out_dir+" not found.")
		if Out_dir[-1] != "/":
			raise ValueError("Out_dir needs to end with a forward slash.")
	if File[-4:] != ".txt":
		raise ValueError("Please only use this function on .txt files.")
	if not os.path.isfile(In_dir+File):
		raise ValueError(File+" not found in directory\n"+In_dir)

	print "Passed bash_sort checks."

	in_file_path = In_dir + File
	out_file_path = Out_dir + File[:-4]+"_sorted.txt"
	print out_file_path
	if Header:
		# Save the header to out_file
		command = "head " + in_file_path + " -n 1 > " + out_file_path
		print "bash_sort command looks like: \n"+command
		call([command], shell= True)
		# Which column will be sorted by
		sort_at = str(Col)+","+str(Col)
		# This sorts the file, but skips the header when sorting it, and writes teh result to file
		command = "tail -n +2 " + in_file_path + " | sort -k " + sort_at + " >> " + out_file_path
		print "bash_sort command looks like: \n"+command
		call([command], shell = True)
	# Else no header
	else:
		# Sort the file at specified column
		sort_at = str(Col)+","+str(Col)
		command = "sort "+in_file_path + " -k " + sort_at + " > " + out_file_path
		print "bash_sort command looks like: \n"+command
		call([command], shell=True)

	return out_file_path

