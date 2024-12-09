import os
import sys
import logging
import time
from anthropic import Anthropic
from dotenv import load_dotenv
import srt

def validate_anthropic_key(api_key):
    """
    Validate Anthropic API key by making a test request.
    Returns True if valid, False otherwise.
    """
    try:
        client = Anthropic(api_key=api_key)
        # Make a minimal test request
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1,
            messages=[{
                "role": "user",
                "content": "Hi"
            }]
        )
        return True
    except Exception as e:
        print(f"Error validating API key: {str(e)}")
        return False

def check_anthropic_api_key():
    """
    Check for Anthropic API key in environment variables.
    If not found, prompt user to input it and validate.
    Returns valid API key or None if process is cancelled.
    """
    load_dotenv()  # Load existing environment variables
    
    # Check if API key exists in environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    while not api_key:
        print("\nAnthropic API key not found in environment variables.")
        api_key = input("Please enter your Anthropic API key (or 'q' to quit): ").strip()
        
        if api_key.lower() == 'q':
            return None
            
        # Validate the API key
        if validate_anthropic_key(api_key):
            # Save valid key to .env file
            with open(".env", "a") as env_file:
                env_file.write(f"\nANTHROPIC_API_KEY={api_key}")
            os.environ["ANTHROPIC_API_KEY"] = api_key
            print("API key validated and saved successfully!")
            return api_key
        else:
            print("Invalid API key. Please try again.")
            api_key = None
    
    return api_key

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

    # check the api key exist in the environment variable
    check_anthropic_api_key() 
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        print("Anthropic API key found.")
    else:
        print("Anthropic API key not found, please try another.")
    
    # User input the file name
    # a. check the file name under Subs folder 
    # b. check if it is a valid file
    file_path = get_input_file()

    if file_path is None:
        print("Exiting due to invalid input file.")
        return

    # ask user for the output file name
    get_output_filename ()
    # if not, ask user to input the api key, if the api key is valid, save it to the environment variable
    # if the api key is invalid, ask user to input again
    # validate the api key by connection test

if __name__ == "__main__":
    main()