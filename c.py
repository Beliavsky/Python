""" functions to process C and C++ code """

import os
import sys
import glob

def remove_c_comments(c_code):
    """
    Remove /* */ block comments and // line comments from C/C++ code.
    
    Args:
        c_code (str): Multiline string containing C/C++ code.
    
    Returns:
        str: Multiline string with comments removed.
    """
    result = []
    i = 0
    in_block_comment = False
    in_line_comment = False
    in_string = False
    string_char = None
    
    while i < len(c_code):
        # Handle string literals to avoid removing comments inside them
        if not in_block_comment and not in_line_comment:
            if c_code[i] in ('"', "'") and (i == 0 or c_code[i-1] != '\\'):
                if in_string and c_code[i] == string_char:
                    in_string = False
                    string_char = None
                elif not in_string:
                    in_string = True
                    string_char = c_code[i]
                result.append(c_code[i])
                i += 1
                continue
        
        # Handle block comments
        if not in_string and not in_line_comment:
            if c_code[i] == '/' and i + 1 < len(c_code) and c_code[i + 1] == '*':
                in_block_comment = True
                i += 2
                continue
            elif in_block_comment and c_code[i] == '*' and i + 1 < len(c_code) and c_code[i + 1] == '/':
                in_block_comment = False
                i += 2
                continue
        
        # Handle line comments
        if not in_string and not in_block_comment:
            if c_code[i] == '/' and i + 1 < len(c_code) and c_code[i + 1] == '/':
                in_line_comment = True
                i += 2
                continue
            elif in_line_comment and c_code[i] == '\n':
                in_line_comment = False
                result.append(c_code[i])
                i += 1
                continue
        
        # Copy character if not in a comment
        if not in_block_comment and not in_line_comment:
            result.append(c_code[i])
        i += 1
    
    return ''.join(result)

def remove_c_comments_dir(directory, print_original=False):
    """
    Loop over *.c files in the specified directory, remove comments, and print to stdout.
    
    Args:
        directory (str): Directory containing *.c files (default: 'foo').
        print_original (bool): If True, print original code before cleaned code.
    """
    # Ensure directory exists
    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' does not exist.", file=sys.stderr)
        return
    
    # Find all *.c files
    c_files = glob.glob(os.path.join(directory, "*.c"))
    
    if not c_files:
        print(f"No *.c files found in directory '{directory}'.", file=sys.stderr)
        return
    
    for c_file in c_files:
        try:
            # Read the C file
            with open(c_file, 'r', encoding='utf-8') as f:
                c_code = f.read()
            
            # Remove comments
            cleaned_code = remove_c_comments(c_code)
            
            # Print to stdout
            print(f"\n=== {c_file} ===")
            if print_original:
                print("--- Original Code ---")
                print(c_code)
                print("--- Cleaned Code ---")
            else:
                print("--- Cleaned Code ---")
            print(cleaned_code)
        
        except Exception as e:
            print(f"Error processing {c_file}: {e}", file=sys.stderr)
