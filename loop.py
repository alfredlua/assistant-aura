"""
A loop that calls the Gemini API and several tools.
"""

import os
from dotenv import load_dotenv 
from onboarding_message import intro

import google.generativeai as genai
import anthropic

from config import SYSTEM_PROMPT, CLAUDE_TOOLS
from tools.screenshot import save_screenshot
from tools.browser import scrape_static_source, scrape_dynamic_source
from tools.parser import parse_text

import inquirer

load_dotenv()
gemini_api_key=os.getenv("GOOGLE_GEMINI_API_KEY")
anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")

# Main loop

async def loop():
  """
  The loop for the assistant.
  """

  genai.configure(api_key=gemini_api_key)
  gemini_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT,
    tools=[save_screenshot, scrape_static_source, scrape_dynamic_source, parse_text]
  )

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
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        tools=CLAUDE_TOOLS
      )
    
  functions = {
    "scrape_static_source": scrape_static_source,
    "scrape_dynamic_source": scrape_dynamic_source,
    "parse_text": parse_text,
    "save_screenshot": save_screenshot
  }

  def call_function(func_name, func_params):
      return functions[func_name](**func_params)
    
  def process_response(response):
    queue = [response]
    while queue:
      current_response = queue.pop(0)
      if selected_model == "gemini":
        messages.append({"role": "model", message_key: current_response.candidates[0].content.parts})
        for part in current_response.candidates[0].content.parts:
          if part.function_call:
            tool_use = part.function_call
            func_name = tool_use.name
            func_params = tool_use.args
            tool_result = call_function(func_name, func_params)
            print("🛠️  Tool result:", tool_result, "\n\n------------\n")
            messages.append({"role": "user", message_key: [{"text": tool_result}]})
            tool_response = generate_text(selected_model, messages)
            queue.append(tool_response) 
          else:
            if part.text.strip():
              print(f"\n🤵🏻 Aura ({selected_model}): {part.text}")
      elif selected_model == "claude":
        if "error" in current_response:
           return f"An error occurred: {current_response['error']}"

        if current_response.content[-1].type == "tool_use":
            tool_use = current_response.content[-1]
            func_name = tool_use.name
            func_params = tool_use.input
            tool_use_id = tool_use.id

            tool_result = call_function(func_name, func_params)
            print("🛠️  Tool result:", tool_result, "\n\n------------\n")

            messages.append(
                {"role": "assistant", "content": current_response.content}
            )
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": f"{tool_result}",
                }],
            })

            follow_up_response = generate_text(
                model=selected_model,
                messages=messages,
            )
            queue.append(follow_up_response) 
        
        elif current_response.content[0].type == "text":
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

      # Create report of what the assistant did
      messages.append({"role": "user", message_key: f"Summarize what the model did in first-person narrative. Do not use any tools: {messages}"})
      summary = generate_text(selected_model, messages)
      print(f"\n🤵🏻 Aura ({selected_model}): Here's a summary of what I did:\n\n {summary.text if selected_model == "gemini" else summary.content[0].text}")

    except Exception as e:
      import traceback
      print(f"An error occurred: {e}")
      print("Error type:", type(e).__name__)
      print("Traceback:", traceback.format_exc())

# Run script

if __name__ == "__main__":
  import asyncio
  asyncio.run(loop())