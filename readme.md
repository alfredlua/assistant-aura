# Assistant Aura

This is an attempt to reimplement Claude computer use but with Gemini.

Updates:

- 14/1/2025: I created a basic terminal-based chat app that can visit websites (and websites within websites) and summarize them. It has several tools: visit a URL, scrape a URL with Beautiful Soup into a temp file, prase a file with an LLM, and take a screenshot. 

---

## What it can do (for now)

For "Go to sciurls.com, find the first 3 articles, visit each of the links, and tell me what each is about", it returned:

>Here's a summary of the three articles:
>
>1. **OpenAI's o3 Chatbot and the Quest for AGI:** This article discusses OpenAI's new chatbot model, o3, which achieved a record-breaking score on the ARC-AGI test, a benchmark for assessing AI's reasoning and generalization abilities.  However, the article emphasizes the challenges in definitively measuring AGI and highlights the high computational cost and lack of a universally agreed-upon definition of AGI.
> 
>2. **A New Formation Mechanism for the Pluto-Charon Binary System:** This article summarizes a study proposing a novel "kiss and capture" mechanism for the formation of Pluto's moon, Charon, using simulations with solid proto-bodies instead of the previously assumed fluid ones.
>
>3. **Sang-Wook Han on Quantum Computing at KIST:** This article features an interview with Sang-Wook Han, discussing the potential of quantum computing and the challenges in its widespread industrial application.  It highlights the technology's potential across various fields while acknowledging the years needed before industrial-scale production becomes a reality.

For "Go to Hacker News, find the first 3 pieces of news, visit each of the links, and tell me what each is about", it returned:

> The first story is about malicious NPM packages targeting Cursor.com, published by a Snyk security researcher. The second story is about the release of OpenZFS 2.3.0, which includes features like RAIDZ expansion and improved deduplication performance.  The third is about Shavarsh Karapetyan, a Soviet-Armenian finswimming champion who rescued dozens of people from a trolleybus that plunged into Lake Yerevan.

---

Issues:
- It doesn't work well with dynamically-loaded sites, though there is a function for scraping with Selenum, which has to be tested further.
- It does not work on Reddit because Reddit seems to block scripts from scraping.