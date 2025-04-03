""" Generate a description of changes and a commit message from Git diff using
Gemini API. """
import subprocess
import sys
import google.generativeai as genai
import os
import textwrap

def print_wrapped_squeeze_blanks(text, width=80):
    """ Wrap lines > width chars, keep single blank lines, squeeze multiples. """
    # Split into lines and process each
    lines = text.split('\n')
    result = []
    prev_blank = False
    
    for line in lines:
        # Wrap long lines
        wrapped = [line] if len(line) <= width else textwrap.wrap(line, width)
        
        if line.strip():  # Non-blank line
            result.extend(wrapped)
            prev_blank = False
        elif not prev_blank:  # Blank line, but not after another blank
            result.append('')
            prev_blank = True
            
    print('\n'.join(result))

def get_git_diff(filename):
    """Get the diff between current file and last committed version."""
    try:
        # Get the diff using git command
        diff = subprocess.check_output(
            ['git', 'diff', 'HEAD', filename],
            text=True,
            stderr=subprocess.STDOUT
        )
        return diff if diff else "No changes detected in the file."
    except subprocess.CalledProcessError as e:
        return f"Error getting diff: {e.output}"
    except Exception as e:
        return f"Error: {str(e)}"

def generate_commit_message(diff):
    """Generate a commit message using Gemini API."""
    with open(r"c:\python\code\gemini_key.txt", "r") as key_file:
        api_key = key_file.read().strip()
    
    genai.configure(api_key=api_key)
    model_name = "gemini-1.5-flash"
    model = genai.GenerativeModel(model_name)  # Using a fast model
    
    # Create prompt for Gemini
    prompt = (
        "Describe the substantive differences between the local and committed versions of the file"
        f"{diff}. Then provide a one-line commit message, with commit message appearing on its own line."
    )
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating commit message: {str(e)}"

def main():
    # Check if filename is provided as command line argument
    if len(sys.argv) != 2:
        print("Usage: python xgemini_diff.py <filename>")
        sys.exit(1)
        
    filename = sys.argv[1]
    
    # Verify file exists
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    
    diff = get_git_diff(filename) # Get the diff
    
    # Generate and print the commit message
    commit_message = generate_commit_message(diff)
    print_wrapped_squeeze_blanks(commit_message)

if __name__ == "__main__":
    main()
