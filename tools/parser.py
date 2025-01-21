import os
from dotenv import load_dotenv 

import google.generativeai as genai

load_dotenv()
api_key=os.getenv("GOOGLE_GEMINI_API_KEY")

genai.configure(api_key=api_key)

def parse_text(instruction: str) -> str:
  """
  Given an instruction, use an LLM to extract the required information from the file in a suitable format for post-processing.
  
  Args:
    instruction: The prompt for an LLM to extract the required information from the html file.

  Returns:
    A json of the result.
  """

  # print(f'🤵🏻 Parsing text in temp/working_memory.txt with the instruction: {instruction}...\n')

  # if path.startswith('/'):
  #   path = path[1:]
  
  with open('temp/working_memory.txt', 'r') as file:
    text = file.read()
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(instruction + "/nHere's the HTML:/n" + text)
  if response:
    return response.text
  else:
    return "No matches found"