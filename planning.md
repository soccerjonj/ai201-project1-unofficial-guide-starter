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

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

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

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
