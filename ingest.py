"""
Milestone 3 — Document ingestion + chunking pipeline.

Stages (matches planning.md Architecture):
  1. load_documents()  - read every file listed in documents/manifest.csv + its metadata
  2. clean_text()      - strip nav/ads/boilerplate, decode HTML entities,
                         leave each review/comment as its own paragraph
  3. chunk_text()      - one chunk per review/comment; split only the long ones
                         (> CHUNK_MAX_WORDS) with CHUNK_OVERLAP_WORDS overlap

Run:  python ingest.py
Produces: chunks.json  (list of {id, text, metadata}) for Milestone 4.
"""

import csv
import html
import json
import re
from pathlib import Path

DOCS_DIR = Path("documents")
MANIFEST = DOCS_DIR / "manifest.csv"
OUTPUT = Path("chunks.json")

# --- Chunking parameters (from planning.md > Chunking Strategy) ---
CHUNK_MAX_WORDS = 150       # ~195 tokens, stays under all-MiniLM-L6-v2's ~256 limit
CHUNK_OVERLAP_WORDS = 25    # only applied when a single review exceeds the cap
MIN_CHUNK_WORDS = 5         # drop sub-5-word fragments (orphan usernames, stray UI)


# ----------------------------------------------------------------------
# Stage 2 helpers: cleaning
# ----------------------------------------------------------------------

# Lines that exactly match one of these (after stripping) are boilerplate.
BOILERPLATE_EXACT = {
    # Reddit chrome
    "skip to main content", "share", "save", "hide", "report",
    "reply share report save", "continue this thread", "read more",
    "view all comments", "back to top", "about community", "[removed]",
    "[deleted]", "sort by: best",
    # Reddit comment UI (real copy-paste artifacts)
    "upvote", "downvote", "reply", "award", "give award", "follow",
    "best", "top", "new", "q&a", "controversial", "old", "promoted",
    "op", "•", "sort by:", "search comments", "expand comment search",
    "comments section", "add a comment", "join", "joined", "mod",
    "more replies", "single comment thread", "view discussions in other "
    "communities", "sign up", "vote", "go to comments",
    "comment deleted by user", "join the conversation", "join the discussion",
    "view all comments", "add comment",
    # ApartmentRatings listing-card junk
    "total monthly price", "contact property", "pet friendly", "luxury",
    "furnished", "(", ")", "check availability",
    # Reddit site chrome / footer / video-player UI
    "view all moderators", "moderators", "reddit rules", "privacy policy",
    "user agreement", "your privacy choices", "accessibility", "help",
    "blog", "careers", "press", "collapse video player", "learn more",
    "get started", "shop now", "apply now", "install", "content policy",
    # Yelp chrome
    "yelp", "find a table", "write a review", "add photo",
    "recommended reviews", "search reviews", "sort by yelp sort",
    "start your review of eastgate apartments", "other apartments nearby",
    "advertisement", "apartments",
    "your trust is our top concern, so businesses can't pay to alter or "
    "remove their reviews.",
}

# Lines matching one of these regexes are boilerplate.
BOILERPLATE_PATTERNS = [
    re.compile(r"^r/\w+$", re.I),                       # r/depaul
    re.compile(r"^search within r/", re.I),
    re.compile(r"^posted by u/", re.I),
    re.compile(r"^u/.+ago$", re.I),                     # u/name · 7 months ago
    re.compile(r"^level \d+$", re.I),                    # level 1 / level 2
    re.compile(r"^\d[\d,.]*[km]? (points?|comments?|reviews?|members?)$", re.I),
    re.compile(r"^(useful|funny|cool)( \d+)?$", re.I),
    re.compile(r"^\d(\.\d)? star rating$", re.I),
    re.compile(r"^\d{1,2}/\d{1,2}/\d{4}$"),             # 3/14/2024
    re.compile(r"^[A-Z][a-z]+ [A-Z]\.$"),              # Megan T.  (reviewer name)
    re.compile(r"^[A-Z][a-zA-Z .]+, [A-Z]{2}$"),       # Chicago, IL  (reviewer city)
    re.compile(r"^page \d+ of \d+$", re.I),
    re.compile(r"^created .+\d{4}$", re.I),
    re.compile(r"^copyright", re.I),
    re.compile(r"^was this review", re.I),
    re.compile(r"^\d+ N .+ Ave", re.I),                 # street address
    # Reddit comment UI (real copy-paste artifacts)
    re.compile(r"^-?\d[\d,]*$"),                        # lone vote count: 23, 111, -4
    re.compile(r"^(upvote|downvote)( \d+)?$", re.I),
    re.compile(r"^\d[\d,]* go to comments$", re.I),
    re.compile(r"^\d+ more repl(y|ies)$", re.I),        # 1 more reply
    re.compile(r"^comment (deleted|removed) by", re.I),
    re.compile(r"^u/\S+$", re.I),                       # bare u/Name line
    re.compile(r"^u/\S+ avatar$", re.I),               # u/Name avatar
    re.compile(r"^\d+\s*(mo|yr|y|d|h|m|w|sec|min)\s*ago$", re.I),  # 2mo ago, 5h ago
    re.compile(r"^\d+ (second|minute|hour|day|week|month|year)s? ago$", re.I),
    re.compile(r"^thumbnail image:", re.I),
    re.compile(r"^\S+\.(com|org|net|io|edu|gov)$", re.I),  # bare domain (ad link)
    re.compile(r"•\s*promoted$", re.I),
    # ApartmentRatings listing cards
    re.compile(r"^[A-F][+-]?$"),                        # epIQ grade: B+, A
    re.compile(r"^\d\.\d$"),                            # rating: 4.7
    re.compile(r"^[()]$"),                              # lone paren
    re.compile(r"^\d+ reviews?( & surveys)?$", re.I),
    re.compile(r"^[\d,\s\-]+ (beds?|baths?)$", re.I),  # 0 - 3 Beds
    re.compile(r"^[\d,\s\-]+ sq ft$", re.I),
    re.compile(r"^\$[\d,]+$"),                          # $946
    re.compile(r"^city rank #?\d+$", re.I),
    re.compile(r"- chicago, il$", re.I),               # "Triangle Square - Chicago, IL"
    re.compile(r", il \d{5}$", re.I),                  # address line ", IL 60614"
    re.compile(r"^\d+ apartments near me", re.I),
    re.compile(r"^price range:", re.I),
    re.compile(r"reviews are available from registered residents", re.I),
    re.compile(r"^the epiq rating", re.I),
    # Reddit site chrome / footer / video player
    re.compile(r"^reddit, inc\.", re.I),
    re.compile(r"all rights reserved", re.I),
    re.compile(r"©"),
    re.compile(r"^\d+:\d+ / \d+:\d+$"),                # 0:00 / 0:00
    re.compile(r"^clickable image", re.I),
]

# Reddit promoted-ad call-to-action lines that mark the END of an ad block.
PROMO_END = {"learn more", "sign up", "get started", "shop now", "install",
             "apply now", "download", "reply", "award", "upvote", "downvote"}

# Phrases scrubbed even when they trail a real content line.
INLINE_JUNK = re.compile(r"\s*(read more|continue this thread)\s*$", re.I)

# ApartmentRatings wraps each truncated review snippet like:
#   pure white svg"The maintenance team is fantastic..."... [more]
# Strip the wrapper, keep the review text.
LISTING_PREFIX = re.compile(r'^pure white svg\s*"?', re.I)
LISTING_SUFFIX = re.compile(r'"?\s*\.\.\.\s*\[more\]\s*$', re.I)


def is_boilerplate(line: str) -> bool:
    low = line.lower()
    if low in BOILERPLATE_EXACT:
        return True
    return any(p.search(line) for p in BOILERPLATE_PATTERNS)


def clean_text(raw: str, metadata: dict | None = None) -> str:
    """
    Remove boilerplate and decode HTML entities.

    Returns a string where each surviving review/comment is one paragraph,
    separated from the next by a blank line.

    Boundary rule: a *boilerplate* line ends the current unit, but a blank
    line does NOT. Real reviews/comments span multiple paragraphs separated
    by blank lines, while separate comments are always divided by boilerplate
    (the "Upvote / Reply / Award" cluster on Reddit, "Useful/Funny/Cool" on
    Yelp). Flushing on boilerplate — not blank lines — keeps each comment
    whole instead of shattering it on every paragraph break.

    If `metadata` is given, standalone header lines that exactly match the
    document's building or neighborhood are dropped (page labels, not content).
    Reddit usernames are learned from "u/Name avatar" lines and the orphan
    username line that follows is dropped too.
    """
    labels = set()
    if metadata:
        for key in ("building", "neighborhood"):
            value = (metadata.get(key) or "").strip().lower()
            if value:
                labels.add(value)

    usernames = set()
    blocks, current = [], []
    in_promo = False

    def flush():
        if current:
            blocks.append(" ".join(current))
            current.clear()

    for line in raw.splitlines():
        line = html.unescape(line).strip()       # &#39; -> ' , &mdash; -> —
        low = line.lower()

        # Promoted ad: skip everything from the "Promoted" marker to its
        # call-to-action (Learn More / Sign Up / a bare domain), since the
        # ad body text is arbitrary and can't be pattern-matched.
        if low == "promoted" or re.search(r"•\s*promoted$", low):
            in_promo = True
            flush()
            continue
        if in_promo:
            if low in PROMO_END or re.match(r"^\S+\.(com|org|net|io|edu|gov)$", low):
                in_promo = False
            continue

        # "u/Name avatar" -> remember "name" so its orphan username line is dropped.
        m = re.match(r"^u/(\S+)\s+avatar$", line, re.I)
        if m:
            usernames.add(m.group(1).lower())
            flush()
            continue

        if is_boilerplate(line) or low in labels or low in usernames:
            flush()
            continue
        if not line:
            continue                              # blank line: skip, do NOT flush
        line = INLINE_JUNK.sub("", line)
        line = LISTING_PREFIX.sub("", line)       # strip ApartmentRatings wrapper
        line = LISTING_SUFFIX.sub("", line)
        line = line.strip()
        if line:
            current.append(line)
    flush()
    return "\n\n".join(blocks)


# ----------------------------------------------------------------------
# Stage 3: chunking
# ----------------------------------------------------------------------

def chunk_text(cleaned: str,
               max_words: int = CHUNK_MAX_WORDS,
               overlap: int = CHUNK_OVERLAP_WORDS) -> list[str]:
    """
    One chunk per review/comment (paragraph). A review longer than `max_words`
    is split into `max_words`-word windows that overlap by `overlap` words.
    No overlap is carried across separate reviews.
    """
    chunks = []
    for para in cleaned.split("\n\n"):
        words = para.split()
        if not words:
            continue
        if len(words) <= max_words:
            chunks.append(para)
            continue
        start = 0
        while start < len(words):
            chunks.append(" ".join(words[start:start + max_words]))
            if start + max_words >= len(words):
                break
            start += max_words - overlap
    return chunks


# ----------------------------------------------------------------------
# Stage 1: loading
# ----------------------------------------------------------------------

def load_documents() -> list[dict]:
    """Read every file in the manifest, returning raw text + its metadata."""
    docs = []
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            path = DOCS_DIR / row["filename"]
            if not path.exists():
                print(f"  ! listed in manifest but missing on disk: {path}")
                continue
            docs.append({
                "raw": path.read_text(encoding="utf-8"),
                "metadata": {
                    "filename": row["filename"],
                    "source": row["source"],
                    "neighborhood": row["neighborhood"],
                    "building": row["building"],
                    "url": row["url"],
                },
            })
    return docs


# ----------------------------------------------------------------------
# Orchestration + inspection
# ----------------------------------------------------------------------

def build_chunks(docs: list[dict]) -> list[dict]:
    all_chunks = []
    for doc in docs:
        cleaned = clean_text(doc["raw"], doc["metadata"])
        kept = [t for t in chunk_text(cleaned)
                if len(t.split()) >= MIN_CHUNK_WORDS]   # drop tiny fragments
        for i, text in enumerate(kept):
            meta = dict(doc["metadata"])
            meta["chunk_index"] = i
            all_chunks.append({
                "id": f"{doc['metadata']['filename']}::{i}",
                "text": text,
                "metadata": meta,
            })
    return all_chunks


if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} documents from {MANIFEST}\n")

    # Inspect cleaning: print the first cleaned document in full.
    print("=" * 70)
    print("CLEANED DOCUMENT (first):", docs[0]["metadata"]["filename"])
    print("=" * 70)
    print(clean_text(docs[0]["raw"], docs[0]["metadata"]))

    chunks = build_chunks(docs)

    # Inspect chunking: print 5 representative chunks with word counts.
    print("\n" + "=" * 70)
    print("5 REPRESENTATIVE CHUNKS")
    print("=" * 70)
    for c in chunks[:5]:
        wc = len(c["text"].split())
        print(f"\n[{c['id']}]  ({wc} words)  source={c['metadata']['source']}"
              f" building={c['metadata']['building'] or '-'}")
        print(c["text"])

    # Count + size sanity check.
    counts = [len(c["text"].split()) for c in chunks]
    print("\n" + "=" * 70)
    print(f"TOTAL CHUNKS: {len(chunks)}")
    print(f"word count  min={min(counts)}  max={max(counts)}  "
          f"avg={sum(counts) / len(counts):.0f}")
    print("=" * 70)

    OUTPUT.write_text(json.dumps(chunks, indent=2, ensure_ascii=False),
                      encoding="utf-8")
    print(f"\nWrote {len(chunks)} chunks -> {OUTPUT}")
