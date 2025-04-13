import subprocess
import re

def parse_dir_output(file_name):
    """ Reformats 'dir /s' command output for a file into a table
    showing date, time, size, and directory. """
    # Run the dir /s command
    result = subprocess.run(['dir', '/s', file_name], capture_output=True, text=True, shell=True)
    output = result.stdout

    # Regex patterns to match directory and file lines
    dir_pattern = re.compile(r'Directory of (.*?)\s*$')
    file_pattern = re.compile(r'(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2}\s+[AP]M)\s+([\d,]+)\s+' + re.escape(file_name))

    current_dir = ''
    results = []

    # Process each line of the output
    lines = output.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Check for directory line
        dir_match = dir_pattern.match(line)
        if dir_match:
            current_dir = dir_match.group(1).strip()
            i += 1
            continue

        # Check for file line
        file_match = file_pattern.match(line)
        if file_match:
            date, time, size = file_match.groups()
            results.append((date, time, size.replace(',', ''), current_dir))
        i += 1

    # Print formatted table
    if results:
        print("file:", file_name)
    else:
        print("file:", file_name, "not found")
    for date, time, size, directory in results:
        print(f"{date} {time}   {size}   {directory}")

from sys import argv, exit
if len(argv) < 2:
    exit("usage: python xprocess_dir.py <file_name>")
file_name = argv[1]
parse_dir_output(file_name)
