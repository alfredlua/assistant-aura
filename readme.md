# Assistant Aura

![Welcome to Aura](/img/onboarding.jpeg)

This is an attempt to reimplement Claude computer use but with Gemini.

Updates:

- 20/1/2025: I split the assistant into four agents: Orchestrator, Plan Critic, Researcher, and Planner (to learn about creating multi-agent systems). 
- 17/1/2025: I added support for Claude 3 Haiku (to keep cost low). See the [`single-agent` branch](https://github.com/alfredlua/assistant-aura/tree/single-agent). 
- 14/1/2025: I created a basic terminal-based chat app that can visit websites (and websites within websites) and summarize them. It has several tools: visit a URL, scrape a URL with Beautiful Soup into a temp file, parse a file with an LLM, and take a screenshot. It uses Gemini 1.5 Flash (because it's free).

---

## How it works

![Multi-agent chart](/img/multi-agent-chart.jpeg)

## What it can do (for now)

![Test example](/img/example.jpeg)

Upon receiving a detailed instruction, it can visit websites (and websites within websites) and summarize them. After it completes the task, it will also give you a report on what it did. 

Here are some examples:

For "Go to sciurls.com, find the first 3 articles, visit each of the links, and tell me what each is about", it returned:

>Here's a summary of the three articles:
>
>1. **OpenAI's o3 Chatbot and the Quest for AGI:** This article discusses OpenAI's new chatbot model, o3, which achieved a record-breaking score on the ARC-AGI test, a benchmark for assessing AI's reasoning and generalization abilities.  However, the article emphasizes the challenges in definitively measuring AGI and highlights the high computational cost and lack of a universally agreed-upon definition of AGI.
> 
>2. **A New Formation Mechanism for the Pluto-Charon Binary System:** This article summarizes a study proposing a novel "kiss and capture" mechanism for the formation of Pluto's moon, Charon, using simulations with solid proto-bodies instead of the previously assumed fluid ones.
>
>3. **Sang-Wook Han on Quantum Computing at KIST:** This article features an interview with Sang-Wook Han, discussing the potential of quantum computing and the challenges in its widespread industrial application.  It highlights the technology's potential across various fields while acknowledging the years needed before industrial-scale production becomes a reality.

For "Go to Hacker News, find the first 3 posts, visit each of the links, and tell me what each is about", it returned:

> The first story is about malicious NPM packages targeting Cursor.com, published by a Snyk security researcher. The second story is about the release of OpenZFS 2.3.0, which includes features like RAIDZ expansion and improved deduplication performance.  The third is about Shavarsh Karapetyan, a Soviet-Armenian finswimming champion who rescued dozens of people from a trolleybus that plunged into Lake Yerevan.

---

## Issues

Well, it wouldn't be an app without issues. So, here goes:

- It is lazy. If you ask it, "what's the first post on Hacker News?", it will only find the title of the post and guess what it is about. You have to specifically instruct it to visit the post. Oh, where's the AI that will replace me?
- It doesn't work well with dynamically-loaded sites. I have added a function for scraping with Selenium but sites such as Reddit blocks Selenium.
- It does fail sometimes. Like humans, once it failed, it will sometimes be too demotivated to try again. But like all computer systems, you can turn it off and on and try again.