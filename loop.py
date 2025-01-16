"""
A loop that calls the Gemini API and several tools.
"""

import os
from dotenv import load_dotenv 
from onboarding_message import intro

import google.generativeai as genai
import anthropic

from tools.screenshot import save_screenshot
from tools.browser import scrape_static_source, scrape_dynamic_source
from tools.parser import parse_text

import inquirer

load_dotenv()
gemini_api_key=os.getenv("GOOGLE_GEMINI_API_KEY")
anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")

# System prompt

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

# Main loop

async def loop():
  """
  The loop for the assistant.
  """
  tool_collection = [save_screenshot, scrape_static_source, scrape_dynamic_source, parse_text]

  # Anthropic declares tools differently

  functions = {
    "scrape_static_source": scrape_static_source,
    "scrape_dynamic_source": scrape_dynamic_source,
    "parse_text": parse_text,
    "save_screenshot": save_screenshot
  }

  genai.configure(api_key=gemini_api_key)
  gemini_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT,
    tools=tool_collection)

  claude_model = anthropic.Anthropic()

  messages = []

  # Helper functions

  def generate_text(model, messages):
    if model == "gemini":
      return gemini_model.generate_content(messages)
    elif model == "claude":
      return claude_model.messages.create(
        model="claude-3-haiku-20240307", 
        messages=messages,
        max_tokens=2048
      )

  def call_function(function_call):
      function_name = function_call.name
      function_args = function_call.args
      return functions[function_name](**function_args)
    
  def process_response(response):
    queue = [response]
    while queue:
      current_response = queue.pop(0)
      if selected_model == "gemini":
        messages.append({"role": "model", message_key: current_response.candidates[0].content.parts})
        for part in current_response.candidates[0].content.parts:
          if part.function_call:
            tool_result = call_function(part.function_call)
            print("🛠️  Tool result:", tool_result, "\n\n------------\n")
            messages.append({"role": "user", message_key: [{"text": f"Here is the result from the tool: {tool_result}"}]})
            tool_response = generate_text(selected_model, messages)
            queue.append(tool_response) 
          else:
            if part.text.strip():
              print(f"\n🤵🏻 Aura ({selected_model}): {part.text}")
      elif selected_model == "claude":
        if "error" in current_response:
           return f"An error occurred: {current_response['error']}"

        # if response.content[-1].type == "tool_use":
        #     tool_use = response.content[-1]
        #     func_name = tool_use.name
        #     func_params = tool_use.input
        #     tool_use_id = tool_use.id

        #     result = handle_tool_use(func_name, func_params)
        #     messages.append(
        #         {"role": "assistant", "content": response.content}
        #     )
        #     messages.append({
        #         "role": "user",
        #         "content": [{
        #             "type": "tool_result",
        #             "tool_use_id": tool_use_id,
        #             "content": f"{result}",
        #         }],
        #     })

        #     follow_up_response = self.generate_message(
        #         messages=messages,
        #         max_tokens=2048,
        #     )

        #     if "error" in follow_up_response:
        #         return f"An error occurred: {follow_up_response['error']}"

        #     response_text = follow_up_response.content[0].text
        #     messages.append(
        #         {"role": "assistant", "content": response_text}
        #     )
        #     return response_text
        
        if current_response.content[0].type == "text":
            response_text = current_response.content[0].text
            messages.append(
                {"role": "assistant", "content": response_text}
            )
            print(f"\n🤵🏻 Aura ({selected_model}): {response_text}")
        
        else:
            raise Exception("An error occurred: Unexpected response type")

  print(f"{intro}🤵🏻 Aura: Hello! To get started, select an AI model that will power me. (Type 'quit' to end the chat)\n")

  question = [
    inquirer.List(
      'choice',
      message="Choose an AI model",
      choices=['gemini', 'claude'],
    ),
  ]

  message_key = ""
  selected_model = inquirer.prompt(question)['choice']
  if selected_model == 'gemini':
    message_key = "parts"
    print("You chose gemini.")
  elif selected_model == 'claude':
    message_key = "content"
    print("You chose claude.")

  while True:
    try:
      user_message = input("You: ")
      if user_message.lower() == "quit":
        print("Exiting chat.")
        break
      elif user_message.lower() == "restart":
        messages = []
        continue
      elif user_message.lower() == "debug":
        print("Chat History\n", messages)
        continue
      
      messages.append({"role": "user", message_key: user_message})
      response = generate_text(selected_model, messages)
      process_response(response)

      # summary = generate_text(selected_model, f"Summarize what the model did in first-person narrative. Do not use any tools: {messages}")
      # print(f"\n🤵🏻 Aura ({selected_model}): Here's a summary of what I did:\n\n {summary.text}")

    except Exception as e:
      import traceback
      print(f"An error occurred: {e}")
      print("Error type:", type(e).__name__)
      print("Traceback:", traceback.format_exc())

# Run script

if __name__ == "__main__":
  import asyncio
  asyncio.run(loop())