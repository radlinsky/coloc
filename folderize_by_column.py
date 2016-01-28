#!/usr/bin/python

### folderize_by_column.py
### Caleb Matthew Radens
### 2015_1_26

### This script parses a file by a specified column, and writes to
###  file groups of rows that match. Files are named by their row group. 
###
###  Arguments:
###    input_file.txt: input txt file
###	 valid filepath   
###    Column_#: which column to group by
###	 integer
###    output_directory/: where should files by written to?
###      Extant directory
###    keep_*: which columns from the file to keep when writing new files.
###      keep_all = keep all columns in new files
###      keep_0_1_2 = keep first 3 columns in new files
###      keep_6_2_4 = keep the 7th, 3rd, and 5th columns..
###
###  Assumptions:
###    The file is bash-sortable by the column of interest
###    The 'Column_#' command line argument is a valid column index
###	Type = <int>
###     (0 = first column)
###    The column of interest has no empty values
###    The column of interest does not have any rows with value='INITIATED'
###    The file is not zipped/compressed
###    The file is a .txt file
###    There is a single line header
###
###  Usage:
###    python folderize_by_gene.py input_file.txt Column_# output_directory/ keep_*

import sys
import os
import gzip
import csv
from subprocess import call

print "Initiating folderize_by_column.py"
print "Argument List:", str(sys.argv[1:])

if (len(sys.argv) != 5):
	raise Exception("Expected four command arguments.")
in_FILE = str(sys.argv[1])
Column_index = int(sys.argv[2])
out_DIR = str(sys.argv[3])
Keep = str(sys.argv[4])

if (in_FILE[-4:] != ".txt"):
	raise Exception("Expected 1st command argument to be a file name ending in '.txt'")
if not (os.path.isfile(in_FILE)):
	raise ValueError(in_FILE+" not found. Is it a *full* and valid file path?")
if not type(Column_index) is int or Column_index < 0:
	raise Exception("Column index needs to be an integer >= 0.")
if not (os.path.isdir(out_DIR)):
	raise ValueError(out_DIR+" not found. Is it a valid directory?")
if out_DIR[-1] != "/":
	raise ValueError("The out directory needs to end with a forward slash.")
if not "keep_" in Keep:
	raise ValueError("'keep_*' argument needs to start with 'keep_'")
after_keep = Keep[len("keep_"):]
if len(after_keep) == 0:
	raise ValueError("Please specify 'all' or 'col#_col#_etc' after 'keep_'. Saw: "+after_keep)
if "all" in after_keep:
	if any(char.isdigit() for char in after_keep):
		raise ValueError("Please only choose one: 'all' or 'col#_col#_etc' after 'keep_'")
	if len(after_keep[len("all"):]) > 0:
		raise ValueError("Expected nothing after 'keep_all' but saw: keep_all"+after_keep)
	# Temporarily make cols_to_keep = "all" (it will be over-written later)
	cols_to_keep = "all"
# Note:
#	any(char.isdigit() for char in STRING_OF_INTEREST)
#	This checks if there are any digits in the STRING_OF_INTEREST
elif any(char.isdigit() for char in after_keep):
	split_keep = after_keep.split("_")
	cols_to_keep = list()
	for keep_col in split_keep:
		if not keep_col.isdigit:
			raise ValueError("Expected 'keep_#_#...', but instead of #, saw: "+keep_col)
		cols_to_keep.append(int(keep_col))
else:
	raise ValueError("'keep_*' argument isn't properly formatted. Looked like: "+Keep)
		
print "Passed script checks."
print "Keeping column(s): "+str(cols_to_keep)

all_row_groups = list()
row_group = "INITIATED"

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
	if Header:
		# Save the header to out_file
		command = "head " + in_file_path + " -n 1 > " + out_file_path
		call([command], shell= True)
		# Which column will be sorted by
		sort_at = str(Col)+","+str(Col)
		# This sorts the file, but skips the header when sorting it, and writes teh result to file
		command = "tail -n +2 " + in_file_path + " | sort -k " + sort_at + " >> " + out_file_path
		call([command], shell = True)
	# Else no header
	else:
		# Sort the file at specified column
		sort_at = str(Col)+","+str(Col)
		command = "sort "+in_file_path + " -k " + sort_at + " > " + out_file_path
		call([command], shell=True)

	return out_file_path

try:
	in_FILE = bash_sort(File = in_FILE, 
				In_dir = "",
				Out_dir = "",
				Col = Column_index+1,
				Header = True)
except BaseException:
	raise StandardError("bash_sort failed.")

f_IN = open(in_FILE, 'rb')
line_i = 1
for line in f_IN:
	# Remove newline chars and split by tab
	split_line = line.rstrip('\r\n').split('\t')
	# First line is header, save it and look at the next line
	if line_i == 1:
		# If you want to keep all columns:
		if cols_to_keep == "all":
			# Get number of columns in header of file
			n_cols = len(split_line)
			# make keep_col a list of all column indeces
			cols_to_keep = range(n_cols)
		# For each # in keep_col list, add the corresponding column from split_line to head
		head = [split_line[col_i] for col_i in cols_to_keep]
		line_i = line_i + 1
		continue

	if split_line[Column_index] == "":
		raise ValueError("Row value was empty at line: "+str(line_i)+". That's not cool.")

	if row_group == "INITIATED":
		# Initialize row_group list
		row_group_list = list()
		
		# Extract the value of the first row in the col of interest
		row_group = split_line[Column_index]
		# Add row_group to list
		row_group_list.append(row_group)
		# Add which line we're at to the list
		row_group_list.append(line_i)

		# Start saving the head and 1st line of data to row_group file list
		row_group_file = list()
		row_group_file.append(head)
		kept_cols = [split_line[col_i] for col_i in cols_to_keep]
		row_group_file.append(kept_cols)

	# If this line's row_group is the same as the last, add it to the row_group file list
	elif split_line[Column_index] == row_group:
		kept_cols = [split_line[col_i] for col_i in cols_to_keep]
		row_group_file.append(kept_cols)

	# Check if current line of file's row_group is different from the last line checked
	elif split_line[Column_index] != row_group:
		# Add which line was last added (now we have the first and last lines)
		row_group_list.append(line_i-1)
		all_row_groups.append(row_group_list)

		# Write the contents of the row_group file list to a csv in its own directory
		filename = out_DIR+row_group+"/"+row_group+".BED.csv"
		if not os.path.exists(os.path.dirname(filename)):
			try:
				os.makedirs(os.path.dirname(filename))
			except OSError as exc: # Guard against race condition
				if exc.errno != errno.EEXIST:
					raise
		with open(filename, "wb") as f:
			writer = csv.writer(f)
			writer.writerows(row_group_file)

		# Re-initialize summary list
		row_group_list = list()
		# Add the first row_group row to the row_group list
		row_group = split_line[Column_index]
		row_group_list.append(row_group)
		row_group_list.append(line_i)

		# Re-initialize file list
		row_group_file = list()
		row_group_file.append(head)
		kept_cols = [split_line[col_i] for col_i in cols_to_keep]
		row_group_file.append(kept_cols)

	line_i = line_i + 1
f_IN.close()

for row_group in all_row_groups:
	print row_group[0]+": "+str(row_group[2]-row_group[1]+1)+" element(s)."
print "Completed folderize_by_column.py"
