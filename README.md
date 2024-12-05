# SubE2C

SubE2C is a Python tool designed to convert English subtitles to Traditional Chinese (Zh-TW) using the Anthropic API.

## Folder Structure
```
SubE2C/
├── Subs/
│   └── sample.srt
├── Outputs/
│   └── translated_sample.srt
├── src/
│   └── SubE2C.py
├── requirements.txt
└── README.md
```
## Requirements

- Python 3.x
- Anthropic API key

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/chrisxp1223/SubE2C.git
    cd SubE2C
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Set up your Google Gemini API key as an environment variable:
    ```sh
    export ANTHROPIC_API_KEY='your_api_key_here'
    ```

2. Run the script:
    ```sh
    python src/SubE2C.py
    ```

3. Follow the prompts to enter the input and output SRT file paths and your Anthropic API key if not set as an environment variable.

## Example

Place your English subtitle file in the `Subs/` directory, for example, `sample.srt`. Then run the script and provide the paths when prompted:

```sh
Enter the input SRT file path: [sample.srt](SubE2C/Subs)
Enter the output SRT file path: Outputs/translated_sample.srt