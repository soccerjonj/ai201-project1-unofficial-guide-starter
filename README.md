# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

Off-campus housing experiences for DePaul University students: neighborhood suggestions, management company reviews, lease and move-in cost warnings, and commute realities for both the Lincoln Park and Loop campuses. This knowledge is hard to find through official channels because DePaul houses only a fraction of its students, so most rent on the private market — and the honest information lives scattered across Reddit threads, Yelp and Google reviews, and student Facebook groups rather than in any single university resource. 

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Reddit (r/depaul, r/AskChicago, r/chicagoapartments) | Lincoln Park off-campus housing threads | documents/reddit_lp-housing.txt |
| 2 | Reddit (r/depaul, r/AskChicago, r/chicagoapartments) | Living near the Loop campus and the commute | documents/reddit_loop-living.txt |
| 3 | Reddit (r/depaul, r/AskChicago, r/chicagoapartments) | Finding roommates / 3-bed apartments | documents/reddit_roommates.txt |
| 4 | Reddit (r/depaul, r/AskChicago, r/chicagoapartments) | DePaul student neighborhood and cost discussion | documents/reddit_student-neighborhoods.txt |
| 5 | Reddit (r/AskChicago, r/chicagoapartments) | Move-in fee and lease cost warnings | documents/reddit_fees-warnings.txt |
| 6 | Reddit (r/AskChicago, r/chicagoapartments) | Affordable / walkable neighborhood discussion | documents/reddit_chicago-neighborhoods.txt |
| 7 | Reddit (r/chicagoapartments) | Property management company experiences | documents/reddit_management-co.txt |
| 8 | ApartmentRatings | Tenant reviews for buildings in 60614 | https://www.apartmentratings.com/il/60614/ |
| 9 | Apartments.com | Lincoln Park neighborhood guide | https://www.apartments.com/local-guide/lincoln-park-chicago-il/ |
| 10 | Niche | Lincoln Park neighborhood reviews + stats | https://www.niche.com/places-to-live/n/lincoln-park-chicago-il/ |
| 11 | DePaul Honors Blog | Student guide to LP, Wrigleyville, Logan Square | https://dpuhonors.com/2025/09/25/chicago-neighborhoods/ |
---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**
I split my documents recursively into chunks based on each individual review or comment unless it was a long review or comment that is over the word/token cap I set which was then chunked into 150 words (about 195 tokens).
**Overlap:**
There is no overlap for individual comments or reviews but for long texts that need chunking, there is overlap of 25 words.
**Why these choices fit your documents:**
These numbers fit the structure of my documents since a lot of the text that was captured was shorter than 150 words and are all separate discrete writings.
**Final chunk count:**
830 chunks
---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**
I used the all-MiniLM-L6-v2 via sentence-transformers embedding model because it is free and local.
**Production tradeoff reflection:**
I'd consider a more accurate model that could handle multiple languages so it could handle reviews in other languages and also because the reviews and comments will contain slang and neighborhood/building nicknames that the current model may miss or misunderstand. Context length doesn't really matter for this specific purpose since 95% or more will be shorter than the current chunk size I'm using on the local model. The biggest tradeoff would be the cost since it is currently free running it locally as well as latency since it would not be local.
---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**
System prompt rules were given such as: "Rule 1 — "Use ONLY information stated in the context passages. Never add facts from your own knowledge or general world knowledge." This tells the model that retrieved chunks are the only allowed source. Rule 2 — "If the passages do not contain enough information to answer the question, reply with exactly: 'The documents I have don't cover this.' Do not guess or fill gaps." This makes grounding verifiable because when asked questions it doesn't have information on, it should respond with "The documents I have don't cover this." The context is also formatted and labeled before the model sees it so that each retrieved chunk is numbered with a source. That being said grounding is still prompt enforced and not technically guaranteed.
**How source attribution is surfaced in the response:**
Source attribution is surfaced in the response because of the built in metadata code, therefore using the rules created create inline citations that are numbered based on a source list at the bottom.
---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What neighborhoods do DePaul students recommend for balancing a short commute with affordable rent? | It reccomends Wirkcer Park, Lincoln Park, Lakeview Eastm and Roscoe Village and notes Lincoln Park as expensive, Wicker Park a bit far, and also anywhere off the Red or Brown line as ideal including Lakeview and Ravenswood. | Relevant | Accurate |
| 2 | What do students say about finding roommates to live with and finding apartments that are 3bed+? | Ask friends, friends of friends, look on facebook groups, reddit etc. | It's easer to find apartments the more roommates you have and the further away from the loop you are. To find them look on off-campus housing facebook group as well as spareroom and roomies. Also, some apartments like Ion, can place you in any apartment with an open room. | Relevant | Accurate |
| 3 | What do students with classes only at the Loop campus say about where to live and their commute? | Live in south loop, printers row, the loop, river north, streeterville, west loop expected | Suggest living in the South Loop for decent price wise, a student mentions living closer to the loop is prefereable and being in the loop is convenient, specific info about students with classes only at the Loop is limited as most students seem to have classes in both campuses. | Relevant | Accurate |
| 4 | What do students say about whether living in Lincoln Park is worth it as compared to other neighborhoods? | If you have the money to pay for rent it is worth it for the walkability to campus | Students mention Lincoln Park is one of most expensive neighborhoods in the city but some still find it worth it as it has great food, a lively atmosphere, they feel safe walking around at night. Students can consider living in nearby neieghborhoods like Lakeview which is similar to Lincoln Park or areas 10-15 minutes from Lincoln Park where they pay $650-1200 for a studio or shared 2 bed. Others mention prefering Lincoln Park over River North and Gold Coast because those feel too corporate. | Relevant | Accurate |
| 5 | What lease or move in costs do students warn about when trying to find off campus housing? | Move in fees, admin fees, especially non refundable fees, security deposits, utilites included/not included, broker fees. | Students warn about high rent costs but there is no specific mention of lease or move-in costs, only monthly rent payments. | Partially Relevant | Partially Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**
What lease or move in costs do students warn about when trying to find off campus housing?
**What the system returned:**
Students warn about high rent costs [6] and advise to be cautious of places with high rents, considering them a red flag [6]. One student mentions that their daughter's rent is split among roommates, with utilities included, and she will be paying ~$1,000 [5]. Another student's sons pay $2,200/month for a 3+2 duplex [1]. However, there is no specific mention of lease or move-in costs, only monthly rent payments. [1, 5, 6]
**Root cause (tied to a specific pipeline stage):**
The root cause is the retrieval stage being heavily influenced by the keywords, dominating the query vector, in the search like "students" and "off campus housing" which bury most of the information I have about apartment and lease costs and fees. The chunks about those were not pulled from student threads and contain the word "apartment" instead of "off campus housing" as well as "fee" and other terms not in the query, therefore they don't rank in the top-k.
**What you would change to fix it:**
Instead of just doing a semantic search, I would do a hybrid approach of semantic and keyword search so that more sources in the vector with the terms "lease" "move in costs" surface more, as well as a slightly more tuned query to include words like "fees" "move in fees" "lease fees".
---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
One way the spec helped me during my implementation was to be able to go back and reflect on my thinking and choices I made when planning this project after doing hours of work and possibly forgetting some of the choices and ideas I had. For example, the chunking strategy documentation made it very simple to look back on my thinking and understand my choices, making it easier to prompt Claude and hand them a directed prompt to generate chunk_text(). 
**One way your implementation diverged from the spec, and why:**
At first I was planning on pulling reviews for specific buildings but I quickly realized when gathering sources that this wouldn't really help any students trying to get information and if anything might just be advertising one or two specific apartment complexes over and over to users of the app. Since I realized I would not be using these specific sources I then spent more time trying to find other sources and ended up just pulling more and more reddit threads since that seemed to be the highest quality source of recent information on both student housing as well as neighborhoods and fees.
---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
I gave Claude my Chunking Strategy section from planning.md and asked it to generate the function chunk_text(). 
- *What it produced:*
Claude returned ingest.py with a loader, a cleaner, and the function chunk_text() matching the given spec.
- *What I changed or overrode:*
When copy-pasting from reddit pages, there were tons of tiny chunks produced containing irrelevant information like "upvotes" "downvotes" "usernames" and even ads. I iterated on the cleaning rules with Claude to remove these issues and implemented a 5 word minimum for chunks. I also rejected a comment stripping feature that I did not want.

**Instance 2**

- *What I gave the AI:*
I gave Claude the working app.py and the observation I made that I incorrectly assigned a single thread source to a page containing multiple reddit threads related to the same topic. I asked it to correct the source attribution to the specific subreddits used for each document so I was not ever giving incorrect source information.
- *What it produced:*
Claude redid the source attribution making it only subreddit specific of the given subreddits for each document.
- *What I changed or overrode:*
I chose the subreddit-level fix over the alternative of splitting every file into separate per-thread documents, accepting slightly less precise citations rather than re-collecting everything. I also directed it to re-run ingestion and rebuild the ChromaDB index so the corrected metadata took effect, not just the manifest.