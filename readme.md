# Assistant Aura

![Welcome to Aura](/img/onboarding.jpeg)

This started as [an attempt to reimplement Claude's computer use but with Gemini](https://alfredlua.substack.com/p/alfred-intelligence-3-building-an) but has evolved into a multi-agent assistant who can visit websites and summarize information.

Updates:

- 23/1/2025: I added a new agent, Retriever, which finds relevant information from a local database of past tasks and results (to learn about RAG).
- 20/1/2025: I split the assistant into four agents: Orchestrator, Plan Critic, Researcher, and Planner (to learn about creating multi-agent systems). 
- 17/1/2025: I added support for Claude 3 Haiku (to keep cost low). For updates from here and earlier, see the [`single-agent` branch](https://github.com/alfredlua/assistant-aura/tree/single-agent). 
- 14/1/2025: I created a basic terminal-based chat app that can visit websites (and websites within websites) and summarize them. It has several tools: visit a URL, scrape a URL with Beautiful Soup into a temp file, parse a file with an LLM, and take a screenshot. It uses Gemini 1.5 Flash (because it's free).

---

## What it can do (for now)

![Test example](/img/example.jpeg)

Upon receiving a task, it can visit websites (and websites within websites) and summarize them. 

For "summarize the top post on hn", it returned:

>This post details reverse engineering the Bambu Connect Electron app, highlighting its inherent insecurity due to relying on security through obscurity. The instructions involve extracting the app's main.js file, fixing an asar archive, and using Ghidra to locate and extract a private key. Finally, the post provides a Python script to further deobfuscate and extract certificates and the private key from the app. [https://wiki.rossmanngroup.com/wiki/Reverse_Engineering_Bambu_Connect](https://wiki.rossmanngroup.com/wiki/Reverse_Engineering_Bambu_Connect)

---

## How it works

This AI assistant consists of four agents:

1. **Orchestrator:** This agent comes up with the plan for the task, coordinates the work with the various agents, and updates the plan if necessary.
2. **Plan Critic:** This agent evaluates the plan by the Orchestrator and suggests improvements, up to three times.
3. **Retriever:** This agent retrieves relevant information from a local database, which stores past tasks and results.
4. **Researcher:** This agent has tools to scrape the source code of a website and save it to a file (temp/working_memory.txt).
5. **Parser:** This agent has a tool to extract information from temp/working_memory.txt using an LLM.

Here’s a rough flow of how the agents work together to complete a task:

![With RAG](/img/assistant-with-rag.jpeg)

1. The Orchestrator receives a task from the user, such as “summarize the first post on hn”, and comes up with a plan for his team.
2. The Plan Critic evaluates the plan and suggests improvements, up to three times. 
3. When the plan is good to go, the teammates work through each step sequentially. 
    1. The plan always starts with the Retriever. It searches for relevant information from a local database, which stores previous tasks and results.
    2. If no relevant task or result is found, the Researcher scrapes a given website and the Parser extracts specific information or summarizes the content of the website.
    3. After each step, the Orchestrator reviews the result from the respective teammate and updates the plan until the task is completed.
4. The Orchestrator informs the user of the answer.
5. The completed task and result are saved to the local database as text documents and embeddings.

---

## Issues

Well, it wouldn't be an app without issues. So, here goes:

- ~~It is lazy. If you ask it, "what's the first post on Hacker News?", it will only find the title of the post and guess what it is about. You have to specifically instruct it to visit the post. Oh, where's the AI that will replace me?~~ I updated the system prompt to make it less lazy.
- It cannot search on Google or use your computer (yet).
- It doesn't work well with dynamically-loaded sites. I have added a function for scraping with Selenium but sites such as Reddit block Selenium.
- It does fail sometimes. Like humans, once it fails, it will sometimes be too demotivated to try again. But like all computer systems, you can turn it off and on and try again.
