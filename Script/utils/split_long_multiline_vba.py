"""
' Spliting very long line of vba multiline string into different sub functions and print out those strings accordingly
"""

def code_replace(seg_num, vba_long_str):
    vba_long_str = vba_long_str.rstrip("& _\n")
    code_str = f"Sub code_segment_{seg_num}\nDebug.Print <PLACE_HOLDER>\nEnd Sub\n"
    code_str = code_str.replace("<PLACE_HOLDER>", vba_long_str)
    print(code_str)


def generate_main_func(seg_num):
    print("Sub main()")
    for i in range(seg_num):
        print(f"\tcode_segment_{i}")
    print("End Sub")


with open("long_text_vba.txt", "r") as f:
    lines = f.readlines()
f.close()

vba_long_str = ""
seg_num = 0
for idx, line in enumerate(lines):
    vba_long_str += line

    # Line splitting
    if idx != 0 and idx % 24 == 0: # Since vba macro have line limit per function
        code_replace(seg_num, vba_long_str)
        seg_num += 1

        # Cleanup
        vba_long_str = ""

    elif idx == len(lines) - 1: # Just for last segment
        code_replace(seg_num, vba_long_str)
        seg_num += 1

# Generate final function
generate_main_func(seg_num)
