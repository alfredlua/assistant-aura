import os
from dotenv import load_dotenv 

import google.generativeai as genai

load_dotenv()
api_key=os.getenv("GOOGLE_GEMINI_API_KEY")

genai.configure(api_key=api_key)

def parse_text(path: str, instruction: str) -> str:
  """
  Given a file and instruction, use an LLM to extract the required information in a suitable format for post-processing.
  
  Args:
    path: The path to a file with the text to be parsed.
    instruction: The prompt for an LLM to extract the required information from the html file.

  Returns:
    A json of the result.
  """

  print(f'Using parse_text with {path} and {instruction}\n')

  with open(path, 'r') as file:
    text = file.read()
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(instruction + "/nHere's the HTML:/n" + text)
  if response:
    return response.text
  else:
    return "No matches found"