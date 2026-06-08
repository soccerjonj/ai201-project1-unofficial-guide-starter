"""
Milestone 5 — Grounded generation + query interface.

Pipeline (matches planning.md Architecture, stage 5):
  retrieve()        -> top-k chunks for the question (from retrieve.py)
  generate_answer() -> ask Groq to answer using ONLY those chunks
  build_sources()   -> source list built in CODE from chunk metadata,
                       so attribution does not depend on the LLM
  Gradio UI         -> question box + grounded, cited answer

Run as a CLI (no gradio needed):   python app.py "is lincoln park worth it?"
Launch the web UI:                 python app.py --ui     (needs: pip install gradio)
"""

import os
import sys

from dotenv import load_dotenv
from groq import Groq

from retrieve import retrieve, TOP_K

load_dotenv()  # read GROQ_API_KEY from .env
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

GROQ_MODEL = "llama-3.3-70b-versatile"  # swap if Groq deprecates it

# Grounding is ENFORCED here, not suggested: the model is told to use only the
# passages, to refuse when they don't cover the question, and to ignore
# irrelevant ones (Anticipated Challenge #1).
SYSTEM_PROMPT = """You are the Unofficial Guide to off-campus housing for DePaul \
University students. You answer using ONLY the numbered context passages given \
to you in the user's message.

Follow these rules exactly:
1. Use ONLY information stated in the context passages. Never add facts from your \
own knowledge or general world knowledge.
2. If the passages do not contain enough information to answer the question, reply \
with exactly: "The documents I have don't cover this." Do not guess or fill gaps.
3. Some passages may be irrelevant to the question even though they were provided. \
Ignore those; do not let them pull your answer off topic.
4. After each claim, cite the passage number(s) you used in brackets, e.g. [2].
5. Be concise and reflect what students actually said, including disagreement when \
the passages disagree."""


def format_context(hits: list[dict]) -> str:
    """Number each retrieved chunk [1..k] and label it with its source."""
    blocks = []
    for i, h in enumerate(hits, 1):
        m = h["metadata"]
        loc = m.get("building") or m.get("neighborhood") or ""
        label = m.get("source", "?") + (f", {loc}" if loc else "")
        blocks.append(f"[{i}] ({label})\n{h['text']}")
    return "\n\n".join(blocks)


def build_sources(hits: list[dict]) -> str:
    """
    Build the source list FROM METADATA in code, deduplicated by document.

    This is the programmatic attribution guarantee: the cited sources come from
    the chunks that were actually retrieved, regardless of what the LLM writes.

    Each line leads with the passage number(s) that document supplied (matching
    the [n] markers in format_context), so the model's inline [n] citations
    resolve to a source even though the list is deduplicated by document.
    """
    groups = {}  # filename -> {"meta": metadata, "passages": [n, ...]}
    for n, h in enumerate(hits, 1):
        m = h["metadata"]
        fn = m.get("filename", "?")
        groups.setdefault(fn, {"meta": m, "passages": []})["passages"].append(n)

    lines = []
    for g in groups.values():
        m = g["meta"]
        loc = m.get("building") or m.get("neighborhood") or ""
        label = m.get("source", "?") + (f", {loc}" if loc else "")
        url = m.get("url") or ""
        passages = ", ".join(str(n) for n in g["passages"])
        lines.append(f"[{passages}] {label}" + (f" ({url})" if url else ""))
    return "\n".join(lines)


def generate_answer(query: str, k: int = TOP_K) -> tuple[str, str]:
    """Retrieve, ask Groq to answer grounded in the chunks, return (answer, sources)."""
    hits = retrieve(query, k)
    user_message = f"Context passages:\n{format_context(hits)}\n\nQuestion: {query}"
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,  # low: stay close to the source text, less invention
    )
    answer = response.choices[0].message.content.strip()
    return answer, build_sources(hits)


REFUSAL = "The documents I have don't cover this"


def handle_query(question: str) -> tuple[str, str]:
    """
    Return (answer, sources) for the two output boxes.

    On a grounded refusal, return an empty sources box — it would be misleading
    to list documents when none were actually used to answer.
    """
    if not question or not question.strip():
        return "Ask a question about DePaul off-campus housing.", ""
    answer, sources = generate_answer(question)
    if answer.strip().rstrip(".") == REFUSAL:
        return answer, ""
    return answer, sources


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] != "--ui":
        # CLI mode — works without gradio installed.
        answer, sources = handle_query(" ".join(args))
        print(answer)
        if sources:
            print("\nRetrieved from:\n" + sources)
    else:
        import gradio as gr

        with gr.Blocks(title="The Unofficial Guide") as demo:
            gr.Markdown(
                "# The Unofficial Guide — DePaul Off-Campus Housing\n"
                "Grounded answers from real student posts and reviews."
            )
            inp = gr.Textbox(
                label="Your question",
                placeholder="e.g. What neighborhoods are cheap and close to campus?",
                lines=2,
            )
            btn = gr.Button("Ask", variant="primary")
            answer = gr.Textbox(label="Answer", lines=8)
            sources = gr.Textbox(label="Retrieved from", lines=4)
            btn.click(handle_query, inputs=inp, outputs=[answer, sources])
            inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

        demo.launch()
