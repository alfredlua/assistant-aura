"""
A loop that calls the Gemini API and several tools.
"""

import os
from dotenv import load_dotenv 
import json
from onboarding_message import intro

import google.generativeai as genai
import anthropic

from config import ORCHESTRATOR_PROMPT, PLAN_CRITIC_PROMPT, RESEARCHER_PROMPT, PARSER_PROMPT
from assistant import Assistant
from tools.browser import scrape_static_source, scrape_dynamic_source
from tools.parser import parse_text
from utils import extract_xml

import inquirer

load_dotenv()
gemini_api_key=os.getenv("GOOGLE_GEMINI_API_KEY")
anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")

# Main loop

async def loop():
  """
  The loop for the assistant.
  """

  plan = []
  orchestrator = Assistant(
    role_prompt=ORCHESTRATOR_PROMPT, 
    tools=[])
  plan_critic = Assistant(
    role_prompt=PLAN_CRITIC_PROMPT,
    tools=[]
  )
  researcher = Assistant(
    role_prompt=RESEARCHER_PROMPT, 
    tools=[scrape_static_source, scrape_dynamic_source])
  parser = Assistant(
    role_prompt=PARSER_PROMPT, 
    tools=[parse_text])

  print(f"{intro}🤵🏻 Aura: Hello! How can I help? (Type 'quit' to end the chat)\n")

  while True:
    try:
      user_message = input("You: ")
      if user_message.lower() == "quit":
        print("Exiting chat.")
        break
      # elif user_message.lower() == "restart":
      #   Assistant.messages = []
      #   continue
      elif user_message.lower() == "debug":
        print("Chat History\n\nOrchestrator\n", orchestrator.print_messages(), "\n\nCritic\n", plan_critic.print_messages(), "\n\nResearcher\n", researcher.print_messages(), "\n\nParser\n", parser.print_messages())
        break
      elif user_message.lower() == "log":
        print("Log\n\nOrchestrator\n", orchestrator.log, "\n\nCritic\n", plan_critic.log, "\n\nResearcher\n", researcher.log, "\n\nParser\n", parser.log)
        break
      
      orchestrator_response = orchestrator.process_user_input(user_message, "user")

      # The plan critic will work with the orchestrator to improve the plan.
      iter = 0
      while iter < 3:
        iter += 1
        critic_response = plan_critic.process_user_input(orchestrator_response, "orchestrator")
        if "The plan is good to go!" in critic_response:
          break
        else:
          orchestrator_response = orchestrator.process_user_input(critic_response, "plan_critic")

      # Loop for executing the plan
      all_completed = False
      while all_completed == False:

        # Once the plan is good to be executed, display the plan and update it after every step. If the final answer is available, display it and end the loop.
        plan = extract_xml(orchestrator_response, "plan")
        final_answer = extract_xml(orchestrator_response, "final_answer")
        if final_answer:
          print(f"🤵🏻 Aura: Here's the answer to your request: \n\n{final_answer}")
          break
        elif plan:
          # print(f"\nPLAN:\n{plan}")
          plan_list = json.loads(plan.strip())["plan"]
        else:
          print("There's an issue extracting the plan.")

        # Loop through every step
        for step in plan_list:
          if step["status"].lower() in ["completed", "failed"]:
            continue
          elif step["status"].lower() == "to do":
            if step["teammate"].lower() == "researcher":
              researcher_response = researcher.process_user_input(step["step"], "orchestrator")
              orchestrator_response = orchestrator.process_user_input(researcher_response, "researcher")
              break
            elif step["teammate"].lower() == "parser":
              parser_response = parser.process_user_input(step["step"], "orchestrator")
              orchestrator_response = orchestrator.process_user_input(parser_response, "parser")
              break
            elif step["teammate"].lower() == "orchestrator":
              orchestrator_response = orchestrator.process_user_input(step["step"], "user")
              break
            else:
              print("Invalid teammate specified.")

        if plan_list[-1]["status"].lower() == "completed":
          all_completed = True

    except Exception as e:
      import traceback
      print(f"An error occurred: {e}")
      print("Error type:", type(e).__name__)
      print("Traceback:", traceback.format_exc())

# Run script

if __name__ == "__main__":
  import asyncio
  asyncio.run(loop())


###############
# Code from the version that supports Claude

# genai.configure(api_key=gemini_api_key)
# gemini_model = genai.GenerativeModel(
#   model_name="gemini-1.5-flash",
#   system_instruction=SYSTEM_PROMPT,
#   tools=[save_screenshot, scrape_static_source, scrape_dynamic_source, parse_text]
# )

# claude_model = anthropic.Anthropic()

# question = [
#   inquirer.List(
#     'choice',
#     message="Choose an AI model",
#     choices=['gemini', 'claude'],
#   ),
# ]

# message_key = ""
# selected_model = inquirer.prompt(question)['choice']
# if selected_model == 'gemini':
#   message_key = "parts"
#   print("You chose gemini.")
# elif selected_model == 'claude':
#   message_key = "content"
#   print("You chose claude.")

# Helper functions

# def generate_text(model, messages):
#   if model == "gemini":
#     return gemini_model.generate_content(messages)
#   elif model == "claude":
#     return claude_model.messages.create(
#       model="claude-3-haiku-20240307", 
#       messages=messages,
#       max_tokens=2048,
#       system=SYSTEM_PROMPT,
#       tools=CLAUDE_TOOLS
#     )
  
# functions = {
#   "scrape_static_source": scrape_static_source,
#   "scrape_dynamic_source": scrape_dynamic_source,
#   "parse_text": parse_text,
#   "save_screenshot": save_screenshot
# }

# def call_function(func_name, func_params):
#     return functions[func_name](**func_params)
  
# def process_response(response):
#   queue = [response]
#   while queue:
#     current_response = queue.pop(0)
#     if selected_model == "gemini":
#       messages.append({"role": "model", message_key: current_response.candidates[0].content.parts})
#       for part in current_response.candidates[0].content.parts:
#         if part.function_call:
#           tool_use = part.function_call
#           func_name = tool_use.name
#           func_params = tool_use.args
#           tool_result = call_function(func_name, func_params)
#           print("🛠️  Tool result:", tool_result, "\n\n------------\n")
#           messages.append({"role": "user", message_key: [{"text": tool_result}]})
#           tool_response = generate_text(selected_model, messages)
#           queue.append(tool_response) 
#         else:
#           if part.text.strip():
#             print(f"\n🤵🏻 Aura ({selected_model}): {part.text}")
#     elif selected_model == "claude":
#       if "error" in current_response:
#          return f"An error occurred: {current_response['error']}"

#       if current_response.content[-1].type == "tool_use":
#           tool_use = current_response.content[-1]
#           func_name = tool_use.name
#           func_params = tool_use.input
#           tool_use_id = tool_use.id

#           tool_result = call_function(func_name, func_params)
#           print("🛠️  Tool result:", tool_result, "\n\n------------\n")

#           messages.append(
#               {"role": "assistant", "content": current_response.content}
#           )
#           messages.append({
#               "role": "user",
#               "content": [{
#                   "type": "tool_result",
#                   "tool_use_id": tool_use_id,
#                   "content": f"{tool_result}",
#               }],
#           })

#           follow_up_response = generate_text(
#               model=selected_model,
#               messages=messages,
#           )
#           queue.append(follow_up_response) 
      
#       elif current_response.content[0].type == "text":
#           response_text = current_response.content[0].text
#           messages.append(
#               {"role": "assistant", "content": response_text}
#           )
#           print(f"\n🤵🏻 Aura ({selected_model}): {response_text}")
      
#       else:
#           raise Exception("An error occurred: Unexpected response type")

# Create report of what the assistant did
# messages.append({"role": "user", message_key: f"Summarize what the model did in first-person narrative. Do not use any tools: {messages}"})
# summary = generate_text(selected_model, messages)
# print(f"\n🤵🏻 Aura ({selected_model}): Here's a summary of what I did:\n\n {summary.text if selected_model == "gemini" else summary.content[0].text}")
