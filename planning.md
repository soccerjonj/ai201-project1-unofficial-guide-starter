# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- Off Campus Housing Experiences, Neighborhood Suggestions, Building Reviews. There is not much about this through official University Channels and finding the info is hard because it is scattered. -->

This guide covers off-campus housing experiences for DePaul University students: neighborhood suggestions, specific building and landlord reviews, lease and move-in cost warnings, and commute realities for both the Lincoln Park and Loop campuses. This knowledge is hard to find through official channels because DePaul houses only a fraction of its students, so most rent on the private market — and the honest information lives scattered across Reddit threads, Yelp and Google reviews, and student Facebook groups rather than in any single university resource. The Unofficial Guide gathers these fragmented, first-hand student accounts into one place you can search and ask questions of.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Reddit | DePaul subreddit | https://www.reddit.com/r/depaul/ |
| 2 | Reddit | ChicagoApartments subreddit | https://www.reddit.com/r/chicagoapartments/ |
| 3 | Reddit | Chicago subreddit neighborhood and housing threads | https://www.reddit.com/r/chicago/ |
| 4 | Yelp | Reviews for apartment buildings near DePaul (Lincoln Park, Loop) | https://www.yelp.com/ |
| 5 | Google Reviews | Property management companies (search "apartments near DePaul University") | maps.google.com |
| 6 | Apartments.com | Apartment reviews section on individual listings | https://www.apartments.com/ |
| 7 | ApartmentRatings.com | Tenant reviews indexed by building address | https://www.apartmentratings.com/ |
| 8 | Niche.com | Neighborhood reviews with student demographic filters | https://www.niche.com/ |
| 9 | Zillow / HotPads | Rent price reality + building review sections | https://www.zillow.com/ |
| 10 | Quora / student blogs | Unofficial student-written housing advice and Q&A threads | various |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**
I will split my documents recursively into chunks based on each individual review or comments unless it is a long review or comment that is over the word/token cap I'm setting which will then be chunked into 150 words (about 195 tokens).
**Overlap:**
There will be no overlap for individual comments or reviews but for long texts that need chunking, there will be overlap of 25 words.
**Reasoning:**
These numbers fit the structure of my documents since a lot of the text that will be captured will be shorter than 150 words and they will all be separate discrete writings.

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
I'm using the all-MiniLM-L6-v2 via sentence-transformers embedding model
**Top-k:**
k = 7, that way it can surface multiple different reviews for buildings and neighborhoods but won't completely bog down the reviews for a specific building if there are less than 7.
**Production tradeoff reflection:**
I'd consider a more accurate model that could handle multiple languages so it could handle reviews in other languages and also because the reviews and comments will contain slang and neighborhood/building nicknames that the current model may miss or misunderstand. Context length doesn't really matter for this specific purpose since 95% or more will be shorter than the current chunk size I'm using on the local model. The biggest tradeoff would be the cost since it is currently free running it locally as well as latency since it would not be local.
---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What neighborhoods do DePaul students recommend for balancing a short commute with affordable rent? | Lincoln Park, Lakeview, Wrigleyville expected |
| 2 | What do students say about finding roommates to live with and finding apartments that are 3bed+? | Ask friends, friends of friends, look on facebook groups, reddit etc. |
| 3 | What do students with classes only at the Loop campus say about where to live and their commute? | Live in south loop, printers row, the loop, river north, streeterville, west loop expected |
| 4 | What do students say about whether living in Lincoln Park is worth it as compared to other neighborhoods? | If you have the money to pay for rent it is worth it for the walkability to campus |
| 5 | What lease or move in costs do students warn about when trying to find off campus housing? | Move in fees, admin fees, especially non refundable fees, security deposits, utilites included/not included, broker fees. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. If there are only 2-3 relevant chunks to a question, the extra 4-5 chunks will add noise to the LLM's response. In the prompt I will instruct the model to ignore chunks that don't address the question to attempt to mitigate this.

2. Making sure that specific reviews or comments are actually about the specific building or neighborhood, especially if the neighborhood or building name are not actually in the chunk. To solve this I will store metadata about the building and neighborhood to prevent this. 

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```
┌──────────────────────────────────────────────────────────────────┐
│ 1. DOCUMENT INGESTION                                            │
│    Load raw docs from documents/, strip nav/ads/boilerplate,     │
│    attach source + building/neighborhood metadata                │
│    Tool: Python (+ pdfplumber only if any docs are PDFs)         │
└───────────────────────────────┬──────────────────────────────────┘
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│ 2. CHUNKING                                                      │
│    Split into review-unit chunks (~150 words / ~195 tokens cap), │
│    25-word overlap only on long docs that exceed the cap         │
│    Tool: custom Python function (chunk_text)                     │
└───────────────────────────────┬──────────────────────────────────┘
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│ 3. EMBED + STORE                                                 │
│    Turn each chunk into a vector; store vector + text + metadata │
│    Tool: all-MiniLM-L6-v2 (sentence-transformers)  →  ChromaDB   │
└───────────────────────────────┬──────────────────────────────────┘
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│ 4. RETRIEVAL                                                     │
│    Embed the user query, return top-7 nearest chunks + metadata  │
│    Tool: sentence-transformers (query)  →  ChromaDB (similarity) │
└───────────────────────────────┬──────────────────────────────────┘
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│ 5. GENERATION                                                    │
│    LLM answers using ONLY retrieved chunks; cites source metadata│
│    Tool: Groq API (Llama model)                                  │
└──────────────────────────────────────────────────────────────────┘

         ▲ user question enters at stage 4; grounded, cited answer exits stage 5
```

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
I plan to use Claude. I will give Claude the Chunking Strategy: Chunk Size, Overlap, and Reasoning. I expect it to load the files in documents/ and clean them. Then create a custom python function for ingestion and chunking (chunk_text). To verify the output I will run it on a specific page and print the chunks to confirm none exceed the word limit and that all reviews and comments are their own distinct chunk.
**Milestone 4 — Embedding and retrieval:**
I plan to use Claude. I will give Claude the Retrieval Approach: Embedding Model, Top-K. I expect it to produce code to embed chunks with all-MiniLM-L6-v2, store them in ChromaDB with metadata, and create a retrieve(query) returning top-7 chunks + metadata. To verify I will run my eval questions and confirm that it returns 7 relevant chunks along with their metadata attached.
**Milestone 5 — Generation and interface:**
I plan to use Claude. I will give Claude the grounded response generation requirement and the Anticipated Challenges section where my instructions about avoiding these challenges live as well as the query interface requirement. I expect it to produce a Groq prompt and API call that answers using only retrieved chunks while citing it's sources along with a simple Gradio web interface. To verify I can ask a question that is out of scope and irrelevant to the dataset and confirm the model says it doesn't know or it isn't covered rather than making something up.