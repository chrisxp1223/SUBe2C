import os
import sys
import logging
import time
from anthropic import Anthropic
import srt

def get_output_filename():
    """
    Prompt user for output filename and perform basic validation.
    Returns the filename entered by user (without path).
    """
    while True:
        try:
            # Prompt user for filename
            filename = input("\nPlease enter your output filename (.srt): ").strip()
            # If user enters nothing
            if not filename:
                print("Filename cannot be empty. Please try again.")
                continue
            # If user includes .srt, use their input, otherwise append it
            if not filename.endswith('.srt'):
                filename += '.srt'
            # Basic check for length before more detailed validation
            if len(filename) > 255:
                print("Filename is too long. Please enter a shorter name.")
                continue
            return filename
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            raise
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Please try again.")


def validate_srt_file(file_path):
   # Check file extension
   if not file_path.lower().endswith('.srt'):
       print("Error: File must be an SRT subtitle file (ending with .srt)")
       return False
   
   # Try to parse the SRT file
   try:
       with open(file_path, 'r', encoding='utf-8') as f:
           content = f.read().strip()
           if not content:
               print("Error: SRT file is empty.")
               return False
           list(srt.parse(content))
       return True
   except Exception as e:
       print(f"Error: Invalid SRT file format. Please check if the file is a valid subtitle file.")
       return False

def get_input_file():
   # Ask for input file name
   file_name = input("Enter the subtitle file name in Subs folder: ")
   
   # Construct full file path
   file_path = os.path.join("Subs", file_name)
   
   # Check if file exists
   if not os.path.exists(file_path):
       print(f"Error: File '{file_name}' not found in Subs folder. Please check the file name and try again.")
       return None
   else:
       print(f"File '{file_name}' found in Subs folder.") 
   
   if file_path and validate_srt_file(file_path):
       return file_path
   
   return None

def main():

    # User input the file name
    # a. check the file name under Subs folder 
    # b. check if it is a valid file
    
    file_path = get_input_file()

    if file_path is None:
        print("Exiting due to invalid input file.")
        return

    # ask user for the output file name
    get_output_filename ()
    # check the api key exist in the environment variable
    # if not, ask user to input the api key, if the api key is valid, save it to the environment variable
    # if the api key is invalid, ask user to input again
    # validate the api key by connection test

if __name__ == "__main__":
    main()