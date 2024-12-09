import re
import os
import sys
import logging
import time
from anthropic import Anthropic
from dotenv import load_dotenv
from typing import Optional
import srt


def process_srt_file(input_path: str, output_path: str, client: Anthropic) -> bool:
    """
    Process and translate SRT file from English to Traditional Chinese

    Args:
        input_path (str): Path to input SRT file
        output_path (str): Path to output SRT file
        client (Anthropic): Anthropic client object

    Returns:
        bool: True if successful, False if failed
    """
    try:
        # Try different encodings if UTF-8 fails
        encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'latin-1']
        content = None

        for encoding in encodings:
            try:
                with open(input_path, 'r', encoding=encoding) as infile:
                    content = infile.read()
                break
            except UnicodeDecodeError:
                continue

        if content is None:
            raise ValueError("Could not decode the subtitle file with any supported encoding")

        # Split into subtitle blocks and filter empty blocks
        blocks = [block.strip() for block in re.split(r'\n\n+', content.strip()) if block.strip()]
        translated_blocks = []
        total_blocks = len(blocks)

        print("\nStarting translation process...")
        print(f"Total subtitle blocks to translate: {total_blocks}")

        for i, block in enumerate(blocks, 1):
            try:
                # Split block into components
                lines = block.split('\n')
                if len(lines) < 3:
                    print(f"\nWarning: Block {i} has invalid format, skipping...")
                    translated_blocks.append(block)  # Keep original
                    continue

                # Extract components
                subtitle_number = lines[0]
                timestamp = lines[1]
                text_content = '\n'.join(lines[2:])  # Preserve multi-line subtitles

                print(f"\nTranslating block {i}/{total_blocks}")
                print(f"Original text: {text_content}")

                # Translate text content
                translated_text = translate_text(client, text_content)

                if translated_text is None:
                    print(f"Warning: Translation failed for block {i}, keeping original...")
                    translated_text = text_content
                else:
                    print(f"Translated text: {translated_text}")

                # Reconstruct block with translation
                translated_block = f"{subtitle_number}\n{timestamp}\n{translated_text}"
                translated_blocks.append(translated_block)

                # Show progress
                progress = (i / total_blocks) * 100
                print(f"Progress: {progress:.1f}%")

            except Exception as e:
                print(f"\nError processing block {i}: {str(e)}")
                # Keep original block if translation fails
                translated_blocks.append(block)
                continue

        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Write translated content with newline preservation
        with open(output_path, 'w', encoding='utf-8') as outfile:
            outfile.write('\n\n'.join(translated_blocks) + '\n')

        print(f"\nTranslation completed successfully!")
        print(f"Translated file saved to: {output_path}")
        print(f"Total blocks processed: {total_blocks}")
        return True

    except Exception as e:
        print(f"\nError processing SRT file: {str(e)}")
        logging.error(f"SRT processing error: {str(e)}")
        return False

def connect_claude_api(api_key: str) -> Optional[Anthropic]:
    """
    Establish connection with Claude API

    Args:
        api_key (str): Anthropic API key

    Returns:
        Optional[anthropic.Anthropic]: Anthropic client object if successful, None if failed
    """
    try:
        client = Anthropic(api_key=api_key)
        return client
    except Exception as e:
        logging.error(f"Failed to connect to Claude API: {str(e)}")
        return None

def translate_text(client: Anthropic, text: str,
                  max_retries: int = 10, delay: int = 5) -> Optional[str]:
    """
    Translate text from English to Traditional Chinese using Claude API

    Args:
        client (Anthropic): Anthropic client object
        text (str): Text to translate
        max_retries (int): Maximum number of retry attempts
        delay (int): Delay in seconds between retries

    Returns:
        Optional[str]: Translated text if successful, None if failed
    """
    # TODO: Add batch processing for better API call optimization
    # TODO: Add custom instructions to improve translation quality

    prompt = f"""Please translate the following English text to Traditional Chinese (zh-tw).
    Only return the translated text, no explanations or other text.

    Text: {text}
    """

    for attempt in range(max_retries):
        try:
            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return message.content[0].text

        except Exception as e:
            logging.error(f"Translation attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(delay)
                continue
            else:
                logging.error("Max retries reached. Translation failed.")
                return None

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
    # if not, ask user to input the api key, if the api key is valid, save it to the environment variable
    # if the api key is invalid, ask user to input again
    # validate the api key by connection test
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
    output_path = get_output_filename ()
    # if not, ask user to input the api key, if the api key is valid, save it to the environment variable
    # if the api key is invalid, ask user to input again
    # validate the api key by connection test
    client = connect_claude_api(api_key)

    success = process_srt_file(file_path, output_path, client)
    if success:
        print("File processed successfully")
    else:
        print("Error processing file")


if __name__ == "__main__":
    main()
