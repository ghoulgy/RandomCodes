import uncompyle6
import sys
import os

dir_path = sys.argv[1]

for filename in os.listdir(dir_path):
	if filename.endswith('.pyc'):
		pyc_full_path = os.path.join(dir_path + filename)
		decompiled_full_path = os.path.join(dir_path + filename + '_decompiled')
		with open(decompiled_full_path, 'w') as f:
			uncompyle6.decompile_file(pyc_full_path, f)
