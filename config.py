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
- Always respond with what you will be doing before calling any tools.
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

CLAUDE_TOOLS = [
  {
    "name": "visit_website",
    "description": "Open a specific website with the default browser.",
    "input_schema": {
      "type": "object",
      "properties": {
        "url": {"type": "string", "description": "The website URL to visit."}
      },
      "required": ["url"]
    }
  },
  {
    "name": "scrape_static_source",
    "description": "Scrape the source of a given static website using Beautiful Soup.",
    "input_schema": {
      "type": "object",
      "properties": {
        "url": {"type": "string", "description": "The website URL to scrape."}
      },
      "required": ["url"]
    }
  },
  {
    "name": "scrape_dynamic_source",
    "description": "Scrape the source of a dynamically loaded website using Selenium.",
    "input_schema": {
      "type": "object",
      "properties": {
        "url": {"type": "string", "description": "The website URL to scrape."}
      },
      "required": ["url"]
    }
  },
  {
    "name": "parse_text",
    "description": "Given a file and instruction, use an LLM to extract the required information in a suitable format for post-processing.",
    "input_schema": {
      "type": "object",
      "properties": {
        "path": {"type": "string", "description": "The path to a file with the text to be parsed."},
        "instruction": {"type": "string", "description": "The prompt for an LLM to extract the required information from the html file."}
      },
      "required": ["path", "instruction"]
    }
  },
]