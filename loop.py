"""
A loop that calls the Gemini API and several tools.
"""

import os
from dotenv import load_dotenv 
import json
from onboarding_message import intro

import google.generativeai as genai

<<<<<<< Updated upstream
=======
from config import SYSTEM_PROMPT, CLAUDE_TOOLS, ORCHESTRATOR_PROMPT, PLAN_CRITIC_PROMPT, RESEARCHER_PROMPT, PARSER_PROMPT
from assistant import Assistant
>>>>>>> Stashed changes
from tools.screenshot import save_screenshot
from tools.browser import scrape_source
from tools.parser import parse_text
from utils import extract_xml

load_dotenv()
api_key=os.getenv("GOOGLE_GEMINI_API_KEY")

# This system prompt is taken from Claude computer use. I only added my computer's architecture (arm64).
# From Anthropic: This system prompt is optimized for the Docker environment in this repository and
# specific tool combinations enabled.
# We encourage modifying this system prompt to ensure the model has context for the
# environment it is running in, and to provide any additional information that may be
# helpful for the task at hand.
# SYSTEM_PROMPT = f"""<SYSTEM_CAPABILITY>
# * You are utilising an Ubuntu virtual machine using arm64 architecture with internet access.
# * You can feel free to install Ubuntu applications with your bash tool. Use curl instead of wget.
# * To open firefox, please just click on the firefox icon.  Note, firefox-esr is what is installed on your system.
# * Using bash tool you can start GUI applications, but you need to set export DISPLAY=:1 and use a subshell. For example "(DISPLAY=:1 xterm &)". GUI apps run with bash tool will appear within your desktop environment, but they may take some time to appear. Take a screenshot to confirm it did.
# * When using your bash tool with commands that are expected to output very large quantities of text, redirect into a tmp file and use str_replace_editor or `grep -n -B <lines before> -A <lines after> <query> <filename>` to confirm output.
# * When viewing a page it can be helpful to zoom out so that you can see everything on the page.  Either that, or make sure you scroll down to see everything before deciding something isn't available.
# * When using your computer function calls, they take a while to run and send back to you.  Where possible/feasible, try to chain multiple of these calls all into one function calls request.
# * The current date is {datetime.today().strftime('%A, %B %-d, %Y')}.
# </SYSTEM_CAPABILITY>

# <IMPORTANT>
# * When using Firefox, if a startup wizard appears, IGNORE IT.  Do not even click "skip this step".  Instead, click on the address bar where it says "Search or enter address", and enter the appropriate search term or URL there.
# * If the item you are looking at is a pdf, if after taking a single screenshot of the pdf it seems that you want to read the entire document instead of trying to continue to read the pdf from your screenshots + navigation, determine the URL, use curl to download the pdf, install and use pdftotext to convert it to a text file, and then read that text file directly with your StrReplaceEditTool.
# </IMPORTANT>"""
SYSTEM_PROMPT = f"""<SYSTEM_CAPABILITY>
You are a helpful personal computer assistant with access to the computer and internet. You also have access to tools for visiting a website, scraping the source, parsing web source, and taking a screenshot. You will be given a task to complete on the computer and via the internet. Take your time to think through the task, break it down into steps, identify the ones that require your tools, present the steps, and then execute the steps.
</SYSTEM_CAPABILITY>

<IMPORTANT>
- Always reponse with what you will be doing before calling any tools.
- After every turn, think out loud about the completed step, the given result, and the next step. Do not call a tool without thinking.
- Always continue until the task is completed. Generate new steps if required. 
- Be honest and have integrity. If you tried to visit or scrape a website but failed, tell the user you couldn't do it, whether you tried different approaches, and what your final solution is. For example, I tried to scrape (url) but I couldn't. Based on the title and url, I'm guessing it is about (an educated guess).
- Here's an example:

User: "Give me the URLs of the first 10 posts on Hacker News"
Model: Thinking... I need to scrape https://news.ycombinator.com and find the first 10 posts. This will require the scrape_source function with the argument, "https://news.ycombinator.com" and the parse_text function with the arguments, "temp/temp.html" and a suitable prompt. Here is the plan:
1. I will first return the scrape_source function.
2. I will wait for the results.
3. I will return the parse_text function. 
</IMPORTANT>
"""

async def loop():
  """
  The loop for the assistant.
  """
  genai.configure(api_key=api_key)

<<<<<<< Updated upstream
  tool_collection = [save_screenshot, scrape_source, parse_text]
  functions = {
    "scrape_source": scrape_source,
    "parse_text": parse_text,
    "save_screenshot": save_screenshot
  }

  def call_function(function_call):
    function_name = function_call.name
    function_args = function_call.args
    return functions[function_name](**function_args)
  
  def process_response(response):
    queue = [response]  # Use a queue to track responses
    while queue:
      current_response = queue.pop(0)
      for part in current_response.candidates[0].content.parts:
        if part.function_call:
          tool_result = call_function(part.function_call)
          print("🛠️  Tool result:", tool_result, "\n\n------------\n")
          tool_response = chat.send_message(tool_result)
          queue.append(tool_response)  # Add the new response to the queue
        else:
          if part.text.strip():
            print("\n🤵🏻 Aura: ", part.text)

  model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT,
    tools=tool_collection)
  
  chat = model.start_chat()

  print(f"{intro}🤵🏻 Aura: Hello! How can I help you today? (Type 'quit' to end the chat)\n")
=======
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
>>>>>>> Stashed changes

  while True:
    try:
      user_message = input("You: ")
      if user_message.lower() == "quit":
        print("Exiting chat.")
        break
<<<<<<< Updated upstream
      elif user_message.lower() == "debug":
        print("Chat History\n", chat.history)
        break
      
      response = chat.send_message(user_message)
      response.resolve()

      process_response(response)

      summary = chat.send_message(f"Summarize what the model did in first-person narrative. Do not use any tools: {chat.history}")
      print("\n🤵🏻 Aura: Here's a summary of what I did:\n\n", summary.text)
=======
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
>>>>>>> Stashed changes

    except Exception as e:
      import traceback
      print(f"An error occurred: {e}")
      print("Error type:", type(e).__name__)
      print("Traceback:", traceback.format_exc())

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
