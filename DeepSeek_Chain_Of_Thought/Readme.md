# Chain of Thought for Claude 


> Claude's got the flow, it's a chain of thought,

> Connecting ideas like a mastermind plot,

> Logic so sharp, can’t be sold or bought

> This been written by some random bot

## What the hell dis is?

Dis my friend is an experiment.

* Reasoning is a new trend in LLM development (exposing the throught trace)
* Prevents hallucinations, assures the user, makes things transparent
* Hallucinations are an issue for reliability, but you can see when things go wrong now

Getting reasoning traces can be expensive, or not.
Here is how to get it for free.

### DeepSeek exports Chain of Thought

* DeepSeek is the new kid on the block.
* It tackles the hallucination problem by exporting is "chain of thought".


### DeepSeek

* via OpenRouter
* via LM Studio (self-hosted)

Self-hosting has the advantage of 

1. being free
2. being accessible
3. being private

DeepSeek is hosted in the People's Republic of China. But it's Free Open Source.

1. DeepSeek uses user data for its training
2. The Chinese government can access the data
3. Today (26.01.2025) a hand full of people know how it works

### Claude

* via Anthropic (United States of America)
* via OpenRouter (intermediate)

Using this as an upstream cloud model has the advantage of:

1. being affordable
2. access to a large knowledge corpus
3. 3. Today (26.01.2025) many people use it

### o1

* via OpenAI (limited avaibility today (26.01.2025))
* the most powerful model out there

Hard problems are being solved with o1.

But o1 is expensive and it does not export the chain of thought.

### Gemini

* via Google Cloud
* much larger context window than DeepSeek
* better for complex tasks which involve RAG

You need to use the right SDK.

## Install

requirements.txt