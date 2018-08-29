'''
'   By MH and CYJ
'''

import re
import os

input2 = raw_input("Input: ")
search = raw_input("Search: ")
src_dict = (input2) # Specify base directory
pattern = re.compile (search) # Pattern to search for
 
for dirs, subdirs, filenames in os.walk(src_dict): # obtain list of files in directory
    for name in filenames:
        files = os.path.join(src_dict, name) # join the full path with the names of the files.
        strng = open(files) # We need to open the files
        for lines in strng.readlines(): # We then need to read the files
            if re.search(pattern, lines): # If we find the pattern we are looking for
                print (os.path.join(dirs, name)+ " " + lines[:-1])
