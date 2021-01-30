import json 
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("encoded_string_code", help="encoded string code")
parser.add_argument("mapped_json_file", help="mapped json string file")
args = parser.parse_args()

esc = args.encoded_string_code
mjf = args.mapped_json_file

# load encoded code file
with open(esc, "r") as f:
  replace_content = f.read()
f.close()

# load json file
f = open(mjf) 
mapped_data = json.load(f)

# Find and Replace based on the mapped json file
for enc_str in mapped_data.keys():
  fun_enc_str = "mo427a(\"" + enc_str + "\")"
  if fun_enc_str in replace_content:
    replace_content = replace_content.replace(fun_enc_str, mapped_data[enc_str])

with open('out.txt', 'w') as wf:
  wf.write(replace_content)
wf.close()