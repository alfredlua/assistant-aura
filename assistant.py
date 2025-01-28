import os
from dotenv import load_dotenv 
import json
import textwrap
from tabulate import tabulate

import google.generativeai as genai

from config import ORCHESTRATOR_PROMPT, PLAN_CRITIC_PROMPT, RETRIEVER_PROMPT, RESEARCHER_PROMPT, PARSER_PROMPT
from tools.retriever import get_tasks
from tools.researcher import scrape_static_source, scrape_dynamic_source
from tools.parser import parse_text
from utils import extract_xml

load_dotenv()
gemini_api_key=os.getenv("GOOGLE_GEMINI_API_KEY")

class Assistant:
  """
  A template for the various assistants
  """

  def __init__(self, role_prompt, tools):
    genai.configure(api_key=gemini_api_key)
    self.gemini_model = genai.GenerativeModel(
      model_name="gemini-1.5-flash",
      system_instruction=role_prompt,
      tools=tools
    )
    self.messages = []
    role_mapping = {
        ORCHESTRATOR_PROMPT: "orchestrator",
        PLAN_CRITIC_PROMPT: "critic",
        RETRIEVER_PROMPT: "retriever",
        RESEARCHER_PROMPT: "researcher",
        PARSER_PROMPT: "parser"
    }
    self.role = role_mapping.get(role_prompt, None)
    self.log = []

  def print_messages(self):
    return self.messages
  
  def generate_text(self):
    try:
      return self.gemini_model.generate_content(self.messages)
    except Exception as e:
      return f"error: str({e})"
    
  def process_user_input(self, user_message, chatmate):
    self.messages.append({"role": "user", "parts": f"<{chatmate}>{user_message}</{chatmate}>"})
    response = self.generate_text()
    return self.process_response(response)

  functions = {
    "get_tasks": get_tasks,
    "scrape_static_source": scrape_static_source,
    "scrape_dynamic_source": scrape_dynamic_source,
    "parse_text": parse_text,
  }

  def call_function(self, func_name, func_params):
    return self.functions[func_name](**func_params)
  
  def process_response(self, response):
    queue = [response]
    result = ''
    while queue:
      current_response = queue.pop(0)
      self.log.append({current_response})
      current_response_dict = type(current_response).to_dict(current_response)
      parts = current_response_dict['candidates'][0]['content']['parts']
      self.messages.append({"role": "model", "parts": parts})
      for part in parts:
        if part.get('function_call'):
          tool_use = part['function_call']
          func_name = tool_use['name']
          func_params = tool_use['args']
          tool_result = self.call_function(func_name, func_params)
          self.messages.extend([
            {"role": "user", "parts": [{"text": f"<tool_result>{tool_result}</tool_result>"}]},
            {"role": "model", "parts": [{"text": f"{tool_result}"}]},
          ])
          result += tool_result
        else:
          if part['text'].strip():
            result += part['text']
            if self.role == "orchestrator":
              orchestrator_response = extract_xml(part['text'], "response")
              plan = json.loads(extract_xml(part['text'], "plan"))
              print(f"Orchestrator: {orchestrator_response} \n\n Plan:\n")
              # Prepare data for tabulate
              max_width = 50
              table_data = []
              for step in plan["plan"]:
                table_data.append([
                    "\n".join(textwrap.wrap(step["step"], width=max_width)),
                    step["teammate"],
                    step["status"]
                ])
              headers = ["Step", "Teammate", "Status"]
              print(tabulate(table_data, headers=headers, tablefmt="grid"))
              print("\n")
    if result:
      return result
    else:
      return f"Error: There was no result. Please try again."
