import os
import sys
import logging
import time
import google.generativeai as genai
from pysrt import SubRipFile, SubRipItem
from google.api_core import exceptions

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_gemini_api_connection(api_key=None):
    """
    Test the Google Gemini API connection using the provided API key.
    If no API key is provided, it attempts to use the GOOGLE_API_KEY environment variable.
    
    :param api_key: Google Gemini API key (optional)
    :return: True if connection is successful, False otherwise
    """
    if not api_key:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("Error: No API key provided and GOOGLE_API_KEY environment variable not set.")
            return False
    
    try:
        # Configure the library with your API key
        genai.configure(api_key=api_key)
        
        # Initialize the model
        model = genai.GenerativeModel('gemini-pro')
        
        # Generate a simple response
        response = model.generate_content("Hello, are you working?")
        
        # Check if the response is valid
        if response.text:
            print("API connection successful!")
            print("Response:", response.text)
            return True
        else:
            print("API connection failed. No valid response received.")
            return False
    
    except Exception as e:
        print(f"API connection failed. Error: {str(e)}")
        return False
def translate_text(text, model):
    max_retries = 3
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            response = model.generate_content(f"Translate the following English text to Chinese: {text}")
            return response.text
        except exceptions.GoogleAPIError as e:
            if e.code == 429:  # Too Many Requests
                if attempt < max_retries - 1:
                    logging.warning(f"Rate limit hit. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logging.error("Max retries reached. Please try again later.")
                    raise
            else:
                logging.error(f"Google API Error: {e}")
                raise
        except Exception as e:
            logging.error(f"Unexpected error in translate_text: {e}")
            raise

def translate_subtitles(input_file, output_file, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        subs = SubRipFile.open(input_file)
        
        for i, sub in enumerate(subs):
            try:
                translated_text = translate_text(sub.text, model)
                sub.text = translated_text
                logging.info(f"Translated subtitle {i+1}/{len(subs)}")
                time.sleep(1)  # Add a 1-second delay between requests
            except Exception as e:
                logging.error(f"Error translating subtitle {i+1}: {e}")
                continue
        
        subs.save(output_file, encoding='utf-8')
    except Exception as e:
        logging.error(f"Error in translate_subtitles: {e}")
        raise


def main():

    input_file = input("Enter the input SRT file path: ")
    output_file = input("Enter the output SRT file path: ")

    gemini_api_key = os.getenv("GOOGLE_API_KEY")
    if not gemini_api_key:
        gemini_api_key = input("Enter your Google Gemini API key: ")
    if not gemini_api_key:
        raise ValueError("Google Gemini API key not found")
    else:
        print("OpenAI API key found")

    success = test_gemini_api_connection()
    print(f"Connection test {'succeeded' if success else 'failed'}.")

    translate_subtitles(input_file, output_file, gemini_api_key)
    logging.info(f"Translation completed. Output saved to {output_file}")
    # 7. read the srt file
    # 8. translate the srt file
    # 9. write the translated srt file


if __name__ == "__main__":
    main()