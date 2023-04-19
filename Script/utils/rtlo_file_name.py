"""
Simple right-to-left overide file name creation
To do it manually, go to the link below and copy the unicode and paste it when you create a new file/folder
https://old.unicode-table.com/en/202E/
"""
import os

file_name = "Invoice_zby\u202etxt.js"
full_file_path = os.path.join(os.path.dirname(__file__), file_name)

with open(full_file_path, "w", encoding='utf-8') as f:
    f.close()
